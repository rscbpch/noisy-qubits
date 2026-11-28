// The algorithms and devices the site offers. Change the lists here.
import type { AlgorithmId, AlgorithmInfo, DeviceInfo } from '../api/types'

export const ALGORITHMS: AlgorithmInfo[] = [
  { id: 'superposition', label: 'Superposition / quantum randomness', minQubits: 2, maxQubits: 10 },
  { id: 'deutsch_jozsa', label: 'Deutsch-Jozsa', minQubits: 2, maxQubits: 10 },
  { id: 'qft', label: 'QFT', minQubits: 2, maxQubits: 10 },
  { id: 'qpe', label: 'Quantum Phase Estimation (QPE)', minQubits: 2, maxQubits: 10 },
  // Simon's uses half the qubits for input and half for output.
  { id: 'simon', label: "Simon's algorithm", minQubits: 2, maxQubits: 10 },
]

export const DEVICES: DeviceInfo[] = [
  { id: 'FakeGuadalupe', numQubits: 16 },
  { id: 'FakeKolkata', numQubits: 27 },
  { id: 'FakeMontreal', numQubits: 27 },
]

/** The one-line description under the algorithm menu. */
export const ALGORITHM_DESCRIPTIONS: Record<AlgorithmId, string> = {
  superposition: 'H on every qubit: all outcomes equally likely.',
  deutsch_jozsa: 'One oracle query tells constant from balanced.',
  qft: 'Quantum Fourier Transform, tested by undoing it.',
  qpe: 'Estimates the phase of a unitary.',
  simon: 'Finds a hidden XOR period.',
}

export function algorithmLabel(id: AlgorithmId): string {
  return ALGORITHMS.find((a) => a.id === id)?.label ?? id
}
