/*
 * Batch Experiments Page JavaScript
 * Handles running batch experiments and displaying results
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Experiments page loaded');
    
    // Load defense strategies
    loadDefenseStrategies();
    
    // Load previous experiments
    loadPreviousExperiments();
    
    // Setup form submission
    const form = document.getElementById('experiment-form');
    if (form) {
        form.addEventListener('submit', handleExperimentSubmit);
    }
    
    // Setup quick template buttons
    document.querySelectorAll('.load-template').forEach(button => {
        button.addEventListener('click', function() {
            const prompts = this.getAttribute('data-prompts');
            const defenses = JSON.parse(this.getAttribute('data-defenses'));
            loadTemplate(prompts, defenses);
        });
    });
    
    // Setup manipulation type "All" checkbox
    const manipAll = document.getElementById('manip-all');
    if (manipAll) {
        manipAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.manip-type');
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
            });
        });
    }
    
    // Update prompt count display
    const promptSlider = document.getElementById('num-prompts');
    if (promptSlider) {
        promptSlider.addEventListener('input', function() {
            document.getElementById('prompt-count').textContent = this.value + ' prompts';
        });
    }
});

/**
 * Load defense strategies as checkboxes
 */
function loadDefenseStrategies() {
    fetch('/api/defense/strategies')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const container = document.getElementById('defense-checkboxes');
                if (container) {
                    container.innerHTML = '';
                    
                    data.strategies.forEach(strategy => {
                        const div = document.createElement('div');
                        div.className = 'form-check';
                        
                        const checkbox = document.createElement('input');
                        checkbox.className = 'form-check-input defense-checkbox';
                        checkbox.type = 'checkbox';
                        checkbox.value = strategy.id;
                        checkbox.id = `defense-${strategy.id}`;
                        
                        // Check some by default
                        if (['no_defense', 'medium_hardening', 'aggressive_hardening'].includes(strategy.id)) {
                            checkbox.checked = true;
                        }
                        
                        const label = document.createElement('label');
                        label.className = 'form-check-label';
                        label.htmlFor = `defense-${strategy.id}`;
                        label.textContent = strategy.name;
                        
                        div.appendChild(checkbox);
                        div.appendChild(label);
                        container.appendChild(div);
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error loading defense strategies:', error);
            showNotification('Failed to load defense strategies', 'danger');
        });
}

/**
 * Load previous experiments
 */
function loadPreviousExperiments() {
    fetch('/api/results/list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const container = document.getElementById('previous-experiments');
                if (container) {
                    container.innerHTML = '';
                    
                    if (data.experiments.length === 0) {
                        container.innerHTML = `
                            <div class="list-group-item text-center text-muted">
                                No previous experiments found.
                            </div>
                        `;
                        return;
                    }
                    
                    data.experiments.forEach(exp => {
                        const date = new Date(exp.timestamp).toLocaleString();
                        const item = document.createElement('a');
                        item.href = '#';
                        item.className = 'list-group-item list-group-item-action';
                        item.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">Experiment ${exp.id.substring(0, 8)}</h6>
                                <small>${date}</small>
                            </div>
                            <p class="mb-1">${exp.num_prompts} prompts, ${exp.defense_strategies.length} defenses</p>
                        `;
                        
                        item.addEventListener('click', function(e) {
                            e.preventDefault();
                            loadExperimentResults(exp.id);
                        });
                        
                        container.appendChild(item);
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error loading previous experiments:', error);
        });
}

/**
 * Load a quick experiment template
 */
function loadTemplate(prompts, defenses) {
    // Set prompt slider
    const promptSlider = document.getElementById('num-prompts');
    if (promptSlider) {
        promptSlider.value = prompts;
        document.getElementById('prompt-count').textContent = prompts + ' prompts';
    }
    
    // Set defense checkboxes
    const checkboxes = document.querySelectorAll('.defense-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = defenses.includes(cb.value);
    });
    
    showNotification('Template loaded successfully', 'success');
}

/**
 * Handle experiment form submission
 */
function handleExperimentSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const numPrompts = document.getElementById('num-prompts').value;
    const experimentName = document.getElementById('experiment-name').value;
    
    // Get selected defense strategies
    const defenseCheckboxes = document.querySelectorAll('.defense-checkbox:checked');
    const defenseStrategies = Array.from(defenseCheckboxes).map(cb => cb.value);
    
    if (defenseStrategies.length === 0) {
        showNotification('Please select at least one defense strategy', 'warning');
        return;
    }
    
    // Get selected manipulation types
    const manipCheckboxes = document.querySelectorAll('.manip-type:checked');
    const manipulationTypes = Array.from(manipCheckboxes).map(cb => cb.value);
    
    if (manipulationTypes.length === 0) {
        showNotification('Please select at least one manipulation type', 'warning');
        return;
    }
    
    // Disable submit button
    const submitBtn = document.getElementById('run-experiment-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running Experiment...';
    }
    
    // Show progress section
    const progressSection = document.getElementById('progress-section');
    if (progressSection) {
        progressSection.classList.remove('d-none');
    }
    
    // Update status
    const status = document.getElementById('experiment-status');
    if (status) {
        status.textContent = 'Running';
        status.className = 'badge bg-warning';
    }
    
    // Prepare request data
    const requestData = {
        num_prompts: parseInt(numPrompts),
        defense_strategies: defenseStrategies,
        manipulation_types: manipulationTypes,
        experiment_name: experimentName || undefined
    };
    
    // Start progress animation
    let progress = 0;
    const progressBar = document.getElementById('experiment-progress');
    const progressText = document.getElementById('progress-text');
    
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += 5;
            if (progressBar) progressBar.style.width = progress + '%';
            if (progressText) progressText.textContent = `Running... ${progress}%`;
        }
    }, 500);
    
    // Send experiment request
    fetch('/api/experiment/batch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        
        // Complete progress bar
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.classList.remove('progress-bar-animated');
        }
        
        if (progressText) {
            progressText.textContent = 'Complete!';
        }
        
        // Re-enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-play"></i> Run Experiment';
        }
        
        // Update status
        if (status) {
            status.textContent = 'Complete';
            status.className = 'badge bg-success';
        }
        
        if (data.success) {
            showNotification('Experiment completed successfully!', 'success');
            displayExperimentResults(data);
            
            // Reload previous experiments list
            loadPreviousExperiments();
        } else {
            showNotification('Experiment failed: ' + (data.error || 'Unknown error'), 'danger');
            displayExperimentError();
        }
    })
    .catch(error => {
        clearInterval(progressInterval);
        console.error('Error running experiment:', error);
        
        // Re-enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-play"></i> Run Experiment';
        }
        
        // Update status
        if (status) {
            status.textContent = 'Error';
            status.className = 'badge bg-danger';
        }
        
        showNotification('Network error. Please try again.', 'danger');
        displayExperimentError();
    });
}

/**
 * Display experiment results
 */
function displayExperimentResults(data) {
    const container = document.getElementById('results-content');
    if (!container) return;
    
    const stats = data.statistics;
    
    container.innerHTML = `
        <div class="fade-in">
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> Experiment Complete</h5>
                <p class="mb-0">Experiment ID: <strong>${data.experiment_id}</strong></p>
                <p class="mb-0">Results saved to: <code>${data.results_file}</code></p>
            </div>
            
            <h5 class="mt-4">Summary Statistics</h5>
            <div class="row">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h1 class="display-6">${stats.total_experiments}</h1>
                            <p class="card-text">Total Tests</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h1 class="display-6">${(stats.overall_safety_score * 100).toFixed(1)}%</h1>
                            <p class="card-text">Overall Safety</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h1 class="display-6">${Object.keys(stats.by_defense).length}</h1>
                            <p class="card-text">Defenses Tested</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h1 class="display-6">${Object.keys(stats.by_manipulation).length}</h1>
                            <p class="card-text">Manipulation Types</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <h5 class="mt-4">Safety Scores by Defense Strategy</h5>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Defense Strategy</th>
                            <th>Safety Score</th>
                            <th>Attack Success Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(stats.by_defense).map(([defense, score]) => `
                            <tr>
                                <td>${defense}</td>
                                <td>${(score * 100).toFixed(1)}%</td>
                                <td>${((1 - score) * 100).toFixed(1)}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="mt-4">
                <button class="btn btn-outline-primary" onclick="loadExperimentResults('${data.experiment_id}')">
                    <i class="fas fa-chart-bar"></i> View Detailed Results
                </button>
                <button class="btn btn-outline-secondary" onclick="location.reload()">
                    <i class="fas fa-redo"></i> Run New Experiment
                </button>
            </div>
        </div>
    `;
}

/**
 * Load and display detailed results for a specific experiment
 */
function loadExperimentResults(experimentId) {
    // Redirect to results page with the experiment ID
    window.location.href = `/results?experiment=${experimentId}`;
}

/**
 * Display experiment error
 */
function displayExperimentError() {
    const container = document.getElementById('results-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="text-center text-danger py-5">
            <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
            <h5>Experiment Failed</h5>
            <p>There was an error running the experiment. Please try again.</p>
            <button class="btn btn-outline-danger" onclick="location.reload()">
                <i class="fas fa-redo"></i> Reload Page
            </button>
        </div>
    `;
}