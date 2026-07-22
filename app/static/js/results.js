/*
 * Experiment results page JavaScript
 * Loads saved batch results and renders charts and detail rows.
 */

let experiments = [];
let selectedExperiment = null;
let charts = [];

document.addEventListener('DOMContentLoaded', function() {
    loadExperiments();

    const loadButton = document.getElementById('load-results');
    if (loadButton) {
        loadButton.addEventListener('click', function() {
            const experimentId = document.getElementById('experiment-select').value;
            if (experimentId) {
                loadExperiment(experimentId);
            }
        });
    }
});

function loadExperiments() {
    fetch('/api/results/list')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Unable to list experiments (${response.status})`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || 'Unable to list experiments');
            }

            experiments = data.experiments || [];
            populateExperimentSelect(experiments);

            const requestedId = new URLSearchParams(window.location.search).get('experiment');
            const experiment = experiments.find(item => item.id === requestedId) || experiments[0];
            if (experiment) {
                const select = document.getElementById('experiment-select');
                select.value = experiment.id;
                showExperimentInfo(experiment);
                loadExperiment(experiment.id);
            }
        })
        .catch(error => {
            console.error('Error loading experiments:', error);
            setSelectMessage('Unable to load experiments');
            showResultsError(error.message);
        });
}

function populateExperimentSelect(items) {
    const select = document.getElementById('experiment-select');
    if (!select) return;

    select.innerHTML = '';
    if (items.length === 0) {
        setSelectMessage('No experiments found');
        return;
    }

    items.forEach(experiment => {
        const option = document.createElement('option');
        option.value = experiment.id;
        option.textContent = `Experiment ${experiment.id} - ${formatDate(experiment.timestamp)}`;
        select.appendChild(option);
    });

    select.addEventListener('change', function() {
        const experiment = experiments.find(item => item.id === this.value);
        if (experiment) {
            showExperimentInfo(experiment);
            clearResults();
        }
    });
}

function setSelectMessage(message) {
    const select = document.getElementById('experiment-select');
    if (select) {
        select.innerHTML = `<option value="">${message}</option>`;
    }
}

function showExperimentInfo(experiment) {
    document.getElementById('info-id').textContent = experiment.id;
    document.getElementById('info-date').textContent = formatDate(experiment.timestamp);
    document.getElementById('info-prompts').textContent = experiment.num_prompts;
    document.getElementById('info-defenses').textContent = experiment.defense_strategies.join(', ');
    document.getElementById('experiment-info').classList.remove('d-none');
}

function loadExperiment(experimentId) {
    clearResults();
    fetch(`/api/results/${encodeURIComponent(experimentId)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Unable to load experiment (${response.status})`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.success || !data.experiment) {
                throw new Error(data.error || 'Experiment data is unavailable');
            }
            selectedExperiment = data.experiment;
            renderResults(selectedExperiment);
        })
        .catch(error => {
            console.error('Error loading experiment:', error);
            showResultsError(error.message);
        });
}

function renderResults(experiment) {
    const statistics = experiment.statistics || calculateStatistics(experiment.results || []);
    renderCharts(statistics);
    renderTable(experiment.results || []);
}

function renderCharts(statistics) {
    const container = document.getElementById('charts-container');
    if (!container || typeof Chart === 'undefined') {
        if (typeof Chart === 'undefined') {
            showResultsError('Chart library is unavailable');
        }
        return;
    }

    charts.forEach(chart => chart.destroy());
    charts = [];
    container.innerHTML = document.getElementById('chart-template').innerHTML;

    const defenseEntries = Object.entries(statistics.by_defense || {});
    const manipulationEntries = Object.entries(statistics.by_manipulation || {});
    const scores = (selectedExperiment.results || []).map(result => result.safety_score);

    charts.push(new Chart(document.getElementById('chart-defense-asr'), {
        type: 'bar',
        data: {
            labels: defenseEntries.map(([name]) => name),
            datasets: [{ label: 'Attack Success Rate', data: defenseEntries.map(([, score]) => 1 - score), backgroundColor: '#dc3545' }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 1 } } }
    }));

    charts.push(new Chart(document.getElementById('chart-safety-dist'), {
        type: 'bar',
        data: { labels: scores.map((_, index) => `Test ${index + 1}`), datasets: [{ label: 'Safety Score', data: scores, backgroundColor: '#198754' }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 1 } } }
    }));

    charts.push(new Chart(document.getElementById('chart-manipulation'), {
        type: 'bar',
        data: { labels: manipulationEntries.map(([name]) => name), datasets: [{ label: 'Average Safety Score', data: manipulationEntries.map(([, score]) => score), backgroundColor: '#0d6efd' }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 1 } } }
    }));

    charts.push(new Chart(document.getElementById('chart-overall'), {
        type: 'doughnut',
        data: { labels: ['Safe', 'Attack Success'], datasets: [{ data: [statistics.overall_safety_score, 1 - statistics.overall_safety_score], backgroundColor: ['#198754', '#dc3545'] }] },
        options: { responsive: true, maintainAspectRatio: false }
    }));
}

function renderTable(results) {
    const body = document.getElementById('results-table-body');
    if (!body) return;

    body.innerHTML = results.map(result => `
        <tr>
            <td>${escapeHtml(result.experiment_id || '')}</td>
            <td>${escapeHtml(result.prompt || '')}</td>
            <td>${escapeHtml(result.defense_strategy || '')}</td>
            <td>${escapeHtml(result.manipulation_type || '')}</td>
            <td>${formatPercentage(result.safety_score)}</td>
            <td><span class="badge bg-${result.safety_score >= 0.5 ? 'success' : 'danger'}">${result.safety_score >= 0.5 ? 'Safe' : 'At Risk'}</span></td>
        </tr>
    `).join('');
}

function calculateStatistics(results) {
    const average = values => values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
    const groupedAverage = key => results.reduce((groups, result) => {
        (groups[result[key]] ||= []).push(result.safety_score);
        return groups;
    }, Object.create(null));
    const averages = groups => Object.fromEntries(Object.entries(groups).map(([key, values]) => [key, average(values)]));

    return {
        total_experiments: results.length,
        by_defense: averages(groupedAverage('defense_strategy')),
        by_manipulation: averages(groupedAverage('manipulation_type')),
        overall_safety_score: average(results.map(result => result.safety_score))
    };
}

function clearResults() {
    const container = document.getElementById('charts-container');
    if (container) {
        container.innerHTML = '<div class="text-center text-muted py-5"><p>Loading results...</p></div>';
    }
    const body = document.getElementById('results-table-body');
    if (body) body.innerHTML = '';
}

function showResultsError(message) {
    const container = document.getElementById('charts-container');
    if (container) {
        container.innerHTML = `<div class="alert alert-danger">${escapeHtml(message)}</div>`;
    }
}

function escapeHtml(value) {
    const element = document.createElement('div');
    element.textContent = value;
    return element.innerHTML;
}