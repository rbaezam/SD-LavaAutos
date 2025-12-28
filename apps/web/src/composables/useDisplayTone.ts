/**
 * Composable for status-based color tones in the display screen.
 * Provides consistent visual identity per status column.
 */

// Normalize status name for matching (lowercase, no accents)
function normalizeStatusName(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
}

// Simple hash function for consistent color assignment
function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = (hash << 5) - hash + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash)
}

// Known status patterns and their color tones
const STATUS_PATTERNS: Record<string, string> = {
  // Waiting states
  'en espera': 'slate',
  'espera': 'slate',
  'recepcion': 'slate',
  'recibido': 'slate',
  'pendiente': 'slate',

  // Washing states
  'en lavado': 'blue',
  'lavado': 'blue',
  'lavando': 'blue',

  // Drying states
  'en secado': 'amber',
  'secado': 'amber',
  'secando': 'amber',

  // Detailing states
  'detallado': 'violet',
  'detalle': 'violet',
  'detallando': 'violet',
  'aspirado': 'violet',

  // Ready/completed states
  'listo': 'emerald',
  'terminado': 'emerald',
  'completado': 'emerald',

  // Delivered states
  'entregado': 'teal',
  'entrega': 'teal',
}

// Fallback color palette for unknown statuses
const FALLBACK_TONES = ['sky', 'indigo', 'rose', 'orange', 'cyan', 'fuchsia']

export interface ToneClasses {
  // Light mode
  bar: string
  headerBg: string
  headerBorder: string
  badge: string
  badgeText: string
  // Dark mode
  barDark: string
  headerBgDark: string
  headerBorderDark: string
  badgeDark: string
  badgeTextDark: string
}

