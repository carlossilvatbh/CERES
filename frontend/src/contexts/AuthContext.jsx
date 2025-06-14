import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      // Verify token and get user info
      fetchUserInfo()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUserInfo = async () => {
    try {
      // For demo purposes, simulate user info
      const userData = {
        id: 1,
        username: 'admin',
        first_name: 'Admin',
        last_name: 'User',
        email: 'admin@ceres.com'
      }
      setUser(userData)
    } catch (error) {
      console.error('Error fetching user info:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials) => {
    try {
      // For demo purposes, simulate login
      if (credentials.username === 'admin' && credentials.password === 'admin123') {
        const mockToken = 'demo-token-' + Date.now()
        
        localStorage.setItem('token', mockToken)
        setToken(mockToken)
        
        // Set user data
        const userData = {
          id: 1,
          username: 'admin',
          first_name: 'Admin',
          last_name: 'User',
          email: 'admin@ceres.com'
        }
        setUser(userData)
        
        return { success: true }
      } else {
        return { success: false, error: 'Credenciais inválidas' }
      }
    } catch {
      return { success: false, error: 'Erro de rede' }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    setToken(null)
    setUser(null)
  }

  const refreshToken = async () => {
    // For demo purposes, always return true
    return true
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    refreshToken,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

