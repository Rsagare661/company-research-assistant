import { Download, CheckCircle2, ExternalLink, Send } from 'lucide-react'

export default function CompanyReport({ report, pdfBase64, discordSent }) {
  const downloadPdf = () => {
    if (!pdfBase64) return
    const byteChars = atob(pdfBase64)
    const byteNumbers = new Array(byteChars.length)
    for (let i = 0; i < byteChars.length; i++) byteNumbers[i] = byteChars.charCodeAt(i)
    const blob = new Blob([new Uint8Array(byteNumbers)], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${report.company_name.toLowerCase().replace(/\s+/g, '-')}-research-report.pdf`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="mx-auto w-full max-w-3xl animate-rise rounded-xl border border-ink-700 bg-ink-800/60 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-semibold text-mist-100">{report.company_name}</h2>
          {report.website && (
            <a
              href={report.website}
              target="_blank"
              rel="noreferrer"
              className="focus-ring mt-0.5 inline-flex items-center gap-1 font-mono text-xs text-signal hover:underline"
            >
              {report.website} <ExternalLink size={11} />
            </a>
          )}
        </div>
        <span className="flex shrink-0 items-center gap-1.5 rounded-full border border-signal/40 bg-signal/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest text-signal">
          <CheckCircle2 size={12} /> Research Complete
        </span>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-4 border-y border-ink-700 py-4 sm:grid-cols-2">
        <MetaField label="Phone" value={report.phone || 'Not publicly listed'} />
        <MetaField label="Address" value={report.address || 'Not publicly listed'} />
      </div>

      <p className="mt-5 text-sm leading-relaxed text-mist-300">{report.summary}</p>

      {report.products_services?.length > 0 && (
        <Section title="Products & Services">
          <div className="flex flex-wrap gap-2">
            {report.products_services.map((p, i) => (
              <span key={i} className="rounded-md border border-ink-600 bg-ink-800 px-2.5 py-1 text-xs text-mist-100">
                {p}
              </span>
            ))}
          </div>
        </Section>
      )}

      {report.pain_points?.length > 0 && (
        <Section title="AI-Generated Pain Points">
          <ul className="space-y-2">
            {report.pain_points.map((p, i) => (
              <li key={i} className="flex gap-2 text-sm leading-relaxed text-mist-300">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal" /> {p}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {report.additional_insights?.length > 0 && (
        <Section title="Additional Insights">
          <ul className="space-y-2">
            {report.additional_insights.map((p, i) => (
              <li key={i} className="flex gap-2 text-sm leading-relaxed text-mist-300">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-mist-500" /> {p}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {report.competitors?.length > 0 && (
        <Section title="Competitors">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {report.competitors.map((c, i) => (
              <div key={i} className="rounded-md border border-ink-600 bg-ink-800 p-3">
                <p className="text-sm font-semibold text-mist-100">{c.name}</p>
                {c.website && (
                  <a href={c.website.startsWith('http') ? c.website : `https://${c.website}`} target="_blank" rel="noreferrer" className="focus-ring font-mono text-xs text-signal hover:underline break-all">
                    {c.website}
                  </a>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {report.sources?.length > 0 && (
        <Section title={`Sources (${report.pages_crawled} pages crawled)`}>
          <ul className="space-y-1">
            {report.sources.slice(0, 8).map((s, i) => (
              <li key={i} className="truncate font-mono text-[11px] text-mist-500">
                <a href={s.url} target="_blank" rel="noreferrer" className="focus-ring hover:text-signal">{s.url}</a>
              </li>
            ))}
          </ul>
        </Section>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          onClick={downloadPdf}
          className="focus-ring flex items-center gap-2 rounded-lg bg-signal px-4 py-2 text-sm font-semibold text-ink-950 transition hover:bg-signal-soft"
        >
          <Download size={15} /> Download PDF Report
        </button>
        {discordSent && (
          <span className="flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-400">
            <Send size={13} /> Sent to Discord
          </span>
        )}
      </div>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div className="mt-5">
      <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-signal">{title}</p>
      {children}
    </div>
  )
}

function MetaField({ label, value }) {
  return (
    <div>
      <p className="font-mono text-[10px] uppercase tracking-widest text-mist-500">{label}</p>
      <p className="mt-0.5 text-sm text-mist-100">{value}</p>
    </div>
  )
}
