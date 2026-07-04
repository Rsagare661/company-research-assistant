import { useState } from 'react'
import { ArrowRight, Loader2 } from 'lucide-react'

export default function ChatInput({ onSubmit, loading, value, setValue, disabledReason }) {
  const [local, setLocal] = useState(value || '')

  const submit = () => {
    const q = local.trim()
    if (!q || loading) return
    onSubmit(q)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="border-t border-ink-700 bg-ink-900 px-4 py-4 sm:px-6">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-xl border border-ink-600 bg-ink-800 p-2 shadow-glow focus-within:border-signal/60">
        <textarea
          rows={1}
          value={local}
          onChange={(e) => { setLocal(e.target.value); setValue?.(e.target.value) }}
          onKeyDown={handleKeyDown}
          placeholder="Enter a company name (e.g. Aurora Labs) or website URL (e.g. https://aurora.dev)..."
          className="focus-ring max-h-32 flex-1 resize-none rounded-lg bg-transparent px-3 py-2 text-sm text-mist-100 placeholder:text-mist-500"
        />
        <button
          onClick={submit}
          disabled={loading || !local.trim()}
          className="focus-ring flex h-9 items-center gap-1.5 rounded-lg bg-signal px-3.5 text-sm font-semibold text-ink-950 transition hover:bg-signal-soft disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? <Loader2 size={15} className="animate-spin" /> : <>Research <ArrowRight size={14} /></>}
        </button>
      </div>
      <p className="mx-auto mt-2 max-w-3xl text-center font-mono text-[10px] uppercase tracking-widest text-mist-500">
        {disabledReason ? disabledReason : 'Enter to research · Shift+Enter for new line'}
      </p>
    </div>
  )
}
