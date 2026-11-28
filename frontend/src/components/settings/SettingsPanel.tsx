// The left panel. Each control is its own component: move the lines below to
// change their order.
import type { FormEvent } from 'react'
import type { AlgorithmInfo, DeviceInfo } from '../../api/types'
import { checkParams, checkShots } from '../../lib/validation'
import Card from '../ui/Card'
import AlgorithmInputs from './AlgorithmInputs'
import AlgorithmSelect from './AlgorithmSelect'
import DeviceChips from './DeviceChips'
import ErrorHandlingControls from './ErrorHandlingControls'
import NoiseSlider from './NoiseSlider'
import NoiseTypeControls from './NoiseTypeControls'
import QubitSlider from './QubitSlider'
import RunButton from './RunButton'
import ShotsInput from './ShotsInput'
import type { ControlProps } from './types'
import './SettingsPanel.css'

interface Props extends ControlProps {
  algorithms: AlgorithmInfo[]
  devices: DeviceInfo[]
  running: boolean
  onRun: () => void
}

export default function SettingsPanel({ settings, onChange, algorithms, devices, running, onRun }: Props) {
  const checked = checkParams(settings)
  const inputError = checked.ok ? null : checked.message
  const shotsError = checkShots(settings.shots)
  const controls = { settings, onChange }

  function submit(event: FormEvent) {
    event.preventDefault()
    onRun()
  }

  return (
    <Card>
      <form onSubmit={submit} noValidate>
        <h2 className="settings-title">Test setup</h2>
        <AlgorithmSelect {...controls} algorithms={algorithms} />
        <QubitSlider {...controls} algorithm={algorithms.find((a) => a.id === settings.algorithm)} />
        <AlgorithmInputs {...controls} />
        {inputError && <p className="error" role="alert">{inputError}</p>}
        <DeviceChips {...controls} devices={devices} />
        <NoiseSlider {...controls} />
        <NoiseTypeControls {...controls} />
        <ShotsInput {...controls} />
        {shotsError && <p className="error" role="alert">{shotsError}</p>}
        <ErrorHandlingControls {...controls} />
        <RunButton running={running} disabled={!!inputError || !!shotsError} />
      </form>
    </Card>
  )
}
