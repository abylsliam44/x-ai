import { useEffect, type ReactNode } from 'react'
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { ProjectWizardPage } from './pages/ProjectWizardPage'
import { ProjectWorkspacePage } from './pages/ProjectWorkspacePage'
import { SettingsPage } from './pages/SettingsPage'
import { LandingPage } from './pages/LandingPage'
import { useAuth } from './hooks/useAuth'
import { Spinner } from './components/common/Spinner'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login', { state: { from: location }, replace: true })
    }
  }, [user, loading, navigate, location])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg">
        <Spinner size={24} />
      </div>
    )
  }

  if (!user) return null

  return <>{children}</>
}

function PublicRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg">
        <Spinner size={24} />
      </div>
    )
  }

  if (user) return <Navigate to="/dashboard" replace />

  return <>{children}</>
}

function LandingRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg">
        <Spinner size={24} />
      </div>
    )
  }

  if (user) return <Navigate to="/dashboard" replace />

  return <LandingPage />
}

export function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/new"
        element={
          <ProtectedRoute>
            <ProjectWizardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:id"
        element={
          <ProtectedRoute>
            <ProjectWorkspacePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings/:tab"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<LandingRoute />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
