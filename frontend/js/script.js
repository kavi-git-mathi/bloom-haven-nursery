// API Base URL
const API_BASE = 'http://127.0.0.1:5000/api';

// State
let currentUser = null;
let plants = [];
let cart = [];

// DOM Elements
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.nav-link');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Bloom Haven Nursery...');
    initializeApp();
    setupEventListeners();
    loadPlants();
    checkAuthStatus();
});

function initializeApp() {
    const userId = sessionStorage.getItem('user_id');
    if (userId) {
        currentUser = { id: userId };
        updateAuthUI();
        loadCart();
    }
}

function setupEventListeners() {
    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.getAttribute('data-section');
            showSection(sectionId);
            
            navLinks.forEach(nl => nl.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Category cards
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', () => {
            const sectionId = card.getAttribute('data-section');
            showSection(sectionId);
            
            navLinks.forEach(nl => nl.classList.remove('active'));
            document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
        });
    });

    // Auth buttons
    document.getElementById('login-btn').addEventListener('click', () => showModal('login-modal'));
    document.getElementById('signup-btn').addEventListener('click', () => showModal('signup-modal'));
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Auth modals
    document.querySelectorAll('.close-auth').forEach(btn => {
        btn.addEventListener('click', () => {
            hideModal('login-modal');
            hideModal('signup-modal');
        });
    });

    document.getElementById('show-signup').addEventListener('click', (e) => {
        e.preventDefault();
        hideModal('login-modal');
        showModal('signup-modal');
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        hideModal('signup-modal');
        showModal('login-modal');
    });

    // Auth forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('signup-form').addEventListener('submit', handleSignup);

    // Cart
    document.getElementById('cart-btn').addEventListener('click', () => showModal('cart-sidebar'));
    document.getElementById('close-cart').addEventListener('click', () => hideModal('cart-sidebar'));
    document.getElementById('checkout-btn').addEventListener('click', () => {
        if (cart.length === 0) {
            alert('Your cart is empty!');
            return;
        }
        showCheckoutModal();
    });

    // Checkout
    document.getElementById('close-checkout').addEventListener('click', () => hideModal('checkout-modal'));
    document.getElementById('checkout-form').addEventListener('submit', handleCheckout);

    // Contact form
    document.getElementById('contact-form').addEventListener('submit', handleContact);
}

