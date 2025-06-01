// Enhanced Click Handling for Heatmap
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    heatmap_enhancements: {
        // Enhanced click handler with visual feedback
        handle_click_with_feedback: function(clickData, last_click_time) {
            if (clickData) {
                const currentTime = Date.now();
                
                // Debouncing: ignore clicks that are too close together
                if (currentTime - last_click_time < 300) {
                    return window.dash_clientside.no_update;
                }
                
                // Add visual feedback immediately
                addClickFeedback();
                
                // Add success indicator
                showSuccessIndicator();
                
                return currentTime;
            }
            return window.dash_clientside.no_update;
        },
        
        // Show loading state while modal is opening
        show_modal_loading: function(is_open) {
            if (is_open) {
                // Add loading class to modal if it exists
                setTimeout(() => {
                    const modal = document.querySelector('.modal');
                    if (modal) {
                        modal.classList.add('modal-loading');
                    }
                }, 50);
                
                // Remove loading class after content loads
                setTimeout(() => {
                    const modal = document.querySelector('.modal');
                    if (modal) {
                        modal.classList.remove('modal-loading');
                    }
                }, 500);
            }
            return window.dash_clientside.no_update;
        }
    }
});

// Helper function to add click feedback
function addClickFeedback() {
    const heatmapContainer = document.querySelector('#heatmap').closest('.card-body');
    if (heatmapContainer) {
        // Add click effect class
        heatmapContainer.classList.add('click-effect');
        
        // Remove after animation
        setTimeout(() => {
            heatmapContainer.classList.remove('click-effect');
        }, 600);
    }
    
    // Show feedback overlay
    showClickFeedbackOverlay();
    
    // Add subtle haptic feedback if supported
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
}

// Show click feedback overlay
function showClickFeedbackOverlay() {
    // Remove existing overlay if present
    const existingOverlay = document.querySelector('.click-feedback-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    // Create new overlay
    const overlay = document.createElement('div');
    overlay.className = 'click-feedback-overlay';
    overlay.textContent = '✓ פותח...';
    
    document.body.appendChild(overlay);
    
    // Show with animation
    setTimeout(() => {
        overlay.classList.add('show');
    }, 10);
    
    // Remove after animation
    setTimeout(() => {
        overlay.remove();
    }, 1500);
}

// Show success indicator
function showSuccessIndicator() {
    const heatmapCard = document.querySelector('#heatmap').closest('.card');
    if (heatmapCard) {
        // Remove existing indicator
        const existingIndicator = heatmapCard.querySelector('.click-success-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        // Create new indicator
        const indicator = document.createElement('div');
        indicator.className = 'click-success-indicator';
        indicator.innerHTML = '<i class="fas fa-check"></i> נלחץ בהצלחה';
        
        heatmapCard.style.position = 'relative';
        heatmapCard.appendChild(indicator);
        
        // Show with animation
        setTimeout(() => {
            indicator.classList.add('show');
        }, 10);
        
        // Remove after animation
        setTimeout(() => {
            indicator.remove();
        }, 2000);
    }
}

// Enhanced hover effects for heatmap cells
function enhanceHoverEffects() {
    const heatmapDiv = document.querySelector('#heatmap');
    if (heatmapDiv) {
        // Add mouse enter/leave events for better feedback
        heatmapDiv.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
            this.style.filter = 'brightness(1.05)';
        });
        
        heatmapDiv.addEventListener('mouseleave', function() {
            this.style.filter = 'brightness(1)';
        });
        
        // Add click event listener for immediate feedback
        heatmapDiv.addEventListener('click', function(e) {
            // Immediate visual feedback
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.1s ease';
            
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    }
}

// Keyboard navigation support
function addKeyboardSupport() {
    document.addEventListener('keydown', function(e) {
        // Close modal on Escape
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal.show');
            if (modal) {
                const closeBtn = modal.querySelector('#close-modal');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
        }
        
        // Add keyboard navigation for heatmap
        if (e.key === 'Enter' || e.key === ' ') {
            const focusedElement = document.activeElement;
            if (focusedElement && focusedElement.id === 'heatmap') {
                e.preventDefault();
                // Simulate click on center of heatmap
                focusedElement.click();
            }
        }
    });
}

// Optimize click detection for mobile devices
function optimizeMobileClicks() {
    const heatmapDiv = document.querySelector('#heatmap');
    if (heatmapDiv) {
        // Prevent double-tap zoom on mobile
        heatmapDiv.style.touchAction = 'manipulation';
        
        // Add touch event handlers for better mobile experience
        heatmapDiv.addEventListener('touchstart', function(e) {
            this.style.opacity = '0.9';
        }, { passive: true });
        
        heatmapDiv.addEventListener('touchend', function(e) {
            this.style.opacity = '1';
            addClickFeedback();
        }, { passive: true });
    }
}

// Monitor for failed clicks and provide feedback
let clickAttempts = 0;
let lastClickTime = 0;

function monitorClickReliability() {
    const heatmapDiv = document.querySelector('#heatmap');
    if (heatmapDiv) {
        heatmapDiv.addEventListener('click', function() {
            const currentTime = Date.now();
            clickAttempts++;
            
            // If multiple clicks in short succession, show helper message
            if (currentTime - lastClickTime < 1000 && clickAttempts > 2) {
                showClickHelper();
                clickAttempts = 0;
            }
            
            lastClickTime = currentTime;
            
            // Reset counter after delay
            setTimeout(() => {
                clickAttempts = 0;
            }, 2000);
        });
    }
}

// Show helper message for users having trouble clicking
function showClickHelper() {
    const existingHelper = document.querySelector('.click-helper');
    if (existingHelper) return;
    
    const helper = document.createElement('div');
    helper.className = 'click-helper';
    helper.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ffc107;
        color: #000;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease;
        direction: rtl;
        text-align: right;
    `;
    helper.innerHTML = '💡 טיפ: לחצו על התא פעם אחת והמתינו לפתיחת החלונית';
    
    document.body.appendChild(helper);
    
    // Remove after 5 seconds
    setTimeout(() => {
        helper.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => helper.remove(), 300);
    }, 5000);
}

// Add CSS for helper animations
function addHelperStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize all enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add helper styles
    addHelperStyles();
    
    // Initialize enhancements with delay to ensure Plotly is loaded
    setTimeout(() => {
        enhanceHoverEffects();
        addKeyboardSupport();
        optimizeMobileClicks();
        monitorClickReliability();
    }, 1000);
    
    // Re-initialize when new content is loaded (for dynamic updates)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Re-run enhancements if heatmap is updated
                setTimeout(() => {
                    enhanceHoverEffects();
                    optimizeMobileClicks();
                }, 100);
            }
        });
    });
    
    // Observe the main container for changes
    const container = document.querySelector('.container-fluid');
    if (container) {
        observer.observe(container, {
            childList: true,
            subtree: true
        });
    }
});

// Preload common assets for better performance
function preloadAssets() {
    // Preload Font Awesome icons
    const iconLink = document.createElement('link');
    iconLink.rel = 'preload';
    iconLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
    iconLink.as = 'style';
    document.head.appendChild(iconLink);
}

// Call preload on script load
preloadAssets(); 