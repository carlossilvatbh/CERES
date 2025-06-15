/**
 * API Configuration for CERES Frontend
 * Centralized configuration for all API calls
 */

// Base configuration
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  authURL: import.meta.env.VITE_API_AUTH_URL || 'http://localhost:8000/api/auth',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
}

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  auth: {
    login: `${API_CONFIG.authURL}/token/`,
    refresh: `${API_CONFIG.authURL}/token/refresh/`,
    verify: `${API_CONFIG.authURL}/token/verify/`,
  },
  
  // Customers
  customers: {
    list: `${API_CONFIG.baseURL}/customers/`,
    create: `${API_CONFIG.baseURL}/customers/`,
    detail: (id) => `${API_CONFIG.baseURL}/customers/${id}/`,
    update: (id) => `${API_CONFIG.baseURL}/customers/${id}/`,
    delete: (id) => `${API_CONFIG.baseURL}/customers/${id}/`,
  },
  
  // Documents
  documents: {
    list: `${API_CONFIG.baseURL}/documents/`,
    create: `${API_CONFIG.baseURL}/documents/`,
    detail: (id) => `${API_CONFIG.baseURL}/documents/${id}/`,
    upload: `${API_CONFIG.baseURL}/documents/upload/`,
  },
  
  // Screening
  screening: {
    list: `${API_CONFIG.baseURL}/screening/`,
    create: `${API_CONFIG.baseURL}/screening/`,
    detail: (id) => `${API_CONFIG.baseURL}/screening/${id}/`,
    run: (id) => `${API_CONFIG.baseURL}/screening/${id}/run/`,
  },
  
  // Risk Assessment
  risk: {
    list: `${API_CONFIG.baseURL}/risk/`,
    create: `${API_CONFIG.baseURL}/risk/`,
    detail: (id) => `${API_CONFIG.baseURL}/risk/${id}/`,
    assess: (id) => `${API_CONFIG.baseURL}/risk/${id}/assess/`,
  },
  
  // Cases
  cases: {
    list: `${API_CONFIG.baseURL}/cases/`,
    create: `${API_CONFIG.baseURL}/cases/`,
    detail: (id) => `${API_CONFIG.baseURL}/cases/${id}/`,
    update: (id) => `${API_CONFIG.baseURL}/cases/${id}/`,
  },
  
  // Users
  users: {
    list: `${API_CONFIG.baseURL}/users/`,
    profile: `${API_CONFIG.baseURL}/users/profile/`,
    update: (id) => `${API_CONFIG.baseURL}/users/${id}/`,
  },
  
  // Health Check
  health: `${API_CONFIG.baseURL.replace('/api/v1', '')}/healthz/`,
}

// HTTP Client Configuration
export const createAuthHeaders = (token) => ({
  ...API_CONFIG.headers,
  'Authorization': `Bearer ${token}`
})

// Error Messages
export const API_ERRORS = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'Unauthorized. Please login again.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'Resource not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  TIMEOUT: 'Request timeout. Please try again.',
}

// Development helpers
export const isDevelopment = import.meta.env.VITE_APP_ENVIRONMENT === 'development'
export const isProduction = import.meta.env.VITE_APP_ENVIRONMENT === 'production'

console.log('API Configuration loaded:', {
  baseURL: API_CONFIG.baseURL,
  environment: import.meta.env.VITE_APP_ENVIRONMENT,
  isDevelopment,
  isProduction
})

