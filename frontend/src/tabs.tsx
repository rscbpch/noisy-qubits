// Every tab, in display order. To add, remove or reorder a tab, edit this list.
import type { ReactNode } from 'react'
import type { AlgorithmId } from './api/types'
import AboutPanel from './components/about/AboutPanel'
import ResultsTab, { type ResultsTabProps } from './components/results/ResultsTab'
import Placeholder from './components/ui/Placeholder'

/** What a tab may use to draw itself. */
export interface TabContext extends ResultsTabProps {
  algorithm: AlgorithmId
}

interface Tab {
  id: string
  label: string
  render: (context: TabContext) => ReactNode
}

export const TABS = [
  { id: 'results', label: 'Circuit & results', render: (c) => <ResultsTab {...c} /> },
  { id: 'mitigation', label: 'Error mitigation', render: () => <Placeholder title="Error mitigation (ZNE)" owner="Member 5" /> },
  { id: 'qasm', label: 'QASM & import', render: () => <Placeholder title="QASM export, gate box and import" owner="Member 2, later step" /> },
  { id: 'bloch', label: 'Bloch sphere', render: () => <Placeholder title="Bloch sphere" owner="Member 3" /> },
  { id: 'statevector', label: 'State vector', render: () => <Placeholder title="State vector" owner="Member 3" /> },
  { id: 'devices', label: 'Devices', render: () => <Placeholder title="Device comparison" owner="Member 4" /> },
  { id: 'about', label: 'About', render: (c) => <AboutPanel algorithm={c.algorithm} /> },
] as const satisfies readonly Tab[]

export type TabId = (typeof TABS)[number]['id']
