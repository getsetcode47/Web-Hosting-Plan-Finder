// Range slider functions
function updateRangeValue(input, outputId, prefix = '', inputId = null) {
    const value = input.value;
    let displayValue = value;
    
    if (outputId === 'storageValue') {
        displayValue += ' GB';
    }
    
    document.getElementById(outputId).textContent = prefix + displayValue;
    
    // Also update the linked input field if it exists
    if (inputId) {
        document.getElementById(inputId).value = value;
    }
}

// Update slider from manual input
function updateSliderFromInput(input, sliderId) {
    const value = input.value;
    const slider = document.getElementById(sliderId);
    
    // Make sure value is within slider's min and max
    const min = parseInt(slider.min);
    const max = parseInt(slider.max);
    
    // Validate input
    if (value < min) {
        input.value = min;
        slider.value = min;
    } else if (value > max) {
        input.value = max;
        slider.value = max;
    } else {
        slider.value = value;
    }
    
    // Update display value
    let outputId = sliderId + 'Value';
    let prefix = '';
    
    if (sliderId === 'budget') {
        prefix = '₹';
    }
    
    let displayValue = input.value;
    if (sliderId === 'storage') {
        displayValue += ' GB';
    }
    
    document.getElementById(outputId).textContent = prefix + displayValue;
}

// Display results function (moved from inline)
function displayResults(data) {
    console.log("Displaying results:", data);
    
    const bestPlanContainer = document.getElementById('bestPlanContainer');
    const planCards = document.getElementById('planCards');
    const noResults = document.getElementById('noResults');
    
    // Clear previous results
    if (bestPlanContainer) bestPlanContainer.innerHTML = '';
    if (planCards) planCards.innerHTML = '';
    
    if (!data || data.count === 0) {
        console.log("No results to display");
        if (noResults) noResults.style.display = 'block';
        return;
    }
    
    console.log(`Displaying ${data.count} plans`);
    if (noResults) noResults.style.display = 'none';
    
    // Display best plan
    if (data.best_plan && bestPlanContainer) {
        console.log("Displaying best plan:", data.best_plan);
        const bestPlan = data.best_plan;
        const plan = bestPlan.plan;
        const savings = Math.round(((plan.regular_price - plan.price) / plan.regular_price) * 100);
        
        const bestPlanHTML = `
            <div class="best-plan">
                <div class="best-plan-header">
                    <div>
                        <div class="best-plan-provider">${bestPlan.provider}</div>
                        <div class="best-plan-name">${bestPlan.plan_name}</div>
                        <div class="best-for">
                            <strong>Perfect for:</strong> ${plan.best_for}
                        </div>
                    </div>
                    <div class="best-plan-price-container">
                        <span class="best-plan-price">₹${plan.price}/mo</span>
                        <div>
                            <div class="best-plan-original">₹${plan.regular_price}/mo</div>
                            <div class="best-plan-savings">Save ${savings}%</div>
                        </div>
                    </div>
                </div>
                
                <div class="best-plan-details">
                    <div class="detail-item">
                        <div class="detail-icon">✓</div>
                        <div>${typeof plan.websites === 'string' ? plan.websites : plan.websites} Website${plan.websites !== 1 ? 's' : ''}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-icon">✓</div>
                        <div>${plan.storage} ${plan.type} Storage</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-icon">✓</div>
                        <div>${plan.bandwidth} Bandwidth</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-icon">✓</div>
                        <div>${plan.email}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-icon">${plan.free_domain ? '✓' : '×'}</div>
                        <div>${plan.free_domain ? 'Free Domain' : 'No Free Domain'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-icon">${plan.ssl.includes('SSL') ? '✓' : '×'}</div>
                        <div>${plan.ssl}</div>
                    </div>
                </div>
            </div>
        `;
        
        bestPlanContainer.innerHTML = bestPlanHTML;
    }
    
    // Display all matching plans
    if (planCards) {
        data.all_plans.forEach(plan_data => {
            const plan = plan_data.plan;
            const savings = Math.round(((plan.regular_price - plan.price) / plan.regular_price) * 100);
            
            const planHTML = `
                <div class="plan-card ${plan_data.provider}">
                    <div class="plan-provider">
                        <div class="provider-logo">
                            <div class="provider-icon ${plan_data.provider}-icon">${plan_data.provider.charAt(0).toUpperCase()}</div>
                            <span>${plan_data.provider}</span>
                        </div>
                    </div>
                    <h3 class="plan-name">${plan_data.plan_name}</h3>
                    <div class="plan-price-container">
                        <span class="plan-price">₹${plan.price}/mo</span>
                        <span class="plan-original">₹${plan.regular_price}</span>
                    </div>
                    <ul class="plan-features">
                        <li class="plan-feature">
                            <span class="feature-icon">•</span>
                            <span>${typeof plan.websites === 'string' ? plan.websites : plan.websites} Website${plan.websites !== 1 ? 's' : ''}</span>
                        </li>
                        <li class="plan-feature">
                            <span class="feature-icon">•</span>
                            <span>${plan.storage} ${plan.type} Storage</span>
                        </li>
                        <li class="plan-feature">
                            <span class="feature-icon">•</span>
                            <span>${plan.bandwidth} Bandwidth</span>
                        </li>
                        <li class="plan-feature">
                            <span class="feature-icon">•</span>
                            <span>${plan.email}</span>
                        </li>
                        <li class="plan-feature">
                            <span class="feature-icon">${plan.free_domain ? '✓' : '×'}</span>
                            <span>${plan.free_domain ? 'Free Domain' : 'No Free Domain'}</span>
                        </li>
                        <li class="plan-feature">
                            <span class="feature-icon">${plan.ssl.includes('SSL') ? '✓' : '×'}</span>
                            <span>${plan.ssl}</span>
                        </li>
                    </ul>
                    <div class="best-for">
                        <strong>Best for:</strong> ${plan.best_for}
                    </div>
                </div>
            `;
            
            planCards.innerHTML += planHTML;
        });
    }
}

