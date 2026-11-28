// Connects the settings, the test run and the page areas. It has no styling or
// markup of its own.
import { useState } from 'react'
import { USE_MOCK } from './api/client'
import CompareSection from './components/compare/CompareSection'
import Header from './components/layout/Header'
import PageLayout from './components/layout/PageLayout'
import SettingsPanel from './components/settings/SettingsPanel'
import Card from './components/ui/Card'
import Tabs from './components/ui/Tabs'
import { useCatalog } from './hooks/useCatalog'
import { useTestRun } from './hooks/useTestRun'
import { toRequest } from './lib/toRequest'
import { INITIAL_SETTINGS, type Settings } from './settings'
import { TABS, type TabId } from './tabs'

export default function App() {
  const [settings, setSettings] = useState<Settings>(INITIAL_SETTINGS)
  const [tabId, setTabId] = useState<TabId>('results')
  const { algorithms, devices, error: loadError } = useCatalog()
  const request = toRequest(settings)
  const test = useTestRun(request)
  const tab = TABS.find((t) => t.id === tabId) ?? TABS[0]

  function run() {
    setTabId('results')
    test.run()
  }

  return (
    <PageLayout
      header={<Header sampleData={USE_MOCK} />}
      sidebar={
        <SettingsPanel
          settings={settings}
          onChange={(changes) => setSettings((previous) => ({ ...previous, ...changes }))}
          algorithms={algorithms}
          devices={devices}
          running={test.running}
          onRun={run}
        />
      }
      main={
        <Card>
          <Tabs tabs={TABS} active={tab.id} onSelect={setTabId} />
          {loadError && <p className="error" role="alert">{loadError}</p>}
          {tab.render({
            algorithm: settings.algorithm,
            request,
            result: test.result,
            error: test.error,
            running: test.running,
          })}
        </Card>
      }
      below={<CompareSection />}
    />
  )
}
