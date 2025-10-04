/**
 * STEAM Marketplace Frontend JavaScript
 * Handles user interactions, API calls, and dynamic content loading
 */

// Global state
let currentUser = null;
let apiBaseUrl = 'http://localhost:5001/api';
let selectedTokenPackage = null;
let currentContent = null;

// Utility Functions
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('show');
}

function showNotification(title, message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    notification.innerHTML = `
        <div class="notification-header">
            <div class="notification-title">${title}</div>
            <button class="notification-close" onclick="closeNotification(this)">×</button>
        </div>
        <p class="notification-message">${message}</p>
    `;
    
    container.appendChild(notification);
    
    // Show animation
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            closeNotification(notification.querySelector('.notification-close'));
        }
    }, 5000);
}

function closeNotification(button) {
    const notification = button.closest('.notification');
    notification.classList.remove('show');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

function showModal(modalId) {
    document.getElementById(modalId).classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
    document.body.style.overflow = 'auto';
}

// API Functions
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${apiBaseUrl}${endpoint}`, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Authentication Functions
async function handleLogin(event) {
    event.preventDefault();
    showLoading();
    
    try {
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        localStorage.setItem('access_token', response.access_token);
        currentUser = response.creator;
        
        updateUIForLoggedInUser();
        closeModal('loginModal');
        showNotification('Success', 'Logged in successfully!', 'success');
        
        // Reset form
        document.getElementById('loginForm').reset();
        
    } catch (error) {
        showNotification('Login Failed', error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    showLoading();
    
    try {
        const formData = {
            username: document.getElementById('registerUsername').value,
            email: document.getElementById('registerEmail').value,
            display_name: document.getElementById('registerDisplayName').value,
            profile_type: document.getElementById('registerProfileType').value,
            institution: document.getElementById('registerInstitution').value,
            country: document.getElementById('registerCountry').value,
            password: document.getElementById('registerPassword').value
        };
        
        const confirmPassword = document.getElementById('registerConfirmPassword').value;
        
        if (formData.password !== confirmPassword) {
            throw new Error('Passwords do not match');
        }
        
        const response = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        localStorage.setItem('access_token', response.access_token);
        currentUser = response.creator;
        
        updateUIForLoggedInUser();
        closeModal('registerModal');
        showNotification('Welcome!', 'Account created successfully! You received 100 free tokens to get started.', 'success');
        
        // Reset form
        document.getElementById('registerForm').reset();
        
    } catch (error) {
        showNotification('Registration Failed', error.message, 'error');
    } finally {
        hideLoading();
    }
}

function logout() {
    localStorage.removeItem('access_token');
    currentUser = null;
    updateUIForLoggedOutUser();
    showNotification('Logged Out', 'You have been logged out successfully.', 'info');
}

function updateUIForLoggedInUser() {
    // Hide login/register buttons
    document.getElementById('loginBtn').style.display = 'none';
    document.getElementById('registerBtn').style.display = 'none';
    
    // Show user menu and token balance
    document.getElementById('userMenu').style.display = 'flex';
    document.getElementById('tokenBalance').style.display = 'flex';
    
    // Update user info
    document.getElementById('userName').textContent = currentUser.display_name;
    document.getElementById('tokenCount').textContent = currentUser.token_balance;
    
    // Set user avatar (placeholder)
    document.getElementById('userAvatar').src = `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.display_name)}&background=2563eb&color=fff`;
}

function updateUIForLoggedOutUser() {
    // Show login/register buttons
    document.getElementById('loginBtn').style.display = 'flex';
    document.getElementById('registerBtn').style.display = 'flex';
    
    // Hide user menu and token balance
    document.getElementById('userMenu').style.display = 'none';
    document.getElementById('tokenBalance').style.display = 'none';
}

// Modal Functions
function showLoginModal() {
    showModal('loginModal');
}

function showRegisterModal() {
    populateCountrySelect();
    showModal('registerModal');
}

function switchToRegister() {
    closeModal('loginModal');
    showRegisterModal();
}

function switchToLogin() {
    closeModal('registerModal');
    showLoginModal();
}

function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
}

// Content Functions
async function loadTrendingContent() {
    try {
        const response = await apiCall('/content/trending?limit=12');
        const container = document.getElementById('trendingContent');
        
        if (response.trending_content.length === 0) {
            container.innerHTML = '<p class="text-center">No trending content available yet.</p>';
            return;
        }
        
        container.innerHTML = response.trending_content.map(content => `
            <div class="content-card" onclick="showContentDetails('${content.content_id}')">
                <img class="content-image" src="${content.preview_images[0] || 'https://via.placeholder.com/400x200'}" alt="${content.title}">
                <div class="content-info">
                    <div class="content-header">
                        <h3 class="content-title">${content.title}</h3>
                        <div class="content-price">
                            ${content.pricing_model === 'free' ? 'Free' : 
                              content.pricing_model === 'paid' ? 
                              `$${content.price_usd} / ${content.token_price} tokens` : 
                              'Freemium'}
                        </div>
                    </div>
                    <div class="content-meta">
                        <span><i class="fas fa-clock"></i> ${content.duration_minutes || 60} min</span>
                        <span><i class="fas fa-signal"></i> ${content.difficulty_level}</span>
                        <span><i class="fas fa-download"></i> ${content.download_count}</span>
                    </div>
                    <p class="content-description">${content.description}</p>
                    <div class="content-footer">
                        <div class="content-creator">
                            <div class="creator-avatar"></div>
                            <span>${content.creator_name}</span>
                        </div>
                        <div class="content-rating">
                            <div class="stars">
                                ${generateStarRating(content.rating)}
                            </div>
                            <span>${content.rating.toFixed(1)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load trending content:', error);
        document.getElementById('trendingContent').innerHTML = 
            '<p class="text-center">Failed to load trending content. Please try again later.</p>';
    }
}

