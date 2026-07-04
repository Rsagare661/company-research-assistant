import { Check, Loader2 } from 'lucide-react'

const STEPS = [
  { key: 'resolve', label: 'Resolving official website' },
  { key: 'crawl', label: 'Crawling key pages' },
  { key: 'enrich', label: 'Searching for context & competitors' },
  { key: 'ai', label: 'Synthesizing insights with AI' },
  { key: 'pdf', label: 'Generating PDF report' },
]

export default function ProgressTracker({ currentStepIndex, query }) {
  return (
    <div className="mx-auto w-full max-w-xl animate-rise rounded-xl border border-ink-700 bg-ink-800/60 p-5">
      <div className="mb-4 flex items-center gap-2">
        <span className="h-2 w-2 animate-pulse-dot rounded-full bg-signal" />
        <p className="font-mono text-xs uppercase tracking-widest text-signal">
          Researching {query}
        </p>
      </div>
      <ol className="space-y-3">
        {STEPS.map((step, i) => {
          const state = i < currentStepIndex ? 'done' : i === currentStepIndex ? 'active' : 'pending'
          return (
            <li key={step.key} className="flex items-center gap-3 text-sm">
              <span
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[10px] ${
                  state === 'done'
                    ? 'border-signal bg-signal text-ink-950'
                    : state === 'active'
                    ? 'border-signal text-signal'
                    : 'border-ink-600 text-mist-500'
                }`}
              >
                {state === 'done' ? <Check size={12} /> : state === 'active' ? <Loader2 size={11} className="animate-spin" /> : i + 1}
              </span>
              <span className={state === 'pending' ? 'text-mist-500' : 'text-mist-100'}>{step.label}</span>
            </li>
          )
        })}
      </ol>
    </div>
  )
}

export { STEPS }
