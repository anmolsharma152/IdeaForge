/**
 * IdeaForge Web Application JS — API client & UI Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initWorkflowSelect();
    initIdeationForm();
    initSliders();
    initVaultSearch();
    loadMetrics();
});

// NAVIGATION
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;

            navButtons.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');

            if (targetTab === 'tab-vault') {
                loadVaultIdeas();
            } else if (targetTab === 'tab-metrics') {
                loadMetrics();
            }
        });
    });
}

// SLIDERS
function initSliders() {
    const musesSlider = document.getElementById('muses-slider');
    const musesVal = document.getElementById('muses-val');
    const roundsSlider = document.getElementById('rounds-slider');
    const roundsVal = document.getElementById('rounds-val');

    musesSlider.addEventListener('input', (e) => musesVal.textContent = e.target.value);
    roundsSlider.addEventListener('input', (e) => roundsVal.textContent = e.target.value);
}

// WORKFLOW SELECT
async function initWorkflowSelect() {
    const selectEl = document.getElementById('workflow-select');
    const descEl = document.getElementById('workflow-desc');

    try {
        const res = await fetch('/api/workflows');
        const data = await res.json();

        selectEl.innerHTML = '';
        data.workflows.forEach((wf, index) => {
            const option = document.createElement('option');
            option.value = wf.key;
            option.textContent = wf.name;
            if (index === 0) option.selected = true;
            selectEl.appendChild(option);
        });

        const updateDesc = () => {
            const found = data.workflows.find(w => w.key === selectEl.value);
            if (found) descEl.textContent = found.description;
        };

        selectEl.addEventListener('change', updateDesc);
        updateDesc();
    } catch (err) {
        console.error('Failed to load workflows:', err);
    }
}

// IDEATION FORM & RUN API
function initIdeationForm() {
    const form = document.getElementById('ideation-form');
    const statusCard = document.getElementById('status-card');
    const statusText = document.getElementById('status-text');
    const synthesizedCard = document.getElementById('synthesized-card');
    const candidatesContainer = document.getElementById('candidates-container');
    const runBtn = document.getElementById('run-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const goal = document.getElementById('goal-input').value.trim();
        const workflow = document.getElementById('workflow-select').value;
        const muses = parseInt(document.getElementById('muses-slider').value, 10);
        const rounds = parseInt(document.getElementById('rounds-slider').value, 10);

        if (!goal) return;

        // UI Reset & Loading State
        runBtn.disabled = true;
        statusCard.classList.remove('hidden');
        statusText.textContent = 'Running intake, searching web context & executing dual-process muses...';
        synthesizedCard.classList.add('hidden');
        candidatesContainer.classList.add('hidden');

        try {
            const res = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal, workflow, muses, rounds }),
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Synthesis failed');
            }

            const data = await res.json();
            statusCard.classList.add('hidden');

            // Render Refined Idea
            if (data.refined) {
                document.getElementById('result-title').textContent = data.refined.title || 'Synthesized Idea';
                document.getElementById('result-body').textContent = data.refined.body || '';

                const tagsContainer = document.getElementById('result-tags');
                tagsContainer.innerHTML = '';
                (data.refined.tags || []).forEach(tag => {
                    const chip = document.createElement('span');
                    chip.className = 'tag-chip';
                    chip.textContent = tag;
                    tagsContainer.appendChild(chip);
                });

                document.getElementById('result-id').textContent = data.idea_ids ? `ID: ${data.idea_ids.join(', ')}` : '';
                document.getElementById('result-notes').textContent = data.eval_notes || '';
                synthesizedCard.classList.remove('hidden');
            }

            // Render Candidates
            if (data.candidates && data.candidates.length > 0) {
                renderCandidates(data.candidates, data.scores);
                candidatesContainer.classList.remove('hidden');
            }
        } catch (err) {
            statusText.textContent = `Error: ${err.message}`;
            console.error(err);
        } finally {
            runBtn.disabled = false;
        }
    });
}

function renderCandidates(candidates, scores) {
    const grid = document.getElementById('candidates-grid');
    grid.innerHTML = '';

    candidates.forEach((cand, idx) => {
        const score = (scores && scores[idx]) ? scores[idx] : {};
        const card = document.createElement('div');
        card.className = 'candidate-card';

        card.innerHTML = `
            <h4>${escapeHtml(cand.title)}</h4>
            <p style="font-size: 0.9rem; color: #cbd5e1; margin-top: 6px;">${escapeHtml(cand.body)}</p>
            <div class="candidate-scores">
                <span>Nov: <b>${score.novelty ? score.novelty.toFixed(2) : '-'}</b></span>
                <span>Coh: <b>${score.coherence ? score.coherence.toFixed(2) : '-'}</b></span>
                <span>Use: <b>${score.usefulness ? score.usefulness.toFixed(2) : '-'}</b></span>
                <span style="color: var(--accent-purple);">Overall: <b>${score.overall ? score.overall.toFixed(2) : '-'}</b></span>
            </div>
        `;
        grid.appendChild(card);
    });
}

// VAULT & SEARCH
function initVaultSearch() {
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');

    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            searchVaultIdeas(query);
        } else {
            loadVaultIdeas();
        }
    });

    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') searchBtn.click();
    });
}

async function loadVaultIdeas() {
    const grid = document.getElementById('vault-ideas-list');
    grid.innerHTML = '<div class="loading-placeholder">Loading vault memory...</div>';

    try {
        const res = await fetch('/api/ideas');
        const data = await res.json();
        renderVaultCards(data.ideas || []);
    } catch (err) {
        grid.innerHTML = `<div class="error-msg">Failed to load ideas: ${err.message}</div>`;
    }
}

async function searchVaultIdeas(query) {
    const grid = document.getElementById('vault-ideas-list');
    grid.innerHTML = '<div class="loading-placeholder">Running pgvector similarity search...</div>';

    try {
        const res = await fetch(`/api/ideas/search?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        const items = (data.results || []).map(r => ({ ...r.idea, similarity: r.similarity }));
        renderVaultCards(items);
    } catch (err) {
        grid.innerHTML = `<div class="error-msg">Search failed: ${err.message}</div>`;
    }
}

function renderVaultCards(ideas) {
    const grid = document.getElementById('vault-ideas-list');
    grid.innerHTML = '';

    if (ideas.length === 0) {
        grid.innerHTML = '<div class="loading-placeholder">No stored ideas found. Run an ideation session first!</div>';
        return;
    }

    ideas.forEach(idea => {
        const card = document.createElement('div');
        card.className = 'glass-card';

        const simBadge = idea.similarity ? `<span class="tag-chip" style="color:var(--accent-green)">Similarity: ${(idea.similarity * 100).toFixed(1)}%</span>` : '';
        const tags = (idea.tags || []).map(t => `<span class="tag-chip">${escapeHtml(t)}</span>`).join(' ');

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <h3 style="font-size: 1.1rem;">${escapeHtml(idea.title)}</h3>
                ${simBadge}
            </div>
            <p class="idea-body" style="font-size: 0.95rem;">${escapeHtml(idea.body)}</p>
            <div class="tags-container">${tags}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 12px;">Workflow: <b>${escapeHtml(idea.workflow)}</b> | ID: <code>${idea.id}</code></div>
        `;
        grid.appendChild(card);
    });
}

// METRICS
async function loadMetrics() {
    try {
        const res = await fetch('/api/metrics');
        const data = await res.json();

        document.getElementById('metric-sessions').textContent = data.total_sessions || 0;
        document.getElementById('metric-ideas').textContent = data.total_ideas || 0;
        document.getElementById('metric-novelty').textContent = data.avg_novelty ? data.avg_novelty.toFixed(2) : '0.00';

        renderWorkflowChart(data.workflow_counts || {});
    } catch (err) {
        console.error('Failed to load metrics:', err);
    }
}

function renderWorkflowChart(counts) {
    const container = document.getElementById('workflow-chart');
    container.innerHTML = '';

    const entries = Object.entries(counts);
    if (entries.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">No workflow sessions recorded yet.</p>';
        return;
    }

    const maxVal = Math.max(...Object.values(counts), 1);
    entries.forEach(([wf, val]) => {
        const row = document.createElement('div');
        row.style.margin = '12px 0';

        const pct = Math.round((val / maxVal) * 100);
        row.innerHTML = `
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                <span><b>${escapeHtml(wf)}</b></span>
                <span>${val} ideas</span>
            </div>
            <div style="background: rgba(15, 23, 42, 0.8); height: 10px; border-radius: 999px; overflow: hidden; border: 1px solid var(--border-color);">
                <div style="background: var(--gradient-primary); height: 100%; width: ${pct}%; transition: width 0.5s ease;"></div>
            </div>
        `;
        container.appendChild(row);
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
