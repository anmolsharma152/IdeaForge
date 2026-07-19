"""CLI entry point for IdeaForge."""

import asyncio

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(package_name="ideaforge")
def main():
    """IdeaForge — structured creativity with memory that compounds."""


@main.command()
@click.option("--workflow", "-w", required=True, help="Workflow template to run (research, product, learning)")
@click.option("--goal", "-g", required=True, help="Creative goal or prompt")
@click.option("--provider", "-p", default=None, help="LLM provider override (groq, openai)")
@click.option("--model", "-m", default=None, help="LLM model override")
@click.option("--muses", type=int, default=5, help="Number of muse candidates per round")
@click.option("--rounds", type=int, default=3, help="Max evaluation rounds")
def run(workflow: str, goal: str, provider: str | None, model: str | None, muses: int, rounds: int):
    """Run a creative synthesis workflow."""
    import ideaforge.workflows  # noqa: F401 — triggers registration
    from ideaforge.db.schema import ensure_schema
    from ideaforge.graph.build import build_graph
    from ideaforge.memory.store import create_session
    from ideaforge.workflows.base import get_workflow, list_workflows

    wf = get_workflow(workflow)
    if not wf:
        console.print(f"[red]Unknown workflow: {workflow}[/red]")
        console.print(f"Available: {', '.join(list_workflows())}")
        return

    ensure_schema()

    graph = build_graph()
    initial_state = {
        "goal": goal,
        "workflow": workflow,
        "muse_count": muses,
        "max_iterations": rounds,
    }

    console.print(f"\n[bold cyan]IdeaForge[/bold cyan] — {wf.name}")
    console.print(f"[dim]{wf.description}[/dim]\n")

    async def _run():
        state = await graph.ainvoke(initial_state)
        import uuid as _uuid
        idea_ids = [_uuid.UUID(i) for i in state.get("idea_ids", [])]
        await create_session(workflow=workflow, goal=goal, idea_ids=idea_ids)
        return state

    final_state = asyncio.run(_run())

    # Display results
    if final_state.get("refined"):
        refined = final_state["refined"]
        console.print("\n[bold green]═══ Synthesized Idea ═══[/bold green]")
        console.print(f"[bold]{refined['title']}[/bold]")
        console.print(refined["body"])
        if refined.get("tags"):
            console.print(f"[dim]Tags: {', '.join(refined['tags'])}[/dim]")

    if final_state.get("idea_ids"):
        console.print(f"\n[dim]Stored as: {', '.join(final_state['idea_ids'])}[/dim]")

    if final_state.get("eval_notes"):
        console.print(f"[dim]{final_state['eval_notes']}[/dim]")

    # Show all candidates
    candidates = final_state.get("candidates", [])
    scores = final_state.get("scores", [])
    if candidates:
        console.print("\n[bold]═══ All Candidates ═══[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("#")
        table.add_column("Title")
        table.add_column("Novelty")
        table.add_column("Coherence")
        table.add_column("Useful")
        table.add_column("Overall")
        for i, c in enumerate(candidates):
            s = scores[i] if i < len(scores) else {}
            table.add_row(
                str(i + 1),
                c["title"],
                f"{s.get('novelty', 0):.2f}" if s else "-",
                f"{s.get('coherence', 0):.2f}" if s else "-",
                f"{s.get('usefulness', 0):.2f}" if s else "-",
                f"{s.get('overall', 0):.2f}" if s else "-",
            )
        console.print(table)


@main.command("list")
@click.option("--workflow", "-w", default=None, help="Filter by workflow")
@click.option("--limit", "-l", type=int, default=20, help="Max ideas to show")
def list_ideas(workflow: str | None, limit: int):
    """List stored ideas."""
    from ideaforge.db.schema import ensure_schema
    from ideaforge.memory.store import list_ideas as _list_ideas

    ensure_schema()
    ideas = asyncio.run(
        _list_ideas(workflow=workflow, limit=limit)
    )

    if not ideas:
        console.print("[dim]No ideas stored yet.[/dim]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Workflow")
    table.add_column("Tags")
    for idea in ideas:
        table.add_row(
            str(idea.id)[:8],
            idea.title,
            idea.workflow,
            ", ".join(idea.tags),
        )
    console.print(table)


@main.command()
@click.argument("idea_id")
def show(idea_id: str):
    """Show a specific idea by ID."""
    from ideaforge.db.schema import ensure_schema
    from ideaforge.memory.store import get_connections, get_idea

    ensure_schema()
    import uuid

    async def _show():
        idea = await get_idea(uuid.UUID(idea_id))
        if not idea:
            return None, []
        conns = await get_connections(idea.id)
        return idea, conns

    idea, connections = asyncio.run(_show())
    if not idea:
        console.print(f"[red]Idea not found: {idea_id}[/red]")
        return

    console.print(f"\n[bold]{idea.title}[/bold]")
    console.print(idea.body)
    console.print(
        f"\n[dim]Workflow: {idea.workflow} | Tags: {', '.join(idea.tags)}[/dim]"
    )
    if idea.scores:
        console.print(f"[dim]Scores: {idea.scores}[/dim]")

    if connections:
        console.print("\n[bold]═══ Connections ═══[/bold]")
        for c in connections:
            direction = "→" if c["from_id"] == idea.id else "←"
            console.print(
                f"  {direction} [{c['relation']}] {c['linked_title']} "
                f"[dim]({c['linked_workflow']})[/dim]"
            )


@main.command()
@click.argument("idea_id")
@click.option("--threshold", "-t", type=float, default=0.5, help="Similarity threshold")
def connect(idea_id: str, threshold: float):
    """Auto-connect an idea to similar existing ideas."""
    from ideaforge.db.schema import ensure_schema
    from ideaforge.memory.store import auto_connect

    ensure_schema()
    import uuid

    connections = asyncio.run(
        auto_connect(uuid.UUID(idea_id), similarity_threshold=threshold)
    )
    if not connections:
        console.print("[dim]No similar ideas found above threshold.[/dim]")
        return

    console.print(f"[green]Created {len(connections)} connections:[/green]")
    for c in connections:
        console.print(f"  → [{c.relation}] {c.to_id}")


@main.command()
@click.argument("query")
@click.option("--limit", "-l", type=int, default=5, help="Number of results")
def search(query: str, limit: int):
    """Search ideas by semantic similarity."""
    from ideaforge.db.schema import ensure_schema
    from ideaforge.memory.store import search_similar

    ensure_schema()
    results = asyncio.run(
        search_similar(query, limit=limit)
    )

    if not results:
        console.print("[dim]No similar ideas found.[/dim]")
        return

    for r in results:
        console.print(
            f"\n[bold]{r.idea.title}[/bold] "
            f"[dim](similarity: {r.similarity:.3f})[/dim]"
        )
        console.print(r.idea.body[:200])


@main.command("sessions")
@click.option("--workflow", "-w", default=None, help="Filter by workflow")
@click.option("--limit", "-l", type=int, default=20, help="Max sessions to show")
def list_sessions(workflow: str | None, limit: int):
    """List recent workflow sessions."""
    from ideaforge.db.schema import ensure_schema
    from ideaforge.memory.store import list_sessions as _list_sessions

    ensure_schema()
    sessions = asyncio.run(_list_sessions(workflow=workflow, limit=limit))

    if not sessions:
        console.print("[dim]No sessions yet.[/dim]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Workflow")
    table.add_column("Goal")
    table.add_column("Ideas")
    for s in sessions:
        table.add_row(
            str(s.id)[:8],
            s.workflow,
            s.goal[:60] + ("..." if len(s.goal) > 60 else ""),
            str(len(s.idea_ids)),
        )
    console.print(table)


@main.command()
@click.option("--workflow", "-w", default=None, help="Filter by workflow")
def metrics(workflow: str | None):
    """Show aggregate metrics across all stored ideas."""
    from ideaforge.db.schema import ensure_schema
    from ideaforge.db.engine import get_async_engine
    from sqlalchemy import text

    ensure_schema()

    async def _metrics():
        engine = get_async_engine()
        async with engine.connect() as conn:
            # Idea counts
            if workflow:
                result = await conn.execute(
                    text(
                        "SELECT COUNT(*), workflow FROM ideas "
                        "WHERE workflow = :wf GROUP BY workflow"
                    ),
                    {"wf": workflow},
                )
            else:
                result = await conn.execute(
                    text("SELECT COUNT(*), workflow FROM ideas GROUP BY workflow")
                )
            rows = result.fetchall()
            total_ideas = sum(r[0] for r in rows)
            by_workflow = {r[1]: r[0] for r in rows}

            # Score averages
            result = await conn.execute(
                text(
                    "SELECT "
                    "AVG((scores->>'novelty')::float), "
                    "AVG((scores->>'coherence')::float), "
                    "AVG((scores->>'usefulness')::float), "
                    "AVG((scores->>'overall')::float) "
                    "FROM ideas WHERE scores != '{}'::jsonb"
                )
            )
            avgs = result.fetchone()

            # Connection count
            result = await conn.execute(text("SELECT COUNT(*) FROM connections"))
            total_connections = result.scalar() or 0

            # Session count
            result = await conn.execute(text("SELECT COUNT(*) FROM sessions"))
            total_sessions = result.scalar() or 0

            return {
                "total_ideas": total_ideas,
                "by_workflow": by_workflow,
                "avg_scores": {
                    "novelty": round(avgs[0] or 0, 3),
                    "coherence": round(avgs[1] or 0, 3),
                    "usefulness": round(avgs[2] or 0, 3),
                    "overall": round(avgs[3] or 0, 3),
                },
                "total_connections": total_connections,
                "total_sessions": total_sessions,
            }

    stats = asyncio.run(_metrics())

    console.print("\n[bold cyan]IdeaForge Metrics[/bold cyan]")
    console.print(f"  Ideas: {stats['total_ideas']}  |  Sessions: {stats['total_sessions']}  |  Connections: {stats['total_connections']}")

    if stats["by_workflow"]:
        console.print("\n[bold]By Workflow:[/bold]")
        for wf, count in stats["by_workflow"].items():
            console.print(f"  {wf}: {count}")

    avgs = stats["avg_scores"]
    if avgs["overall"] > 0:
        console.print("\n[bold]Average Scores:[/bold]")
        console.print(f"  Novelty:    {avgs['novelty']:.3f}")
        console.print(f"  Coherence:  {avgs['coherence']:.3f}")
        console.print(f"  Usefulness: {avgs['usefulness']:.3f}")
        console.print(f"  Overall:    {avgs['overall']:.3f}")


if __name__ == "__main__":
    main()
