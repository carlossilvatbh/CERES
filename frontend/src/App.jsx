import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import './App.css'

// Pages
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import EnrollmentPage from './pages/EnrollmentPage'
import DocumentsPage from './pages/DocumentsPage'
import ScreeningPage from './pages/ScreeningPage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'
import LoginPage from './pages/LoginPage'

// Layout
import Layout from './components/Layout'

// Context
import { AuthProvider } from './contexts/AuthContext'
import { NotificationProvider } from './contexts/NotificationContext'

function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <Router>
          <div className="min-h-screen bg-background">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="enrollment" element={<EnrollmentPage />} />
                <Route path="documents" element={<DocumentsPage />} />
                <Route path="screening" element={<ScreeningPage />} />
                <Route path="reports" element={<ReportsPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Routes>
            <Toaster />
          </div>
        </Router>
      </NotificationProvider>
    </AuthProvider>
  )
}

export default App

