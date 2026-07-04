import { useEffect, useRef, useState } from 'react'
import Sidebar from './components/Sidebar'
import Hero from './components/Hero'
import ChatInput from './components/ChatInput'
import ProgressTracker, { STEPS } from './components/ProgressTracker'
import CompanyReport from './components/CompanyReport'
import ErrorCard from './components/ErrorCard'
import { fetchModels, researchCompany } from './api/client'
import { Radar } from 'lucide-react'

export default function App() {
  const [models, setModels] = useState([{ id: 'anthropic/claude-sonnet-4.5', label: 'Claude Sonnet 4.5' }])
  const [config, setConfig] = useState({
    openrouterKey: '',
    serperKey: '',
    model: 'anthropic/claude-sonnet-4.5',
    discordToken: '',
    discordChannel: '',
    applicantName: '',
    applicantEmail: '',
  })

  const [turns, setTurns] = useState([]) // {id, query, status: loading|done|error, stepIndex, report, pdfBase64, discordSent, error}
  const [history, setHistory] = useState([])
  const [activeHistoryId, setActiveHistoryId] = useState(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    fetchModels().then(setModels).catch(() => {})
  }, [])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [turns])

  const keysConfigured = config.openrouterKey.trim() && config.serperKey.trim()

  const runResearch = async (query) => {
    if (!keysConfigured) {
      const id = crypto.randomUUID()
      setTurns((t) => [...t, {
        id, query, status: 'error',
        error: 'Add your OpenRouter and Serper.dev API keys in the sidebar to get started.',
      }])
      return
    }

    const id = crypto.randomUUID()
    setTurns((t) => [...t, { id, query, status: 'loading', stepIndex: 0 }])
    setHistory((h) => [{ id, name: query }, ...h].slice(0, 20))
    setActiveHistoryId(id)

    // Simulate step progression while the single backend call is in flight.
    let step = 0
    const interval = setInterval(() => {
      step = Math.min(step + 1, STEPS.length - 1)
      setTurns((t) => t.map((turn) => (turn.id === id ? { ...turn, stepIndex: step } : turn)))
    }, 1400)

    try {
      const payload = {
        query,
        openrouter_api_key: config.openrouterKey,
        serper_api_key: config.serperKey,
        ai_model: config.model,
        discord_bot_token: config.discordToken || null,
        discord_channel_id: config.discordChannel || null,
        applicant_name: config.applicantName || null,
        applicant_email: config.applicantEmail || null,
      }
      const data = await researchCompany(payload)
      clearInterval(interval)
      setTurns((t) => t.map((turn) => (turn.id === id ? {
        ...turn,
        status: 'done',
        report: data.report,
        pdfBase64: data.pdf_base64,
        discordSent: data.discord_sent,
      } : turn)))
    } catch (err) {
      clearInterval(interval)
      setTurns((t) => t.map((turn) => (turn.id === id ? { ...turn, status: 'error', error: err.message } : turn)))
    }
  }

  const handleNewResearch = () => {
    setTurns([])
    setActiveHistoryId(null)
  }

  const handleSelectHistory = (id) => {
    setActiveHistoryId(id)
    // In this single-session build, history just scrolls back to that turn if present.
    const el = document.getElementById(`turn-${id}`)
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="flex h-screen bg-ink-950 text-mist-100">
      <Sidebar
        config={config}
        setConfig={setConfig}
        models={models}
        onNewResearch={handleNewResearch}
        history={history}
        onSelectHistory={handleSelectHistory}
        activeHistoryId={activeHistoryId}
      />

      <main className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-ink-700 px-6 py-3">
          <div className="flex items-center gap-2">
            <Radar size={16} className="text-signal" />
            <span className="font-display text-sm font-semibold">Company Research</span>
          </div>
          <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-emerald-400">
            <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-emerald-400" /> Live
          </span>
        </header>

        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          {turns.length === 0 ? (
            <Hero onPick={runResearch} />
          ) : (
            <div className="space-y-8 px-4 py-8 sm:px-6">
              {turns.map((turn) => (
                <div key={turn.id} id={`turn-${turn.id}`} className="space-y-4">
                  <div className="mx-auto flex max-w-3xl items-center gap-2">
                    <span className="rounded-lg bg-ink-800 px-3 py-1.5 text-sm text-mist-300">{turn.query}</span>
                  </div>
                  {turn.status === 'loading' && <ProgressTracker currentStepIndex={turn.stepIndex} query={turn.query} />}
                  {turn.status === 'error' && <ErrorCard message={turn.error} />}
                  {turn.status === 'done' && (
                    <CompanyReport report={turn.report} pdfBase64={turn.pdfBase64} discordSent={turn.discordSent} />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <ChatInput
          onSubmit={runResearch}
          loading={turns.some((t) => t.status === 'loading')}
          disabledReason={!keysConfigured ? 'Configure API keys in the sidebar to get started' : ''}
        />
      </main>
    </div>
  )
}
