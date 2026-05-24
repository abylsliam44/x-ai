import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ApiError } from '../lib/api'
import { Spinner } from '../components/common/Spinner'

export function LoginPage() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-10 justify-center">
          <div className="w-8 h-8 bg-tx text-bg rounded-lg flex items-center justify-center font-bold text-base">
            n
          </div>
          <span className="font-semibold text-lg tracking-[-0.01em]">nfactorial</span>
        </div>

        <h1 className="text-2xl font-semibold tracking-tight mb-1 text-center">Sign in</h1>
        <p className="text-tx2 text-sm text-center mb-8">
          Continue to your content workspace.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {error && (
            <div className="px-4 py-3 border border-red-900/50 bg-red-900/10 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-mono text-tx3 uppercase tracking-wider">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-mono text-tx3 uppercase tracking-wider">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 w-full h-11 rounded-pill bg-tx text-bg font-semibold text-sm flex items-center justify-center gap-2 hover:bg-tx/90 transition-all disabled:opacity-50"
          >
            {loading ? <Spinner size={16} /> : 'Sign in'}
          </button>
        </form>

        <p className="text-center text-sm text-tx3 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-tx hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
