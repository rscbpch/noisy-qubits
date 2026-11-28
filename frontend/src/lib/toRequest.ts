import type { RunRequest } from '../api/types'
import type { Settings } from '../settings'
import { checkParams, checkShots } from './validation'

/** The request the settings describe, or null if an input is invalid. */
export function toRequest(settings: Settings): RunRequest | null {
  const checked = checkParams(settings)
  if (!checked.ok || checkShots(settings.shots)) return null
  const target = settings.targets[0]
  return {
    params: checked.params,
    // Noise type and readout error apply to uniform noise only.
    ...(target === 'uniform'
      ? { mode: 'uniform' as const, noiseType: settings.noiseType, readoutError: settings.readoutError }
      : { mode: 'device' as const, device: target, noiseType: 'depolarizing' as const, readoutError: false }),
    slider: settings.slider,
    shots: Number(settings.shots),
    zne: settings.zne,
  }
}
