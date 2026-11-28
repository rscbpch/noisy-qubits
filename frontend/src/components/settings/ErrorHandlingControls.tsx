// Minimal ZNE switch so the shell is complete. Member 5 owns this component.
import CheckField from '../ui/CheckField'
import type { ControlProps } from './types'

export default function ErrorHandlingControls({ settings, onChange }: ControlProps) {
  return (
    <>
      <h2 className="settings-title settings-title-split">Error handling</h2>
      <CheckField label="Zero-noise extrapolation (ZNE)" checked={settings.zne}
        onChange={(zne) => onChange({ zne })} />
      <span className="hint">
        Leave it off for the first run. If the test fails, turn it on and run again at the same
        noise. Costs about 3 times the runs.
      </span>
    </>
  )
}