// Tone definitions with Tailwind classes
const TONE_MAP: Record<string, ToneClasses> = {
  slate: {
    bar: 'bg-slate-400',
    headerBg: 'bg-slate-50',
    headerBorder: 'border-l-slate-400',
    badge: 'bg-slate-100',
    badgeText: 'text-slate-600',
    barDark: 'bg-slate-500',
    headerBgDark: 'bg-slate-800/50',
    headerBorderDark: 'border-l-slate-500',
    badgeDark: 'bg-slate-700',
    badgeTextDark: 'text-slate-300',
  },
  blue: {
    bar: 'bg-blue-400',
    headerBg: 'bg-blue-50',
    headerBorder: 'border-l-blue-400',
    badge: 'bg-blue-100',
    badgeText: 'text-blue-600',
    barDark: 'bg-blue-500',
    headerBgDark: 'bg-blue-900/30',
    headerBorderDark: 'border-l-blue-500',
    badgeDark: 'bg-blue-800',
    badgeTextDark: 'text-blue-300',
  },
  amber: {
    bar: 'bg-amber-400',
    headerBg: 'bg-amber-50',
    headerBorder: 'border-l-amber-400',
    badge: 'bg-amber-100',
    badgeText: 'text-amber-600',
    barDark: 'bg-amber-500',
    headerBgDark: 'bg-amber-900/30',
    headerBorderDark: 'border-l-amber-500',
    badgeDark: 'bg-amber-800',
    badgeTextDark: 'text-amber-300',
  },
  violet: {
    bar: 'bg-violet-400',
    headerBg: 'bg-violet-50',
    headerBorder: 'border-l-violet-400',
    badge: 'bg-violet-100',
    badgeText: 'text-violet-600',
    barDark: 'bg-violet-500',
    headerBgDark: 'bg-violet-900/30',
    headerBorderDark: 'border-l-violet-500',
    badgeDark: 'bg-violet-800',
    badgeTextDark: 'text-violet-300',
  },
  emerald: {
    bar: 'bg-emerald-400',
    headerBg: 'bg-emerald-50',
    headerBorder: 'border-l-emerald-400',
    badge: 'bg-emerald-100',
    badgeText: 'text-emerald-600',
    barDark: 'bg-emerald-500',
    headerBgDark: 'bg-emerald-900/30',
    headerBorderDark: 'border-l-emerald-500',
    badgeDark: 'bg-emerald-800',
    badgeTextDark: 'text-emerald-300',
  },
  teal: {
    bar: 'bg-teal-400',
    headerBg: 'bg-teal-50',
    headerBorder: 'border-l-teal-400',
    badge: 'bg-teal-100',
    badgeText: 'text-teal-600',
    barDark: 'bg-teal-500',
    headerBgDark: 'bg-teal-900/30',
    headerBorderDark: 'border-l-teal-500',
    badgeDark: 'bg-teal-800',
    badgeTextDark: 'text-teal-300',
  },
  sky: {
    bar: 'bg-sky-400',
    headerBg: 'bg-sky-50',
    headerBorder: 'border-l-sky-400',
    badge: 'bg-sky-100',
    badgeText: 'text-sky-600',
    barDark: 'bg-sky-500',
    headerBgDark: 'bg-sky-900/30',
    headerBorderDark: 'border-l-sky-500',
    badgeDark: 'bg-sky-800',
    badgeTextDark: 'text-sky-300',
  },
  indigo: {
    bar: 'bg-indigo-400',
    headerBg: 'bg-indigo-50',
    headerBorder: 'border-l-indigo-400',
    badge: 'bg-indigo-100',
    badgeText: 'text-indigo-600',
    barDark: 'bg-indigo-500',
    headerBgDark: 'bg-indigo-900/30',
    headerBorderDark: 'border-l-indigo-500',
    badgeDark: 'bg-indigo-800',
    badgeTextDark: 'text-indigo-300',
  },
  rose: {
    bar: 'bg-rose-400',
    headerBg: 'bg-rose-50',
    headerBorder: 'border-l-rose-400',
    badge: 'bg-rose-100',
    badgeText: 'text-rose-600',
    barDark: 'bg-rose-500',
    headerBgDark: 'bg-rose-900/30',
    headerBorderDark: 'border-l-rose-500',
    badgeDark: 'bg-rose-800',
    badgeTextDark: 'text-rose-300',
  },
  orange: {
    bar: 'bg-orange-400',
    headerBg: 'bg-orange-50',
    headerBorder: 'border-l-orange-400',
    badge: 'bg-orange-100',
    badgeText: 'text-orange-600',
    barDark: 'bg-orange-500',
    headerBgDark: 'bg-orange-900/30',
    headerBorderDark: 'border-l-orange-500',
    badgeDark: 'bg-orange-800',
    badgeTextDark: 'text-orange-300',
  },
  cyan: {
    bar: 'bg-cyan-400',
    headerBg: 'bg-cyan-50',
    headerBorder: 'border-l-cyan-400',
    badge: 'bg-cyan-100',
    badgeText: 'text-cyan-600',
    barDark: 'bg-cyan-500',
    headerBgDark: 'bg-cyan-900/30',
    headerBorderDark: 'border-l-cyan-500',
    badgeDark: 'bg-cyan-800',
    badgeTextDark: 'text-cyan-300',
  },
  fuchsia: {
    bar: 'bg-fuchsia-400',
    headerBg: 'bg-fuchsia-50',
    headerBorder: 'border-l-fuchsia-400',
    badge: 'bg-fuchsia-100',
    badgeText: 'text-fuchsia-600',
    barDark: 'bg-fuchsia-500',
    headerBgDark: 'bg-fuchsia-900/30',
    headerBorderDark: 'border-l-fuchsia-500',
    badgeDark: 'bg-fuchsia-800',
    badgeTextDark: 'text-fuchsia-300',
  },
}

/**
 * Get the tone name for a status
 */
export function getStatusTone(statusName: string, statusId?: string): string {
  const normalized = normalizeStatusName(statusName)

  // Check for known patterns
  for (const [pattern, tone] of Object.entries(STATUS_PATTERNS)) {
    if (normalized.includes(pattern)) {
      return tone
    }
  }

  // Fallback: use hash of status ID or name for consistent color
  const hashSource = statusId || statusName
  const hash = hashString(hashSource)
  const fallbackIndex = hash % FALLBACK_TONES.length
  return FALLBACK_TONES[fallbackIndex]
}

/**
 * Get Tailwind classes for a status tone
 */
export function getToneClasses(statusName: string, statusId?: string): ToneClasses {
  const tone = getStatusTone(statusName, statusId)
  return TONE_MAP[tone] || TONE_MAP.slate
}

// Empty state messages (varied but professional)
const EMPTY_MESSAGES = [
  'Todo despejado por aquí',
  'Sin vehículos por el momento',
  'En espera de próximos autos',
  'Nada pendiente en este estado',
  'Sin movimiento por ahora',
]

/**
 * Get a consistent empty message for a status (based on hash)
 */
export function getEmptyMessage(statusId: string): string {
  const hash = hashString(statusId)
  const index = hash % EMPTY_MESSAGES.length
  return EMPTY_MESSAGES[index]
}

export function useDisplayTone() {
  return {
    getStatusTone,
    getToneClasses,
    getEmptyMessage,
  }
}
