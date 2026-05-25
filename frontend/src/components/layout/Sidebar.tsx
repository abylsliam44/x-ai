import { NavLink, useNavigate } from 'react-router-dom'
import { Icon } from '../common/Icon'
import { useAuth } from '../../hooks/useAuth'

interface NavItemProps {
  to: string
  icon: string
  label: string
  count?: number
  end?: boolean
}

function NavItem({ to, icon, label, count, end }: NavItemProps) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `nav-active-line relative flex items-center gap-3 px-3 pl-4 py-[9px] rounded-lg text-sm cursor-pointer transition-all duration-150 ${
          isActive
            ? 'text-tx bg-surface2 font-medium border border-border2/60'
            : 'text-tx3 hover:bg-surface2/60 hover:text-tx border border-transparent'
        }`
      }
    >
      {({ isActive }) => (
        <>
          <Icon name={icon} size={16} className={isActive ? 'text-tx' : 'text-tx4'} />
          <span className="tracking-[-0.005em]">{label}</span>
          {count !== undefined && (
            <span className="ml-auto font-mono text-[11px] text-tx4 bg-surface px-1.5 py-0.5 rounded">{count}</span>
          )}
        </>
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
    <aside className="border-r border-border px-3 py-5 flex flex-col sticky top-0 h-screen overflow-y-auto bg-surface/30">

      {/* Section label */}
      <div className="px-1 pb-2 font-mono text-[9px] tracking-[0.22em] uppercase text-tx4">
        Workspace
      </div>

      {/* Main nav */}
      <div className="flex flex-col gap-0.5">
        <NavItem to="/dashboard" icon="home" label="Dashboard" end />
        <NavItem to="/projects" icon="folder" label="Projects" />
      </div>

      {/* Content section */}
      <div className="mt-5">
        <div className="px-1 pb-2 font-mono text-[9px] tracking-[0.22em] uppercase text-tx4">
          Content
        </div>
        <div className="flex flex-col gap-0.5">
          <NavItem to="/settings/brand-voice" icon="spark" label="Brand Voice" />
          <NavItem to="/settings/writing-samples" icon="lib" label="Samples" />
        </div>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* User card */}
      <div className="mt-4 pt-4 border-t border-border">
        <button
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm hover:bg-surface2 transition-all duration-150 text-left group"
          onClick={() => navigate('/settings')}
        >
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0 ring-1 ring-border2 group-hover:ring-border2"
            style={{ background: 'linear-gradient(135deg, #e0e0e0, #666)', color: '#000' }}
          >
            {initials}
          </div>
          <div className="flex flex-col leading-tight min-w-0 flex-1">
            <span className="text-[13px] text-tx truncate font-medium">{user?.full_name ?? user?.email}</span>
            {user?.full_name && (
              <span className="text-[11px] text-tx4 font-mono truncate">{user.email}</span>
            )}
          </div>
          <Icon name="settings" size={13} className="text-tx4 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
        </button>

        <button
          className="w-full flex items-center gap-3 px-3 py-[9px] rounded-lg text-sm text-tx4 hover:text-tx2 hover:bg-surface2/50 transition-all duration-150 text-left mt-0.5"
          onClick={logout}
        >
          <Icon name="logout" size={15} />
          <span className="text-[13px]">Sign out</span>
        </button>
      </div>
    </aside>
  )
}
