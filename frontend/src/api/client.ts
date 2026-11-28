// The only place the website talks to the API.
// Fake data is used unless VITE_USE_MOCK=false (see frontend/.env.example).
import { ALGORITHMS, DEVICES } from '../data/algorithms'
import { mockRun } from './mock'
import type { AlgorithmInfo, DeviceInfo, RunRequest, RunResponse } from './types'

export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

async function request<T>(path: string, body?: unknown): Promise<T> {
  let response: Response
  try {
    response = await fetch(
      path,
      body === undefined
        ? undefined
        : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) },
    )
  } catch {
    throw new Error('Cannot reach the API. Is it running?')
  }
  if (!response.ok) {
    // The error format is still an open question (docs/api-contract.md).
    throw new Error(`The API returned an error (${response.status}).`)
  }
  return (await response.json()) as T
}

export function getAlgorithms(): Promise<AlgorithmInfo[]> {
  return USE_MOCK ? Promise.resolve(ALGORITHMS) : request('/api/algorithms')
}

export function getDevices(): Promise<DeviceInfo[]> {
  return USE_MOCK ? Promise.resolve(DEVICES) : request('/api/devices')
}

export function runTest(body: RunRequest): Promise<RunResponse> {
  return USE_MOCK ? mockRun(body) : request('/api/run', body)
}
