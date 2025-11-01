// DianaBot Dashboard JavaScript

const API_BASE_URL = '/api';

// Authentication functions
function getToken() {
    return localStorage.getItem('auth_token');
}

function setToken(token) {
    localStorage.setItem('auth_token', token);
}

function removeToken() {
    localStorage.removeItem('auth_token');
}

function isAuthenticated() {
    const token = getToken();
    if (!token) return false;
    
    // Check if token is expired
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp > Date.now() / 1000;
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        // Unauthorized - redirect to login
        logout();
        return null;
    }
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
}

// Login function
async function login(username, password) {
    try {
        const response = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        if (response && response.access_token) {
            setToken(response.access_token);
            return true;
        }
        return false;
    } catch (error) {
        console.error('Login error:', error);
        return false;
    }
}

// Logout function
function logout() {
    removeToken();
    window.location.href = '/login';
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    
    // Don't check auth for login page
    if (currentPath === '/login') {
        return;
    }
    
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return;
    }
    
    // Set current user info if available
    const token = getToken();
    if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const userElement = document.getElementById('current-user');
        if (userElement) {
            userElement.textContent = payload.username;
        }
    }
});

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat('es-ES').format(num);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('es-ES');
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('es-ES');
}

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-${type} p-4 mb-4 rounded-md border`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('main .max-w-7xl');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Loading state management
function setLoading(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.innerHTML = '<div class="loading"></div>';
    } else {
        element.disabled = false;
        element.innerHTML = element.getAttribute('data-original-text') || element.textContent;
    }
}

// Form handling
function handleFormSubmit(form, onSubmit) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.setAttribute('data-original-text', originalText);
        
        setLoading(submitButton, true);
        
        try {
            await onSubmit(form);
        } catch (error) {
            console.error('Form submission error:', error);
            showAlert('Error al procesar la solicitud', 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });
}

// Data table utilities
function createDataTable(container, data, columns, options = {}) {
    const table = document.createElement('table');
    table.className = 'min-w-full divide-y divide-gray-200';
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    columns.forEach(column => {
        const th = document.createElement('th');
        th.className = 'px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
        th.textContent = column.header;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement('tbody');
    tbody.className = 'bg-white divide-y divide-gray-200';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        columns.forEach(column => {
            const td = document.createElement('td');
            td.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
            
            if (typeof column.render === 'function') {
                td.innerHTML = column.render(item);
            } else {
                td.textContent = item[column.key] || '';
            }
            
            row.appendChild(td);
        });
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);
}

// Export functions for global use
window.DianaBotDashboard = {
    apiRequest,
    login,
    logout,
    formatNumber,
    formatDate,
    formatDateTime,
    showAlert,
    setLoading,
    handleFormSubmit,
    createDataTable
};