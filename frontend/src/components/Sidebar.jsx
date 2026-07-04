import { useState } from 'react'
import { Plus, Radar, KeyRound } from 'lucide-react'

export default function Sidebar({
  config, setConfig, models, onNewResearch, history, onSelectHistory, activeHistoryId,
}) {
  const [tab, setTab] = useState('api')
  const [saved, setSaved] = useState(false)
  const [discordSaved, setDiscordSaved] = useState(false)

  const update = (key, value) => setConfig((c) => ({ ...c, [key]: value }))

  const handleSaveApi = (e) => {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 1800)
  }

  const handleSaveDiscord = (e) => {
    e.preventDefault()
    setDiscordSaved(true)
    setTimeout(() => setDiscordSaved(false), 1800)
  }

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-ink-700 bg-ink-900 text-mist-100">
      <div className="flex items-center gap-2 border-b border-ink-700 px-5 py-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-signal/10 text-signal">
          <Radar size={18} strokeWidth={2.2} />
        </div>
        <div className="leading-tight">
          <p className="font-display text-sm font-semibold tracking-tight">Relu Consultancy</p>
          <p className="font-mono text-[10px] uppercase tracking-widest text-mist-500">Research Intelligence</p>
        </div>
      </div>

      <div className="px-4 pt-4">
        <button
          onClick={onNewResearch}
          className="focus-ring flex w-full items-center gap-2 rounded-lg border border-ink-600 px-3 py-2 text-sm text-mist-300 transition hover:border-signal/50 hover:text-signal"
        >
          <Plus size={15} /> New Research
        </button>
      </div>

      {history.length > 0 && (
        <div className="mt-3 max-h-40 overflow-y-auto px-4">
          <p className="mb-1 font-mono text-[10px] uppercase tracking-widest text-mist-500">Recent</p>
          <ul className="space-y-1">
            {history.map((h) => (
              <li key={h.id}>
                <button
                  onClick={() => onSelectHistory(h.id)}
                  className={`focus-ring w-full truncate rounded-md px-2 py-1.5 text-left text-xs transition ${
                    activeHistoryId === h.id
                      ? 'bg-signal/10 text-signal'
                      : 'text-mist-500 hover:bg-ink-800 hover:text-mist-300'
                  }`}
                >
                  {h.name}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 flex gap-1 px-4">
        <TabButton active={tab === 'api'} onClick={() => setTab('api')}>API</TabButton>
        <TabButton active={tab === 'discord'} onClick={() => setTab('discord')}>Discord</TabButton>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {tab === 'api' ? (
          <form onSubmit={handleSaveApi} className="space-y-4">
            <Field
              label="OpenRouter API Key"
              value={config.openrouterKey}
              onChange={(v) => update('openrouterKey', v)}
              placeholder="sk-or-v1-..."
              type="password"
            />
            <Field
              label="Serper.dev API Key"
              value={config.serperKey}
              onChange={(v) => update('serperKey', v)}
              placeholder="Your Serper key..."
              type="password"
            />
            <div>
              <label className="mb-1 block font-mono text-[10px] uppercase tracking-widest text-mist-500">
                AI Model
              </label>
              <select
                value={config.model}
                onChange={(e) => update('model', e.target.value)}
                className="focus-ring w-full rounded-md border border-ink-600 bg-ink-800 px-3 py-2 text-sm text-mist-100"
              >
                {models.map((m) => (
                  <option key={m.id} value={m.id}>{m.label}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              className="focus-ring w-full rounded-md bg-signal py-2 text-sm font-semibold text-ink-950 transition hover:bg-signal-soft"
            >
              {saved ? 'Saved ✓' : 'Save Configuration'}
            </button>

            <div className="pt-2">
              <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-mist-500">How it works</p>
              <ol className="space-y-1.5 text-xs text-mist-500">
                <li><span className="text-signal">1</span> &nbsp;Enter a company name or URL</li>
                <li><span className="text-signal">2</span> &nbsp;Serper.dev finds and maps the site</li>
                <li><span className="text-signal">3</span> &nbsp;OpenRouter AI synthesizes insights</li>
                <li><span className="text-signal">4</span> &nbsp;Download a professional PDF report</li>
              </ol>
            </div>
          </form>
        ) : (
          <form onSubmit={handleSaveDiscord} className="space-y-4">
            <div className="rounded-md border border-ink-600 bg-ink-800/60 p-3 text-xs text-mist-300">
              <p className="mb-1 flex items-center gap-1.5 font-semibold text-mist-100">
                <KeyRound size={13} className="text-signal" /> Discord Bot Integration
              </p>
              After research completes, the report auto-sends to your configured channel.
            </div>
            <Field
              label="Bot Token"
              value={config.discordToken}
              onChange={(v) => update('discordToken', v)}
              placeholder="Bot token..."
              type="password"
            />
            <Field
              label="Channel ID"
              value={config.discordChannel}
              onChange={(v) => update('discordChannel', v)}
              placeholder="000000000000000000"
            />
            <p className="pt-1 font-mono text-[10px] uppercase tracking-widest text-mist-500">Applicant Details</p>
            <Field
              label="Full Name"
              value={config.applicantName}
              onChange={(v) => update('applicantName', v)}
              placeholder="Your full name"
            />
            <Field
              label="Email Address"
              value={config.applicantEmail}
              onChange={(v) => update('applicantEmail', v)}
              placeholder="email@example.com"
            />
            <button
              type="submit"
              className="focus-ring w-full rounded-md bg-ink-600 py-2 text-sm font-semibold text-mist-100 transition hover:bg-ink-500"
            >
              {discordSaved ? 'Saved ✓' : 'Save Discord Config'}
            </button>
          </form>
        )}
      </div>
    </aside>
  )
}

function TabButton({ active, children, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`focus-ring flex-1 rounded-md py-1.5 font-mono text-[11px] uppercase tracking-widest transition ${
        active ? 'bg-ink-700 text-signal' : 'text-mist-500 hover:text-mist-300'
      }`}
    >
      {children}
    </button>
  )
}

function Field({ label, value, onChange, placeholder, type = 'text' }) {
  return (
    <div>
      <label className="mb-1 block font-mono text-[10px] uppercase tracking-widest text-mist-500">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="focus-ring w-full rounded-md border border-ink-600 bg-ink-800 px-3 py-2 text-sm text-mist-100 placeholder:text-mist-500"
      />
    </div>
  )
}
