import type { Settings } from '../../settings'

/** What a settings control needs: the current values and a way to change them. */
export interface ControlProps {
  settings: Settings
  onChange: (changes: Partial<Settings>) => void
}