async function loadCategories() {
    try {
        const response = await apiCall('/categories');
        const container = document.getElementById('categoryGrid');
        
        const categoryInfo = {
            'science': { icon: 'fa-microscope', description: 'Explore scientific concepts and experiments' },
            'technology': { icon: 'fa-laptop-code', description: 'Learn programming and digital skills' },
            'engineering': { icon: 'fa-cogs', description: 'Build and create with engineering principles' },
            'arts': { icon: 'fa-palette', description: 'Express creativity through arts and design' },
            'mathematics': { icon: 'fa-calculator', description: 'Master mathematical concepts and problem-solving' }
        };
        
        container.innerHTML = response.categories.slice(0, 5).map(category => {
            const info = categoryInfo[category] || { icon: 'fa-book', description: 'Educational content' };
            return `
                <div class="category-card" onclick="filterByCategory('${category}')">
                    <div class="category-icon">
                        <i class="fas ${info.icon}"></i>
                    </div>
                    <h3>${category.charAt(0).toUpperCase() + category.slice(1)}</h3>
                    <p>${info.description}</p>
                    <div class="category-stats">
                        <span>150+ resources</span>
                        <span>4.8★</span>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

async function loadMarketplaceAnalytics() {
    try {
        const response = await apiCall('/analytics/marketplace');
        const analytics = response.analytics;
        
        // Update hero stats
        document.getElementById('totalContent').textContent = analytics.total_content_items.toLocaleString();
        document.getElementById('totalCreators').textContent = analytics.total_creators.toLocaleString();
        document.getElementById('totalDownloads').textContent = analytics.total_downloads.toLocaleString();
        
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

async function showContentDetails(contentId) {
    showLoading();
    try {
        const response = await apiCall(`/content/${contentId}`);
        currentContent = response.content;
        
        // Populate modal with content details
        document.getElementById('contentTitle').textContent = currentContent.title;
        document.getElementById('contentDescription').textContent = currentContent.description;
        document.getElementById('contentImage').src = currentContent.preview_images[0] || 'https://via.placeholder.com/400x250';
        document.getElementById('contentType').textContent = currentContent.content_type.replace('_', ' ').toUpperCase();
        document.getElementById('contentDifficulty').textContent = currentContent.difficulty_level.toUpperCase();
        document.getElementById('contentDuration').textContent = `${currentContent.duration_minutes} minutes`;
        document.getElementById('contentAgeGroup').textContent = currentContent.age_groups.map(age => age.replace('_', '-')).join(', ');
        document.getElementById('downloadCount').textContent = `${currentContent.download_count} downloads`;
        document.getElementById('contentLanguage').textContent = currentContent.language.toUpperCase();
        
        // Rating
        document.getElementById('contentRating').innerHTML = generateStarRating(currentContent.rating);
        document.getElementById('ratingText').textContent = `${currentContent.rating.toFixed(1)} (${currentContent.review_count} reviews)`;
        
        // Learning objectives
        const objectivesList = document.getElementById('learningObjectives');
        objectivesList.innerHTML = currentContent.learning_objectives.map(obj => `<li>${obj}</li>`).join('');
        
        // Requirements
        const requirementsList = document.getElementById('contentRequirements');
        requirementsList.innerHTML = currentContent.requirements.map(req => `<li>${req}</li>`).join('');
        
        // Creator info
        if (currentContent.creator) {
            document.getElementById('creatorName').textContent = currentContent.creator.display_name;
            document.getElementById('creatorBio').textContent = currentContent.creator.bio || `${currentContent.creator.profile_type} from ${currentContent.creator.country || 'Global'}`;
            document.getElementById('creatorRating').textContent = currentContent.creator.rating.toFixed(1);
            document.getElementById('creatorContentCount').textContent = currentContent.creator.content_count || 0;
            document.getElementById('creatorAvatar').src = `https://ui-avatars.com/api/?name=${encodeURIComponent(currentContent.creator.display_name)}&background=2563eb&color=fff`;
        }
        
        // Pricing
        if (currentContent.pricing_model === 'free') {
            document.getElementById('contentPrice').innerHTML = '<span class="amount">Free</span>';
            document.getElementById('purchaseBtn').innerHTML = '<i class="fas fa-download"></i> Download';
        } else {
            document.getElementById('contentPrice').innerHTML = `
                <span class="amount">$${currentContent.price_usd}</span>
                <span class="currency">USD</span>
                <span class="or">or</span>
                <span class="tokens">${currentContent.token_price} tokens</span>
            `;
            document.getElementById('purchaseBtn').innerHTML = '<i class="fas fa-shopping-cart"></i> Purchase';
        }
        
        showModal('contentModal');
        
    } catch (error) {
        showNotification('Error', 'Failed to load content details', 'error');
    } finally {
        hideLoading();
    }
}

async function purchaseContent() {
    if (!currentUser) {
        showNotification('Login Required', 'Please login to purchase content', 'info');
        closeModal('contentModal');
        showLoginModal();
        return;
    }
    
    if (currentContent.pricing_model === 'free') {
        // Handle free download
        try {
            showLoading();
            const response = await apiCall(`/content/${currentContent.content_id}/purchase`, {
                method: 'POST',
                body: JSON.stringify({ payment_method: 'free' })
            });
            
            showNotification('Success', 'Content downloaded successfully!', 'success');
            closeModal('contentModal');
            
        } catch (error) {
            showNotification('Error', error.message, 'error');
        } finally {
            hideLoading();
        }
    } else {
        // Handle paid purchase - show payment options
        showPaymentModal();
    }
}

function showPaymentModal() {
    // For now, just use tokens if available
    if (currentUser.token_balance >= currentContent.token_price) {
        processPurchaseWithTokens();
    } else {
        showNotification('Insufficient Tokens', 'You need more tokens to purchase this content. Please buy tokens first.', 'warning');
        showModal('purchaseTokenModal');
    }
}

async function processPurchaseWithTokens() {
    try {
        showLoading();
        const response = await apiCall(`/content/${currentContent.content_id}/purchase`, {
            method: 'POST',
            body: JSON.stringify({ payment_method: 'tokens' })
        });
        
        // Update user token balance
        currentUser.token_balance -= currentContent.token_price;
        document.getElementById('tokenCount').textContent = currentUser.token_balance;
        
        showNotification('Success', 'Content purchased successfully!', 'success');
        closeModal('contentModal');
        
    } catch (error) {
        showNotification('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Content Creation Functions
function showCreateContent() {
    if (!currentUser) {
        showNotification('Login Required', 'Please login to create content', 'info');
        showLoginModal();
        return;
    }
    
    populateCreateContentForm();
    showModal('createContentModal');
}

async function populateCreateContentForm() {
    try {
        const response = await apiCall('/categories');
        
        // Populate categories
        const categoriesContainer = document.getElementById('contentCategories');
        categoriesContainer.innerHTML = response.categories.map(category => `
            <label>
                <input type="checkbox" name="categories" value="${category}">
                ${category.charAt(0).toUpperCase() + category.slice(1)}
            </label>
        `).join('');
        
        // Populate age groups
        const ageGroupsContainer = document.getElementById('contentAgeGroups');
        ageGroupsContainer.innerHTML = response.age_groups.map(age => `
            <label>
                <input type="checkbox" name="age_groups" value="${age}">
                ${age.replace('_', '-').toUpperCase()}
            </label>
        `).join('');
        
    } catch (error) {
        console.error('Failed to populate form:', error);
    }
}

function handlePricingModelChange() {
    const pricingModel = document.getElementById('pricingModelSelect').value;
    const pricingInputs = document.getElementById('pricingInputs');
    
    if (pricingModel === 'free') {
        pricingInputs.style.display = 'none';
    } else {
        pricingInputs.style.display = 'block';
    }
}

async function handleCreateContent(event) {
    event.preventDefault();
    showLoading();
    
    try {
        const formData = {
            title: document.getElementById('contentTitle').value,
            description: document.getElementById('contentDescriptionInput').value,
            content_type: document.getElementById('contentTypeSelect').value,
            categories: Array.from(document.querySelectorAll('input[name="categories"]:checked')).map(cb => cb.value),
            age_groups: Array.from(document.querySelectorAll('input[name="age_groups"]:checked')).map(cb => cb.value),
            difficulty_level: document.getElementById('contentDifficultySelect').value,
            duration_minutes: parseInt(document.getElementById('contentDurationInput').value),
            learning_objectives: document.getElementById('learningObjectivesInput').value.split('\n').filter(obj => obj.trim()),
            requirements: document.getElementById('requirementsInput').value.split('\n').filter(req => req.trim()),
            tools_needed: document.getElementById('toolsNeededInput').value.split('\n').filter(tool => tool.trim()),
            pricing_model: document.getElementById('pricingModelSelect').value,
            price_usd: parseFloat(document.getElementById('priceUsdInput').value) || 0,
            token_price: parseInt(document.getElementById('tokenPriceInput').value) || 0
        };
        
        const response = await apiCall('/content', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        showNotification('Success', 'Content created successfully!', 'success');
        closeModal('createContentModal');
        
        // Reset form
        document.getElementById('createContentForm').reset();
        
        // Refresh trending content
        loadTrendingContent();
        
    } catch (error) {
        showNotification('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Token Purchase Functions
function selectTokenPackage(tokens, price) {
    selectedTokenPackage = { tokens, price };
    
    // Update UI
    document.querySelectorAll('.package').forEach(pkg => pkg.classList.remove('selected'));
    event.currentTarget.classList.add('selected');
    
    // Show purchase summary
    document.getElementById('selectedTokens').textContent = tokens;
    document.getElementById('selectedPrice').textContent = `$${price.toFixed(2)}`;
    document.getElementById('totalPrice').textContent = `$${price.toFixed(2)}`;
    document.getElementById('purchaseSummary').style.display = 'block';
}

async function processPurchaseTokens() {
    if (!selectedTokenPackage) {
        showNotification('Error', 'Please select a token package first', 'error');
        return;
    }
    
    showLoading();
    try {
        const response = await apiCall('/tokens/purchase', {
            method: 'POST',
            body: JSON.stringify({
                token_amount: selectedTokenPackage.tokens,
                payment_method: 'credit_card'
            })
        });
        
        // Update user balance
        currentUser.token_balance = response.new_balance;
        document.getElementById('tokenCount').textContent = currentUser.token_balance;
        
        showNotification('Success', `Successfully purchased ${selectedTokenPackage.tokens} tokens!`, 'success');
        closeModal('purchaseTokenModal');
        
        // Reset selection
        selectedTokenPackage = null;
        document.getElementById('purchaseSummary').style.display = 'none';
        document.querySelectorAll('.package').forEach(pkg => pkg.classList.remove('selected'));
        
    } catch (error) {
        showNotification('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Search Functions
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;
    
    showLoading();
    try {
        const response = await apiCall(`/content/search?q=${encodeURIComponent(query)}`);
        
        // Update trending content section with search results
        const container = document.getElementById('trendingContent');
        const sectionHeader = document.querySelector('.trending .section-header h2');
        sectionHeader.textContent = `Search Results for "${query}"`;
        
        if (response.results.length === 0) {
            container.innerHTML = '<p class="text-center">No content found for your search.</p>';
            return;
        }
        
        container.innerHTML = response.results.map(content => `
            <div class="content-card" onclick="showContentDetails('${content.content_id}')">
                <img class="content-image" src="${content.preview_images[0] || 'https://via.placeholder.com/400x200'}" alt="${content.title}">
                <div class="content-info">
                    <div class="content-header">
                        <h3 class="content-title">${content.title}</h3>
                        <div class="content-price">
                            ${content.pricing_model === 'free' ? 'Free' : 
                              content.pricing_model === 'paid' ? 
                              `$${content.price_usd} / ${content.token_price} tokens` : 
                              'Freemium'}
                        </div>
                    </div>
                    <div class="content-meta">
                        <span><i class="fas fa-clock"></i> ${content.duration_minutes || 60} min</span>
                        <span><i class="fas fa-signal"></i> ${content.difficulty_level}</span>
                        <span><i class="fas fa-download"></i> ${content.download_count}</span>
                    </div>
                    <p class="content-description">${content.description}</p>
                    <div class="content-footer">
                        <div class="content-creator">
                            <div class="creator-avatar"></div>
                            <span>Creator</span>
                        </div>
                        <div class="content-rating">
                            <div class="stars">
                                ${generateStarRating(content.rating)}
                            </div>
                            <span>${content.rating.toFixed(1)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        showNotification('Error', 'Search failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Utility Functions
function generateStarRating(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    return [
        ...Array(fullStars).fill('<i class="fas fa-star"></i>'),
        ...(hasHalfStar ? ['<i class="fas fa-star-half-alt"></i>'] : []),
        ...Array(emptyStars).fill('<i class="far fa-star"></i>')
    ].join('');
}

function populateCountrySelect() {
    const countries = [
        'United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France', 'Spain', 'Italy',
        'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Japan', 'South Korea', 'Singapore',
        'India', 'China', 'Brazil', 'Mexico', 'Argentina', 'South Africa', 'Other'
    ];
    
    const select = document.getElementById('registerCountry');
    select.innerHTML = '<option value="">Select country</option>' +
        countries.map(country => `<option value="${country}">${country}</option>`).join('');
}

function filterByCategory(category) {
    // Implement category filtering
    document.getElementById('searchInput').value = category;
    performSearch();
}

function exploreContent() {
    document.querySelector('.trending').scrollIntoView({ behavior: 'smooth' });
}

// Navigation Functions
function showProfile() {
    showNotification('Coming Soon', 'Profile management is coming soon!', 'info');
}

function showMyContent() {
    showNotification('Coming Soon', 'Content management is coming soon!', 'info');
}

function showPurchases() {
    showNotification('Coming Soon', 'Purchase history is coming soon!', 'info');
}

function showAnalytics() {
    showNotification('Coming Soon', 'Analytics dashboard is coming soon!', 'info');
}

function addToWishlist() {
    showNotification('Coming Soon', 'Wishlist feature is coming soon!', 'info');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        // Validate token and get user info
        apiCall('/creators/profile')
            .then(response => {
                currentUser = response.creator;
                updateUIForLoggedInUser();
            })
            .catch(() => {
                // Token is invalid, remove it
                localStorage.removeItem('access_token');
                updateUIForLoggedOutUser();
            });
    }
    
    // Load initial content
    loadTrendingContent();
    loadCategories();
    loadMarketplaceAnalytics();
    
    // Setup search on Enter key
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Setup filter tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            if (filter === 'all') {
                loadTrendingContent();
            } else {
                filterByCategory(filter);
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.user-menu')) {
            document.getElementById('userDropdown').classList.remove('show');
        }
        
        if (!e.target.closest('.modal')) {
            // Close modals when clicking outside (but not for important modals)
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                modal.classList.remove('show');
            });
            document.body.style.overflow = 'auto';
        }
    });
});

// Global function attachments for HTML onclick handlers
window.showLoginModal = showLoginModal;
window.showRegisterModal = showRegisterModal;
window.closeModal = closeModal;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.switchToRegister = switchToRegister;
window.switchToLogin = switchToLogin;
window.toggleUserDropdown = toggleUserDropdown;
window.logout = logout;
window.showProfile = showProfile;
window.showMyContent = showMyContent;
window.showCreateContent = showCreateContent;
window.showPurchases = showPurchases;
window.showAnalytics = showAnalytics;
window.performSearch = performSearch;
window.exploreContent = exploreContent;
window.filterByCategory = filterByCategory;
window.showContentDetails = showContentDetails;
window.purchaseContent = purchaseContent;
window.addToWishlist = addToWishlist;
window.handleCreateContent = handleCreateContent;
window.handlePricingModelChange = handlePricingModelChange;
window.selectTokenPackage = selectTokenPackage;
window.processPurchaseTokens = processPurchaseTokens;
window.closeNotification = closeNotification;