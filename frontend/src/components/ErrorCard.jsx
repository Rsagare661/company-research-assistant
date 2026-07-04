import { AlertTriangle } from 'lucide-react'

export default function ErrorCard({ message }) {
  return (
    <div className="mx-auto flex w-full max-w-3xl animate-rise items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/5 p-4">
      <AlertTriangle size={18} className="mt-0.5 shrink-0 text-red-400" />
      <div>
        <p className="text-sm font-semibold text-red-400">Research failed</p>
        <p className="mt-1 text-sm text-mist-300">{message}</p>
      </div>
    </div>
  )
}
