import { noiseDetails } from '../../lib/sliderLabel'
import Field from '../ui/Field'
import type { ControlProps } from './types'
import './NoiseSlider.css'

export default function NoiseSlider({ settings, onChange }: ControlProps) {
  // Describes the main result, which uses the first selected device.
  const target = settings.targets[0]
  const details = noiseDetails(settings.slider, target === 'uniform' ? null : target)

  return (
    <>
      <Field label={`Noise level: ${settings.slider} / 100`}>
        <input type="range" min={1} max={100} step={1} value={settings.slider}
          onChange={(e) => onChange({ slider: Number(e.target.value) })} />
      </Field>
      <div className="slider-scale" aria-hidden="true">
        <span>1</span><span>50 = real device</span><span>100</span>
      </div>
      <div className="noise-value">
        Slider {settings.slider} means <b>{details.value}</b>
        <span>{details.rule} Same scale for every algorithm.</span>
      </div>
    </>
  )
}