// Tips functionality
function showRandomTip() {
    const hostingTips = [
        "Look for hosting plans with SSD storage for faster website loading speeds.",
        "If you expect high traffic, choose a plan with unmetered bandwidth.",
        "For e-commerce sites, make sure your hosting includes a free SSL certificate.",
        "Managed WordPress hosting is a great option if you use WordPress.",
        "Check the uptime guarantee - good hosts offer at least 99.9% uptime.",
        "Backup features are essential to protect your website data.",
        "Consider your future growth needs when selecting a hosting plan."
    ];
    
    const tipCard = document.getElementById('tipCard');
    if (!tipCard) return;
    
    const tipContent = document.getElementById('tipContent');
    const randomTip = hostingTips[Math.floor(Math.random() * hostingTips.length)];
    tipContent.textContent = randomTip;
    tipCard.style.display = 'block';
}

function closeTip() {
    const tipCard = document.getElementById('tipCard');
    if (tipCard) {
        tipCard.style.display = 'none';
    }
}


// Initialize when the document is ready
// When the form is submitted
function toggleCustomPlanInputs() {
    const customPlanCheckbox = document.getElementById('custom_plan');
    if (!customPlanCheckbox) return; // Exit if element not found
    
    const isEnabled = customPlanCheckbox.checked;
    console.log("Custom plan toggle changed. Enabled:", isEnabled);
    
    // Get all manual input fields
    const manualInputs = document.querySelectorAll('.manual-input');
    
    // Enable or disable them based on checkbox state
    manualInputs.forEach(input => {
        input.disabled = !isEnabled;
        
        if (isEnabled) {
            input.classList.add('enabled');
        } else {
            input.classList.remove('enabled');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing app...");
    
    // Initialize range sliders
    const websitesSlider = document.getElementById('websites');
    const storageSlider = document.getElementById('storage');
    const budgetSlider = document.getElementById('budget');
    
    if (websitesSlider) updateRangeValue(websitesSlider, 'websitesValue', '', 'websitesInput');
    if (storageSlider) updateRangeValue(storageSlider, 'storageValue', '', 'storageInput');
    if (budgetSlider) updateRangeValue(budgetSlider, 'budgetValue', '₹', 'budgetInput');
    
    // Add event listener to custom plan toggle
    const customPlanToggle = document.getElementById('custom_plan');
    if (customPlanToggle) {
        console.log("Setting up custom plan toggle");
        customPlanToggle.addEventListener('change', toggleCustomPlanInputs);
        
        // Also initialize the toggle state on page load
        toggleCustomPlanInputs();
    }
    
    // Show a random tip after 5 seconds
    setTimeout(showRandomTip, 5000);
});

document.addEventListener('DOMContentLoaded', function() {
    // ... your existing initialization code ...
    
    // Add event listeners for hosting type radio buttons
    const hostingTypeRadios = document.querySelectorAll('input[name="hosting_type"]');
    hostingTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Update active class on type options
            document.querySelectorAll('.type-option').forEach(option => {
                option.classList.remove('active');
            });
            
            if (this.checked) {
                this.closest('.type-option').classList.add('active');
            }
            
            // Optionally, you can adjust form fields based on hosting type
            const hostingType = this.value;
            console.log("Hosting type changed to:", hostingType);
            
            // You can add logic here to show/hide certain form fields
            // or adjust default values based on hosting type
        });
    });
});