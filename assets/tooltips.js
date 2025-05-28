// Enhanced tooltip and modal functionality
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // Enhanced modal animations
        enhance_modal_animations: function(is_open) {
            if (is_open) {
                // Add custom animation classes when modal opens
                setTimeout(() => {
                    const modalContent = document.querySelector('.modal-content');
                    if (modalContent) {
                        modalContent.style.animation = 'slideUp 0.3s ease-out';
                    }
                    
                    const modalBody = document.querySelector('.modal-body');
                    if (modalBody) {
                        modalBody.style.animation = 'fadeIn 0.4s ease-out 0.1s both';
                    }
                }, 50);
            }
            return window.dash_clientside.no_update;
        },
        
        // Download functionality for PNG
        download_chart_as_png: function(n_clicks) {
            if (n_clicks && n_clicks > 0) {
                const graphDiv = document.querySelector('.modal .js-plotly-plot');
                if (graphDiv) {
                    Plotly.downloadImage(graphDiv, {
                        format: 'png',
                        width: 800,
                        height: 600,
                        filename: 'chart_data'
                    });
                }
            }
            return window.dash_clientside.no_update;
        }
    }
});

// Initialize tooltips when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Close modal on Escape key
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal.show');
            if (modal) {
                const closeBtn = modal.querySelector('#close-modal');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
        }
    });
});

// Smooth scroll to top when modal opens
function scrollToModalTop() {
    const modal = document.querySelector('.modal-body');
    if (modal) {
        modal.scrollTop = 0;
    }
} 