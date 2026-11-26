// Text for the About tab (Member 5). Plain data, so wording can change without touching the component.

export type AlgorithmId = 'superposition' | 'deutsch_jozsa' | 'qft' | 'qpe' | 'simon'

export interface AlgorithmAbout {
  title: string
  what: string
  noise: string
}

export const ALGORITHM_ABOUT: Record<AlgorithmId, AlgorithmAbout> = {
  superposition: {
    title: 'Superposition (control case)',
    what: 'A Hadamard gate on every qubit puts all 1024 outcomes in an equal mix. The score is how close the measured outcomes are to uniform, and the classical baseline is a random number generator.',
    noise: 'Gate noise leaves an even spread roughly even, so this algorithm should pass at almost every noise level. It is the control: if it fails, the noise setup is the problem, not the algorithm. Only errors that favour one value, such as T1 decay or a readout error that turns 1 into 0 more often than 0 into 1, can shift it.',
  },
  deutsch_jozsa: {
    title: 'Deutsch-Jozsa',
    what: 'Decides in one query whether a hidden function is constant or balanced. A noise-free run gives one definite answer, and the classical guess is right half the time.',
    noise: 'The circuit is short, so it should survive more noise than QFT or QPE. Errors show up as extra wrong outcomes spread over the other bitstrings, which lowers the chance of the correct answer.',
  },
  qft: {
    title: 'Quantum Fourier Transform',
    what: 'Turns a bitstring into a pattern of phases and back. We run the QFT followed by the inverse QFT and score how often the original input comes back, against a 1 in 1024 random guess.',
    noise: 'QFT works through interference, so phase-flip errors hurt it even though they never change a plain 0 or 1. It also uses many two-qubit gates, so it fails at a lower noise level than a short circuit. An approximate QFT that drops the smallest rotations uses fewer gates and may survive more noise.',
  },
  qpe: {
    title: 'Quantum Phase Estimation',
    what: 'Reads out a hidden phase as 9 bits using 9 counting qubits and one eigenstate qubit. The score is the chance of getting the correct phase bits, against a 1 in 512 guess.',
    noise: 'This is the deepest circuit in the project, with many controlled gates and a final inverse QFT, so it is expected to fail first and to gain the least from error mitigation.',
  },
  simon: {
    title: "Simon's algorithm",
    what: 'Finds a hidden secret string s using 5 input and 5 output qubits. Each run gives a string y that satisfies y . s = 0 (mod 2), and the score is the share of runs that do.',
    noise: 'A random answer already satisfies the rule half the time, so the pass line is raised to 75%. As noise grows, the result slides toward that 50% random level instead of toward zero.',
  },
}

export interface NoiseTypeAbout {
  name: string
  what: string
  zne: string
}

// "zne" is what zero-noise extrapolation did in our experiments (docs/noise-table.md).
export const NOISE_TYPES: NoiseTypeAbout[] = [
  { name: 'Depolarizing (main)', what: 'After a gate, the qubit is replaced by a random state with a small probability.', zne: 'Helps' },
  { name: 'Bit-flip', what: 'A qubit flips between 0 and 1, like an accidental X gate.', zne: 'Helps partly' },
  { name: 'Phase-flip', what: 'The qubit phase flips, like an accidental Z gate. It breaks interference.', zne: 'Helps partly' },
  { name: 'Amplitude damping (T1)', what: 'A qubit in 1 slowly falls to 0. Longer circuits give it more time to decay.', zne: 'Helps' },
  { name: 'Readout error', what: 'The qubit is fine but the final measurement reports the wrong value.', zne: 'No help' },
]
