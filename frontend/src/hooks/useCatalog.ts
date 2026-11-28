import { useEffect, useState } from 'react'
import { getAlgorithms, getDevices } from '../api/client'
import type { AlgorithmInfo, DeviceInfo } from '../api/types'

/** Loads the lists of algorithms and devices once. */
export function useCatalog() {
  const [algorithms, setAlgorithms] = useState<AlgorithmInfo[]>([])
  const [devices, setDevices] = useState<DeviceInfo[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([getAlgorithms(), getDevices()])
      .then(([algorithmList, deviceList]) => {
        setAlgorithms(algorithmList)
        setDevices(deviceList)
      })
      .catch((reason: Error) => setError(reason.message))
  }, [])

  return { algorithms, devices, error }
}