function showSection(sectionId) {
    sections.forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// API Functions
async function loadPlants() {
    try {
        console.log('Loading plants from API...');
        const response = await fetch(`${API_BASE}/plants`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        plants = await response.json();
        console.log('Plants loaded:', plants);
        renderPlants();
    } catch (error) {
        console.error('Error loading plants:', error);
        // Show error message to user
        showNotification('Error loading plants. Please check if backend is running.');
    }
}

function renderPlants() {
    const floweringContainer = document.getElementById('flowering-plants');
    const indoorContainer = document.getElementById('indoor-plants');
    const vegetableContainer = document.getElementById('vegetable-plants');

    // Clear containers
    floweringContainer.innerHTML = '';
    indoorContainer.innerHTML = '';
    vegetableContainer.innerHTML = '';

    // Show message if no plants
    if (plants.length === 0) {
        const message = '<p class="no-plants">No plants found. Please check backend connection.</p>';
        floweringContainer.innerHTML = message;
        indoorContainer.innerHTML = message;
        vegetableContainer.innerHTML = message;
        return;
    }

    // Render plants by category
    plants.forEach(plant => {
        const plantCard = createPlantCard(plant);
        
        if (plant.type === 'flowering') {
            floweringContainer.appendChild(plantCard);
        } else if (plant.type === 'indoor') {
            indoorContainer.appendChild(plantCard);
        } else if (plant.type === 'vegetable') {
            vegetableContainer.appendChild(plantCard);
        }
    });
}

function createPlantCard(plant) {
    const card = document.createElement('div');
    card.className = 'plant-card';
    
    // FIXED: Properly handle the image HTML without syntax errors
    const imageHtml = plant.image 
        ? `<img src="${plant.image}" alt="${plant.name}" class="plant-img">`
        : `<div class="plant-image-placeholder"><i class="fas fa-leaf"></i></div>`;
    
    card.innerHTML = `
        <div class="plant-image">
            ${imageHtml}
        </div>
        <div class="plant-info">
            <h3 class="plant-name">${plant.name}</h3>
            <div class="plant-price">$${plant.price.toFixed(2)}</div>
            <p class="plant-description">${plant.description}</p>
            <button class="btn-primary btn-full add-to-cart" data-plant-id="${plant.id}">
                Add to Cart
            </button>
        </div>
    `;
    
    card.querySelector('.add-to-cart').addEventListener('click', () => addToCart(plant.id));
    
    return card;
}
a// In the renderCart function, update this part:
cartItem.innerHTML = `
    <div class="cart-item-image">
        ${item.plant_image ? `<img src="${item.plant_image}" alt="${item.plant_name}">` : '<i class="fas fa-leaf"></i>'}
    </div>
    <div class="cart-item-info">
        <div class="cart-item-name">${item.plant_name}</div>
        <div class="cart-item-price">$${item.plant_price.toFixed(2)}</div>
    </div>
    <div class="cart-item-actions">
        <div class="quantity-controls">
            <button class="quantity-btn decrease" data-plant-id="${item.plant_id}">-</button>
            <span>${item.quantity}</span>
            <button class="quantity-btn increase" data-plant-id="${item.plant_id}">+</button>
        </div>
        <button class="remove-btn" data-plant-id="${item.plant_id}">
            <i class="fas fa-trash"></i>
        </button>
    </div>
`;

async function loadCart() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${API_BASE}/cart`);
        if (response.ok) {
            cart = await response.json();
            renderCart();
        }
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

function renderCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    const cartTotal = document.getElementById('cart-total');
    
    cartItemsContainer.innerHTML = '';
    
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        cartCount.textContent = '0';
        cartTotal.textContent = '$0.00';
        return;
    }
    
    let total = 0;
    let itemCount = 0;
    
    cart.forEach(item => {
        const itemTotal = item.plant_price * item.quantity;
        total += itemTotal;
        itemCount += item.quantity;
        
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-image">
                ${item.plant_image ? `<img src="${item.plant_image}" alt="${item.plant_name}">` : '<i class="fas fa-leaf"></i>'}
            </div>
            <div class="cart-item-info">
                <div class="cart-item-name">${item.plant_name}</div>
                <div class="cart-item-price">$${item.plant_price.toFixed(2)}</div>
            </div>
            <div class="cart-item-actions">
                <div class="quantity-controls">
                    <button class="quantity-btn decrease" data-plant-id="${item.plant_id}">-</button>
                    <span>${item.quantity}</span>
                    <button class="quantity-btn increase" data-plant-id="${item.plant_id}">+</button>
                </div>
                <button class="remove-btn" data-plant-id="${item.plant_id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        cartItemsContainer.appendChild(cartItem);
    });
    
    cartCount.textContent = itemCount;
    cartTotal.textContent = `$${total.toFixed(2)}`;
    
    // Add event listeners for cart item actions
    document.querySelectorAll('.decrease').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const plantId = e.target.getAttribute('data-plant-id');
            updateCartItem(plantId, -1);
        });
    });
    
    document.querySelectorAll('.increase').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const plantId = e.target.getAttribute('data-plant-id');
            updateCartItem(plantId, 1);
        });
    });
    
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const plantId = e.target.closest('.remove-btn').getAttribute('data-plant-id');
            removeFromCart(plantId);
        });
    });
}

async function updateCartItem(plantId, change) {
    try {
        const cartItem = cart.find(item => item.plant_id == plantId);
        if (!cartItem) return;
        
        const newQuantity = cartItem.quantity + change;
        
        if (newQuantity <= 0) {
            removeFromCart(plantId);
        } else {
            await fetch(`${API_BASE}/cart`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plant_id: plantId
                })
            });
            
            await fetch(`${API_BASE}/cart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plant_id: plantId,
                    quantity: newQuantity
                })
            });
            
            loadCart();
        }
    } catch (error) {
        console.error('Error updating cart:', error);
    }
}

