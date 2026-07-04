const EXAMPLES = ['stripe.com', 'Tesla', 'Microsoft', 'OpenAI']

export default function Hero({ onPick }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 text-center animate-rise">
      <p className="mb-3 font-mono text-xs uppercase tracking-[0.2em] text-signal">
        AI-Powered Intelligence
      </p>
      <h1 className="font-display max-w-2xl text-4xl font-semibold leading-tight text-mist-100 sm:text-5xl">
        Know any company<br />in minutes.
      </h1>
      <p className="mt-4 max-w-md text-sm text-mist-500 sm:text-base">
        Enter a company name or website URL to get AI-powered insights, competitor
        analysis, pain points, and a professional PDF report.
      </p>

      <div className="mt-7 flex flex-wrap justify-center gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => onPick(ex)}
            className="focus-ring rounded-full border border-ink-600 px-3.5 py-1.5 font-mono text-xs text-mist-300 transition hover:border-signal/60 hover:text-signal"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  )
}
