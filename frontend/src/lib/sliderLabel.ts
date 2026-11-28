// Live text next to the noise slider. The mapping belongs to Member 5: this
// mirrors slider_label() in src/noisy_qubits/noise/slider.py. Change both together.
import type { NoiseMode } from '../api/types'

const MAX_TWO_QUBIT_ERROR_PERCENT = 5
const DEVICE_REAL_SLIDER = 50

export function sliderLabel(mode: NoiseMode, slider: number): string {
  if (mode === 'uniform') {
    const percent = Number(((MAX_TWO_QUBIT_ERROR_PERCENT * slider) / 100).toFixed(2))
    return `Slider ${slider} means ${percent}% error per gate`
  }
  return `Slider ${slider} means ${slider / DEVICE_REAL_SLIDER}x the real device error rates`
}

/** The two lines in the box under the slider (wording from the sample UI). */
export function noiseDetails(slider: number, device: string | null): { value: string; rule: string } {
  if (device === null) {
    const twoQubit = (MAX_TWO_QUBIT_ERROR_PERCENT * slider) / 100
    return {
      value: `${twoQubit.toFixed(2)}% error per two-qubit gate (${(twoQubit / 10).toFixed(2)}% per single-qubit gate)`,
      rule: 'Uniform mode: 5% x slider / 100.',
    }
  }
  const real = slider === DEVICE_REAL_SLIDER ? ' (the real device)' : ''
  return {
    value: `x${(slider / DEVICE_REAL_SLIDER).toFixed(2)} of ${device}'s real error rates${real}`,
    rule: 'Device mode: calibrated rates x slider / 50.',
  }
}
