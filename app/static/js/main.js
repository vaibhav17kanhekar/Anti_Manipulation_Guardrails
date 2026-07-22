/*
 * Anti-Manipulation Guardrails - Main JavaScript
 * Handles common functionality across all pages
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Anti-Manipulation Guardrails Web Interface Loaded');
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize popovers
    initPopovers();
    
    // Set current year in footer
    setCurrentYear();
    
    // Initialize system status
    checkSystemStatus();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Set current year in footer
 */
function setCurrentYear() {
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    
    yearElements.forEach(element => {
        element.textContent = currentYear;
    });
}

/**
 * Check system status and update indicators
 */
function checkSystemStatus() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'healthy') {
                updateStatusIndicator('system-status', 'Operational', 'success');
                updateStatusIndicator('engine-status', 'Ready', 'success');
                updateStatusIndicator('storage-status', 'Ready', 'success');
                updateStatusIndicator('model-status', 'Simulated', 'info');
            } else {
                updateStatusIndicator('system-status', 'Degraded', 'warning');
            }
        })
        .catch(error => {
            console.error('Error checking system status:', error);
            updateStatusIndicator('system-status', 'Offline', 'danger');
            updateStatusIndicator('engine-status', 'Error', 'danger');
        });
}

/**
 * Update status indicator badge
 */
function updateStatusIndicator(elementId, text, type) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
        element.className = `badge bg-${type}`;
    }
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    
    bsToast.show();
    
    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format percentage
 */
function formatPercentage(value) {
    return (value * 100).toFixed(1) + '%';
}

/**
 * Debounce function for limiting API calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Create a loading spinner
 */
function createSpinner(size = 'md') {
    const sizeClass = size === 'lg' ? 'spinner-lg' : size === 'sm' ? 'spinner-sm' : '';
    const spinner = document.createElement('div');
    spinner.className = `spinner ${sizeClass}`;
    return spinner;
}

/**
 * Show loading overlay
 */
function showLoading(containerId, message = 'Loading...') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p class="mt-3">${message}</p>
        </div>
    `;
    
    container.style.position = 'relative';
    container.appendChild(overlay);
    
    return overlay;
}

/**
 * Hide loading overlay
 */
function hideLoading(overlay) {
    if (overlay && overlay.parentNode) {
        overlay.parentNode.removeChild(overlay);
    }
}

// Add loading overlay styles dynamically
const loadingStyles = document.createElement('style');
loadingStyles.textContent = `
    .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        border-radius: inherit;
    }
    
    .loading-content {
        text-align: center;
    }
    
    .spinner-lg {
        width: 60px;
        height: 60px;
    }
    
    .spinner-sm {
        width: 20px;
        height: 20px;
    }
`;

document.head.appendChild(loadingStyles);