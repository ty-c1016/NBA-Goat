// JavaScript for NBA GOAT Analyzer
// Enhances UI interactions: slider displays, form validation, simple loading states

document.addEventListener('DOMContentLoaded', function() {
    // Initialize slider value displays
    initializeSliders();

    // Add form validation
    const form = document.getElementById('preferencesForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // Add loading states for buttons
    addLoadingStates();
});

function initializeSliders() {
    const sliders = ['offensive', 'defensive', 'team_success', 'longevity', 'efficiency', 'peak_performance'];

    sliders.forEach(slider => {
        const input = document.getElementById(slider + '_weight');
        const display = document.getElementById(slider + '_value');

        if (input && display) {
            // Set initial value
            const value = Math.round(input.value * 100);
            display.textContent = value + '%';

            // Update on change
            input.addEventListener('input', function() {
                const value = Math.round(this.value * 100);
                display.textContent = value + '%';

                // Add visual feedback
                display.classList.remove('bg-primary', 'bg-success', 'bg-warning');
                if (value < 30) {
                    display.classList.add('bg-warning');
                } else if (value > 70) {
                    display.classList.add('bg-success');
                } else {
                    display.classList.add('bg-primary');
                }
            });
        }
    });
}

function handleFormSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    if (submitButton) {
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Calculating...';
        submitButton.disabled = true;
    }

    // No additional validation needed - questions.html already validates that total = 100%
    // and the form will handle percentage to decimal conversion
}

function addLoadingStates() {
    // Add loading states to navigation links
    const navLinks = document.querySelectorAll('a[href]');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (this.href && !this.href.includes('#')) {
                this.classList.add('loading');
            }
        });
    });
}

// Utility function to format numbers
function formatNumber(num, decimals = 1) {
    if (num === null || num === undefined) return 'N/A';
    return parseFloat(num).toFixed(decimals);
}

// Function to highlight table rows on hover (enhanced)
function enhanceTableInteraction() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

// Initialize table enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', enhanceTableInteraction);