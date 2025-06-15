/**
 * HTTP Service for CERES Frontend
 * Handles all HTTP requests with authentication and error handling
 */

import { API_CONFIG, createAuthHeaders, API_ERRORS } from '../config/api.js'

class HttpService {
  constructor() {
    this.baseURL = API_CONFIG.baseURL
    this.timeout = API_CONFIG.timeout
  }

  // Get auth token from localStorage
  getToken() {
    return localStorage.getItem('token')
  }

  // Set auth token
  setToken(token) {
    localStorage.setItem('token', token)
  }

  // Remove auth token
  removeToken() {
    localStorage.removeItem('token')
  }

  // Create request headers
  createHeaders(includeAuth = true) {
    const headers = { ...API_CONFIG.headers }
    
    if (includeAuth) {
      const token = this.getToken()
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
    }
    
    return headers
  }

  // Handle API errors
  handleError(error) {
    if (!error.response) {
      throw new Error(API_ERRORS.NETWORK_ERROR)
    }

    const { status, data } = error.response

    switch (status) {
      case 401:
        this.removeToken()
        throw new Error(API_ERRORS.UNAUTHORIZED)
      case 403:
        throw new Error(API_ERRORS.FORBIDDEN)
      case 404:
        throw new Error(API_ERRORS.NOT_FOUND)
      case 500:
        throw new Error(API_ERRORS.SERVER_ERROR)
      default:
        throw new Error(data?.message || `HTTP Error ${status}`)
    }
  }

  // Generic request method
  async request(url, options = {}) {
    const config = {
      method: 'GET',
      headers: this.createHeaders(options.auth !== false),
      ...options
    }

    // Add body for POST/PUT/PATCH requests
    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), this.timeout)

      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw {
          response: {
            status: response.status,
            data: await response.json().catch(() => ({}))
          }
        }
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }

      return await response.text()
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error(API_ERRORS.TIMEOUT)
      }
      this.handleError(error)
    }
  }

  // HTTP Methods
  async get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' })
  }

  async post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: data
    })
  }

  async put(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: data
    })
  }

  async patch(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PATCH',
      body: data
    })
  }

  async delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' })
  }

  // File upload
  async upload(url, formData, options = {}) {
    const headers = this.createHeaders(options.auth !== false)
    delete headers['Content-Type'] // Let browser set it for FormData

    return this.request(url, {
      ...options,
      method: 'POST',
      headers,
      body: formData
    })
  }
}

// Create singleton instance
const httpService = new HttpService()

export default httpService

