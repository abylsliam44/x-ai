import { NavLink, useNavigate } from 'react-router-dom'
import { Icon } from '../common/Icon'
import { useAuth } from '../../hooks/useAuth'

interface NavItemProps {
  to: string
  icon: string
  label: string
  count?: number
}

function NavItem({ to, icon, label, count }: NavItemProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-[9px] rounded-pill text-sm cursor-pointer transition-all duration-150 ${
          isActive
            ? 'text-tx bg-surface2 font-medium'
            : 'text-tx2 hover:bg-surface2 hover:text-tx'
        }`
      }
    >
      <Icon name={icon} size={18} />
      <span>{label}</span>
      {count !== undefined && (
        <span className="ml-auto font-mono text-[11px] text-tx4">{count}</span>
      )}
    </NavLink>
  )
}

export function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : user?.email?.[0]?.toUpperCase() ?? 'U'

  return (
    <aside className="border-r border-border px-[14px] py-5 flex flex-col gap-0 sticky top-0 h-screen overflow-y-auto">
      {/* Main nav */}
      <div className="flex flex-col gap-1">
        <NavItem to="/dashboard" icon="home" label="Dashboard" />
        <NavItem to="/projects" icon="folder" label="Projects" />
        <NavItem to="/settings/brand-voice" icon="spark" label="Brand Voice" />
        <NavItem to="/settings/writing-samples" icon="lib" label="Samples" />
      </div>

      {/* Account */}
      <div className="mt-5 pt-5 border-t border-border flex flex-col gap-1">
        <div className="px-3 pb-2 font-mono text-[10px] tracking-[0.2em] uppercase text-tx4">
          Account
        </div>
        <button
          className="flex items-center gap-3 px-3 py-[9px] rounded-pill text-sm text-tx2 hover:bg-surface2 hover:text-tx transition-all duration-150 text-left w-full"
          onClick={() => navigate('/settings')}
        >
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
            style={{ background: 'linear-gradient(135deg, #fff, #888)', color: '#000' }}
          >
            {initials}
          </div>
          <div className="flex flex-col leading-tight min-w-0">
            <span className="text-[13px] text-tx truncate">{user?.full_name ?? user?.email}</span>
            {user?.full_name && (
              <span className="text-[12px] text-tx3 font-mono truncate">{user.email}</span>
            )}
          </div>
        </button>
      </div>

      {/* System */}
      <div className="mt-5 pt-5 border-t border-border flex flex-col gap-1">
        <div className="px-3 pb-2 font-mono text-[10px] tracking-[0.2em] uppercase text-tx4">
          System
        </div>
        <NavItem to="/settings" icon="settings" label="Settings" />
        <button
          className="flex items-center gap-3 px-3 py-[9px] rounded-pill text-sm text-tx2 hover:bg-surface2 hover:text-tx transition-all duration-150 text-left w-full"
          onClick={logout}
        >
          <Icon name="logout" size={18} />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  )
}
