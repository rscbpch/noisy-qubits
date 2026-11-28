// DRAFT API data contract (Member 2 proposal). Not final until Member 1 agrees.
// Notes and open questions: docs/api-contract.md

import type { AlgorithmId } from '../data/aboutContent'

export type { AlgorithmId }

export type DeviceId = 'FakeGuadalupe' | 'FakeKolkata' | 'FakeMontreal'
export type NoiseMode = 'uniform' | 'device'
export type NoiseType = 'depolarizing' | 'bit_flip' | 'phase_flip' | 'amplitude_damping'
export type Verdict = 'PASS' | 'RECOVERED' | 'FAIL'

// ---------- Circuit ----------

export type GateName =
  | 'h' | 'x' | 'y' | 'z' | 's' | 't'
  | 'rx' | 'ry' | 'rz'
  | 'cx' | 'cz' | 'swap' | 'cp' | 'ccx'
  | 'measure' | 'barrier'

export interface CircuitOp {
  name: GateName
  /** Qiskit argument order: controls first, target last. */
  qubits: number[]
  /** Angle in radians. Present only for rx, ry, rz and cp. */
  angle?: number
  /** Classical bit index. Present only for measure. */
  clbit?: number
}

export interface Circuit {
  numQubits: number
  ops: CircuitOp[]
}

/** The typed inputs of one algorithm. */
export type AlgorithmParams =
  | { algorithm: 'superposition'; nQubits: number }
  | { algorithm: 'deutsch_jozsa'; nQubits: number; oracle: 'constant-0' | 'constant-1' | 'balanced'; truthTable?: string }
  | { algorithm: 'qft'; nQubits: number; inputState: string }
  /** nQubits - 1 counting qubits. The phase is k / 2^(nQubits - 1); k / 512 at 10 qubits. */
  | { algorithm: 'qpe'; nQubits: number; phaseK: number }
  | { algorithm: 'simon'; secret: string }

// ---------- GET /api/algorithms, GET /api/devices ----------

export interface AlgorithmInfo {
  id: AlgorithmId
  label: string
  minQubits: number
  maxQubits: number
}

export interface DeviceInfo {
  id: DeviceId
  numQubits: number
}

// ---------- POST /api/run ----------

export interface RunRequest {
  params: AlgorithmParams
  mode: NoiseMode
  /** Required when mode is 'device'. One device per request. */
  device?: DeviceId
  noiseType: NoiseType
  /** Uniform mode only: also add readout error. The amount is not decided yet. */
  readoutError: boolean
  /** Whole number from 1 to 100. */
  slider: number
  shots: number
  zne: boolean
}

export interface ZneData {
  factors: number[]
  scores: number[]
  raw: number
  mitigated: number
  method: 'exponential' | 'linear' | 'richardson'
  /** [noise factor, score] points. */
  curve: [number, number][]
  /** When false, the verdict must not be RECOVERED. */
  reliable: boolean
}

export interface QubitProbability {
  qubit: number
  /** Chance that the qubit reads 1. */
  ideal: number
  noisy: number
}

export interface RunResponse {
  circuit: Circuit
  /** Example: "Slider 40 means 2% error per gate". */
  sliderLabel: string
  shots: number
  counts: Record<string, number>
  idealScore: number
  score: number
  baseline: number
  passLine: number
  verdict: Verdict
  /** null when ZNE is off or was not needed. */
  mitigation: ZneData | null
  perQubit: QubitProbability[]
  // bloch and stateVector: Member 3 to define.
}

// ---------- POST /api/circuit/validate ----------

export type ValidateRequest =
  | { format: 'gates'; text: string; numQubits: number }
  | { format: 'qasm'; text: string }

export interface ValidationError {
  /** 1-based line number; null if the error is not tied to one line. */
  line: number | null
  message: string
}

export type ValidateResponse =
  | { ok: true; circuit: Circuit }
  | { ok: false; errors: ValidationError[] }

// ---------- POST /api/qasm ----------

export interface QasmRequest {
  params: AlgorithmParams
}

export interface QasmResponse {
  /** OpenQASM 2.0, exported before transpiling. */
  qasm: string
}