async function removeFromCart(plantId) {
    try {
        const response = await fetch(`${API_BASE}/cart`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                plant_id: plantId
            })
        });
        
        if (response.ok) {
            loadCart();
            showNotification('Item removed from cart');
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
    }
}

// Auth Functions
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = { id: data.user_id };
            sessionStorage.setItem('user_id', data.user_id);
            updateAuthUI();
            loadCart();
            hideModal('login-modal');
            showNotification('Login successful!');
        } else {
            const error = await response.json();
            alert(error.error);
        }
    } catch (error) {
        console.error('Error logging in:', error);
        alert('Error connecting to server. Please check if backend is running.');
    }
}

async function handleSignup(e) {
    e.preventDefault();
    
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    
    try {
        const response = await fetch(`${API_BASE}/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = { id: data.user_id };
            sessionStorage.setItem('user_id', data.user_id);
            updateAuthUI();
            loadCart();
            hideModal('signup-modal');
            showNotification('Account created successfully!');
        } else {
            const error = await response.json();
            alert(error.error);
        }
    } catch (error) {
        console.error('Error signing up:', error);
        alert('Error connecting to server. Please check if backend is running.');
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE}/logout`);
        currentUser = null;
        sessionStorage.removeItem('user_id');
        cart = [];
        updateAuthUI();
        renderCart();
        showNotification('Logged out successfully');
    } catch (error) {
        console.error('Error logging out:', error);
    }
}

function updateAuthUI() {
    const authSection = document.querySelector('.nav-auth');
    const userSection = document.querySelector('.nav-user');
    const userName = document.getElementById('user-name');
    
    if (currentUser) {
        authSection.style.display = 'none';
        userSection.style.display = 'flex';
        userName.textContent = 'User';
    } else {
        authSection.style.display = 'flex';
        userSection.style.display = 'none';
    }
}

function checkAuthStatus() {
    const userId = sessionStorage.getItem('user_id');
    if (userId) {
        currentUser = { id: userId };
        updateAuthUI();
        loadCart();
    }
}

// Checkout Functions
function showCheckoutModal() {
    const orderItemsContainer = document.getElementById('order-items');
    const orderTotalElement = document.getElementById('order-total');
    
    orderItemsContainer.innerHTML = '';
    
    let total = 0;
    
    cart.forEach(item => {
        const itemTotal = item.plant_price * item.quantity;
        total += itemTotal;
        
        const orderItem = document.createElement('div');
        orderItem.className = 'order-item';
        orderItem.innerHTML = `
            <span>${item.plant_name} x ${item.quantity}</span>
            <span>$${itemTotal.toFixed(2)}</span>
        `;
        
        orderItemsContainer.appendChild(orderItem);
    });
    
    orderTotalElement.textContent = `$${total.toFixed(2)}`;
    showModal('checkout-modal');
}

async function handleCheckout(e) {
    e.preventDefault();
    
    const deliveryAddress = document.getElementById('delivery-address').value;
    const deliveryOption = document.getElementById('delivery-option').value;
    
    if (!deliveryAddress || !deliveryOption) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/order`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                delivery_address: deliveryAddress,
                delivery_option: deliveryOption
            })
        });
        
        if (response.ok) {
            hideModal('checkout-modal');
            hideModal('cart-sidebar');
            showNotification('Order placed successfully!');
            loadCart();
        } else {
            const error = await response.json();
            alert(error.error);
        }
    } catch (error) {
        console.error('Error placing order:', error);
    }
}

// Contact Form
function handleContact(e) {
    e.preventDefault();
    
    const name = document.getElementById('contact-name').value;
    const email = document.getElementById('contact-email').value;
    const message = document.getElementById('contact-message').value;
    
    alert(`Thank you for your message, ${name}! We'll get back to you soon.`);
    e.target.reset();
}

// Utility Functions
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--primary);
        color: white;
        padding: 1rem 2rem;
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        z-index: 1300;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 3000);
}