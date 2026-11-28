import { useState } from 'react'
import { runTest } from '../api/client'
import type { RunRequest, RunResponse } from '../api/types'

/** The outcome of one run, remembered with the request that produced it. */
interface Outcome {
  key: string
  result: RunResponse | null
  error: string | null
}

/** Runs the test for the current request (null while an input is invalid). */
export function useTestRun(request: RunRequest | null) {
  const [outcome, setOutcome] = useState<Outcome | null>(null)
  const [running, setRunning] = useState(false)
  const key = JSON.stringify(request)
  // Show an outcome only while the settings still match it, so an old result is
  // never shown next to new settings.
  const current = outcome?.key === key ? outcome : null

  async function run() {
    if (!request || running) return
    setRunning(true)
    setOutcome(null)
    try {
      setOutcome({ key, result: await runTest(request), error: null })
    } catch (reason) {
      setOutcome({ key, result: null, error: (reason as Error).message })
    } finally {
      setRunning(false)
    }
  }

  return { result: current?.result ?? null, error: current?.error ?? null, running, run }
}
