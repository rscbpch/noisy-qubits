// Everything the left panel holds. Typed inputs stay as text, so the user can
// type something invalid and see why it is rejected.
import type { AlgorithmId, DeviceId, NoiseType } from './api/types'

/** 'uniform' is the uniform noise mode; the rest are fake devices. */
export type TargetId = 'uniform' | DeviceId

/** Uniform noise counts as one of the choices. */
export const MAX_TARGETS = 3

export const targetLabel = (id: TargetId) => (id === 'uniform' ? 'Uniform noise' : id)

export type OracleChoice = 'constant-0' | 'constant-1' | 'balanced' | 'typed'

export interface Settings {
  algorithm: AlgorithmId
  nQubits: number
  qftInput: string
  qpeK: string
  djOracle: OracleChoice
  djTruthTable: string
  simonSecret: string
  /** At least one. The first one is shown in the main result. */
  targets: TargetId[]
  noiseType: NoiseType
  readoutError: boolean
  slider: number
  shots: string
  zne: boolean
}

const DEFAULT_QFT_STATE = '0110010110' // as in qft.py
const DEFAULT_QPE_PHASE = 160 / 512 // as in the sample UI
const DEFAULT_SECRET = '10110'

/** Simon's secret is half as long as the qubit count. */
export const secretLength = (nQubits: number) => Math.floor(nQubits / 2)

/** The typed inputs that depend on the qubit count. */
export function defaultInputs(nQubits: number): Pick<Settings, 'qftInput' | 'qpeK' | 'simonSecret'> {
  return {
    qftInput: DEFAULT_QFT_STATE.slice(-nQubits),
    qpeK: String(Math.floor(DEFAULT_QPE_PHASE * 2 ** (nQubits - 1))),
    simonSecret: DEFAULT_SECRET.slice(0, secretLength(nQubits)),
  }
}

export const INITIAL_SETTINGS: Settings = {
  algorithm: 'deutsch_jozsa',
  nQubits: 10,
  ...defaultInputs(10),
  djOracle: 'balanced',
  djTruthTable: '',
  targets: ['uniform', 'FakeGuadalupe'],
  noiseType: 'depolarizing',
  readoutError: false,
  slider: 30,
  shots: '1024',
  zne: false,
}
