import { useEffect } from 'react'
import type { ReactNode } from 'react'
import { Icon } from './Icon'

interface ModalProps {
  title: string
  subtitle?: string
  onClose: () => void
  children: ReactNode
  width?: string
}

export function Modal({ title, subtitle, onClose, children, width = 'w-[540px]' }: ModalProps) {
  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handle)
    return () => document.removeEventListener('keydown', handle)
  }, [onClose])

  return (
    <div
      className="modal-backdrop"
      onClick={onClose}
    >
      <div
        className={`modal-panel ${width} max-w-[calc(100vw-40px)] bg-surface border border-border2 rounded-2xl p-7`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between mb-1">
          <div>
            <h3 className="text-lg font-semibold tracking-tight">{title}</h3>
            {subtitle && <p className="text-sm text-tx2 mt-1">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="ml-4 text-tx3 hover:text-tx transition-colors"
          >
            <Icon name="x" size={16} />
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
