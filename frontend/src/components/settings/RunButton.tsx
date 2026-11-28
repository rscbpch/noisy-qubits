import Button from '../ui/Button'
import './RunButton.css'

export default function RunButton({ running, disabled }: { running: boolean; disabled: boolean }) {
  return (
    <div className="run">
      <Button variant="primary" type="submit" disabled={disabled || running}>
        {running ? 'Running...' : 'Run test'}
      </Button>
      <div className={running ? 'progress progress-running' : 'progress'} aria-hidden="true"><i /></div>
    </div>
  )
}
