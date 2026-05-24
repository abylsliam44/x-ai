import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { auth } from '../lib/api'
import { clearToken, getToken, setToken } from '../lib/auth'
import type { User } from '../types/models'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const fetchMe = useCallback(async () => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    try {
      const me = await auth.me()
      setUser(me)
    } catch {
      clearToken()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMe()
  }, [fetchMe])

  const login = async (email: string, password: string) => {
    const res = await auth.login(email, password)
    setToken(res.access_token)
    const me = await auth.me()
    setUser(me)
    navigate('/dashboard')
  }

  const register = async (email: string, password: string, full_name: string) => {
    const res = await auth.register(email, password, full_name)
    setToken(res.access_token)
    const me = await auth.me()
    setUser(me)
    navigate('/dashboard')
  }

  const logout = () => {
    clearToken()
    setUser(null)
    navigate('/login')
  }

  return { user, loading, login, register, logout }
}
