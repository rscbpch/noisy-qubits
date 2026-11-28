// Browser-side input checks (project description, Section 13.2). The API checks
// again; these only give a fast message. Keep them in step with the Python code.
import type { AlgorithmParams } from '../api/types'
import { secretLength, type Settings } from '../settings'

// Proposed range from the sample UI; the description only gives the default.
export const MIN_SHOTS = 100
export const MAX_SHOTS = 8192

export type Checked =
  | { ok: true; params: AlgorithmParams }
  | { ok: false; message: string }

const fail = (message: string): Checked => ({ ok: false, message })
const pass = (params: AlgorithmParams): Checked => ({ ok: true, params })
const isBits = (text: string) => /^[01]+$/.test(text)
const isWhole = (text: string) => /^\d+$/.test(text)

export function checkParams(s: Settings): Checked {
  const { algorithm, nQubits } = s
  switch (algorithm) {
    case 'superposition':
      return pass({ algorithm, nQubits })

    case 'qft':
      if (s.qftInput.length !== nQubits || !isBits(s.qftInput)) {
        return fail(`Input state must be exactly ${nQubits} characters, using only 0 and 1.`)
      }
      return pass({ algorithm, nQubits, inputState: s.qftInput })

    case 'qpe': {
      const size = 2 ** (nQubits - 1)
      if (!isWhole(s.qpeK) || Number(s.qpeK) >= size) {
        return fail(`The phase is k/${size}, where k is a whole number from 0 to ${size - 1}.`)
      }
      return pass({ algorithm, nQubits, phaseK: Number(s.qpeK) })
    }

    case 'deutsch_jozsa': {
      if (s.djOracle !== 'typed') return pass({ algorithm, nQubits, oracle: s.djOracle })
      const length = 2 ** (nQubits - 1)
      const table = s.djTruthTable
      if (table.length !== length || !isBits(table)) {
        return fail(`Truth table needs exactly ${length} characters, using only 0 and 1.`)
      }
      const ones = table.split('1').length - 1
      if (ones !== 0 && ones !== length && ones !== length / 2) {
        return fail('The function must be constant (all 0 or all 1) or balanced (half are 1).')
      }
      // The Python code ignores "oracle" when a truth table is given.
      return pass({ algorithm, nQubits, oracle: 'balanced', truthTable: table })
    }

    case 'simon': {
      const secret = s.simonSecret
      const length = secretLength(nQubits)
      if (secret.length !== length || !isBits(secret)) {
        return fail(`Secret must be exactly ${length} bits of 0 or 1.`)
      }
      if (!secret.includes('1')) return fail('Secret must not be all zeros.')
      return pass({ algorithm, secret })
    }
  }
}

export function checkShots(text: string): string | null {
  const shots = Number(text)
  return isWhole(text) && shots >= MIN_SHOTS && shots <= MAX_SHOTS
    ? null
    : `Shots must be a whole number from ${MIN_SHOTS} to ${MAX_SHOTS}.`
}
