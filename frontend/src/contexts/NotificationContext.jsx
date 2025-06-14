import React, { createContext, useContext, useState, useEffect } from 'react'

const NotificationContext = createContext()

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([])

  const addNotification = (notification) => {
    const id = Date.now().toString()
    const newNotification = {
      id,
      timestamp: new Date(),
      read: false,
      ...notification
    }
    
    setNotifications(prev => [newNotification, ...prev])
    
    // Auto remove after 5 seconds if it's a toast notification
    if (notification.type === 'toast') {
      setTimeout(() => {
        removeNotification(id)
      }, 5000)
    }
  }

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const clearAll = () => {
    setNotifications([])
  }

  const getUnreadCount = () => {
    return notifications.filter(n => !n.read).length
  }

  // Simulate some notifications on mount
  useEffect(() => {
    const simulateNotifications = () => {
      const sampleNotifications = [
        {
          type: 'alert',
          severity: 'high',
          title: 'Alerta de Alto Risco',
          message: 'Cliente Pedro Costa foi identificado em lista restritiva',
          category: 'screening'
        },
        {
          type: 'info',
          severity: 'medium',
          title: 'Documento Processado',
          message: 'RG de João Silva foi processado com sucesso',
          category: 'documents'
        },
        {
          type: 'success',
          severity: 'low',
          title: 'Screening Concluído',
          message: 'Verificação de Maria Santos finalizada sem alertas',
          category: 'screening'
        },
        {
          type: 'warning',
          severity: 'medium',
          title: 'Atualização de Fonte',
          message: 'Lista OFAC foi atualizada com 15 novos registros',
          category: 'system'
        }
      ]

      sampleNotifications.forEach((notification, index) => {
        setTimeout(() => {
          addNotification(notification)
        }, index * 1000)
      })
    }

    // Add sample notifications after 2 seconds
    setTimeout(simulateNotifications, 2000)
  }, [])

  const value = {
    notifications,
    addNotification,
    removeNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    getUnreadCount
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

