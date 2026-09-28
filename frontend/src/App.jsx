import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  ExternalLink, 
  Terminal, 
  FileText, 
  MessageSquare, 
  Mail, 
  Briefcase, 
  Sparkles,
  RefreshCw,
  Search,
  Lock,
  Globe,
  Clock,
  Users,
  ChevronRight
} from 'lucide-react';

const SAMPLE_PRESETS = [
  {
    name: "🟢 Stripe (Legit ATS)",
    type: "job_posting",
    company: "Stripe",
    text: "Stripe is looking for a Senior Backend Engineer to join our Payment Infrastructure team in Seattle or Remote. Responsibilities: Design and build high-throughput payment APIs, improve latency. Requirements: 5+ years experience with distributed systems (Go/Ruby/Java). Apply directly on our Greenhouse job board: https://boards.greenhouse.io/stripe/jobs/5928172002. Contact: recruiting@stripe.com."
  },
  {
    name: "🟡 DevStudio (SMB)",
    type: "job_posting",
    company: "DevStudio",
    text: "DevStudio is a 10-person boutique design and web agency in Indiranagar, Bangalore. We are looking for a React/Next.js developer with 2 years of experience. We offer competitive CTC of 8-12 LPA. Send portfolio to hello@devstudio.in. No upfront fees."
  },
  {
    name: "🔴 UPI Laptop Fee (Scam)",
    type: "email_thread",
    company: "Tech Mahindra Impersonator",
    text: "Congratulations! You have been selected for the Data Analyst position at Tech Mahindra Global. Monthly salary is Rs 65,000. Before dispatching your company Apple MacBook Pro and ID card, you must deposit a refundable security caution fee of Rs 3,500 via Google Pay / PhonePe UPI to hr-techmahindra@okaxis. This amount will be refunded in your first salary slip."
  },
  {
    name: "🟠 Typosquat Lookalike",
    type: "email_thread",
    company: "Google",
    text: "Dear Candidate, Your resume has been shortlisted for Cloud Support at Google India. Please reply back with your CV and confirmation. Regards, Priya Sharma, HR Director at career@g00gle-careers.com."
  },
  {
    name: "🟣 Aadhaar PII Harvesting",
    type: "job_posting",
    company: "Apex Media",
    text: "Immediate opening for Remote Content Moderator. Easy work from home, Rs 40,000 per month. To apply and get registered in the system today, you must upload: 1) High-resolution front and back photo of your Aadhaar Card, 2) PAN Card copy, 3) Bank passbook canceled cheque with IFSC and account number, and 4) Current residential electricity bill. Verification OTP will be sent to your mobile."
  },
  {
    name: "🔵 35-Hr Unpaid Task",
    type: "job_posting",
    company: "CloudForge Labs",
    text: "We are hiring a Fullstack Lead. As round 1 of the interview, candidates are required to submit a complete multi-tenant SaaS CRM dashboard with real Stripe subscription billing, webhook listener, PostgreSQL database schema, OAuth login, and deploy it to AWS with Terraform. Estimated time: 35-40 hours. Candidates must grant our GitHub organization write access to review the code. Failure to complete all modules will result in immediate disqualification."
  },
  {
    name: "📉 Ghost Job (180 Days)",
    type: "job_posting",
    company: "Global Synergy Corp",
    text: "Enterprise Software Architect. Posted 185 days ago. 4,320 applicants already applied. General enterprise architecture requirements, continuously reposted every 3 weeks. No active hiring manager listed."
  },
  {
    name: "🌍 Overseas Visa Scam",
    type: "offer_letter",
    company: "Gulf Overseas Placements",
    text: "Offer of Employment for Dubai International Airport Security Assistant. Monthly tax-free salary 6,500 AED with free food and accommodation. Note: Candidate must immediately transfer Rs 45,000 to overseas agent account for Ministry of Labor clearance and medical certificate processing. No interview required, immediate flight departure."
  }
];

export default function App() {
  const [inputType, setInputType] = useState('job_posting');
  const [rawText, setRawText] = useState(SAMPLE_PRESETS[0].text);
  const [companyName, setCompanyName] = useState(SAMPLE_PRESETS[0].company);
  const [sourceUrl, setSourceUrl] = useState('');
  const [recruiterEmail, setRecruiterEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [backendHealth, setBackendHealth] = useState(null);

  // Check health on load
  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then(res => res.json())
      .then(data => setBackendHealth(data.status))
      .catch(() => setBackendHealth('offline'));
  }, []);

  const handleAnalyze = async () => {
    if (!rawText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: rawText,
          input_type: inputType,
          company_name: companyName || null,
          source_url: sourceUrl || null,
          recruiter_email: recruiterEmail || null
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Analysis request failed');
      }
      const data = await res.json();
      setReport(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to JobShield backend.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset) => {
    setInputType(preset.type);
    setRawText(preset.text);
    setCompanyName(preset.company);
    setSourceUrl('');
    setRecruiterEmail('');
  };

  const getVerdictStyles = (verdict) => {
    if (verdict === 'DO_NOT_PROCEED') {
      return {
        bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
        badge: 'bg-rose-500 text-white',
        ring: 'border-rose-500 text-rose-400'
      };
    }
    if (verdict === 'PROCEED_WITH_CAUTION') {
      return {
        bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
        badge: 'bg-amber-500 text-slate-950 font-bold',
        ring: 'border-amber-500 text-amber-400'
      };
    }
    return {
      bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
      badge: 'bg-emerald-500 text-white',
      ring: 'border-emerald-500 text-emerald-400'
    };
  };

  return (
    <div className="min-h-screen pb-16">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 sticky top-0 z-50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white shadow-lg shadow-cyan-500/20">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-white">JobShield <span className="text-cyan-400">AI</span></span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-300 font-mono">v1.0 MVP</span>
              </div>
              <p className="text-xs text-slate-400">Recruitment Integrity & Opportunity Trust Engine</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <span className={`w-2 h-2 rounded-full ${backendHealth === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span className="font-mono">API: {backendHealth === 'online' ? 'Online' : 'Offline'}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 pt-8 space-y-8">
        
        {/* Intro Banner */}
        <div className="glass-panel p-6 rounded-2xl border border-cyan-500/20 bg-gradient-to-r from-cyan-950/30 via-slate-900/60 to-indigo-950/30 relative overflow-hidden">
          <div className="max-w-3xl relative z-10">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
              Verify Before You Commit.
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              JobShield gathers independently verifiable evidence (RDAP domain age, official ATS confirmation, upfront payment demands, PII harvesting, and unpaid work scopes) to produce a transparent, evidence-cited trust score.
            </p>
          </div>
          <div className="absolute right-0 top-0 bottom-0 w-80 bg-gradient-to-l from-cyan-500/10 to-transparent pointer-events-none" />
        </div>

        {/* Quick Benchmark Presets */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              1-Click Benchmark Test Cases (From 30-Case Test Suite)
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
            {SAMPLE_PRESETS.map((preset, i) => (
              <button
                key={i}
                onClick={() => loadPreset(preset)}
                className="px-2.5 py-2 text-left rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/40 transition-all text-xs font-medium text-slate-300 hover:text-white truncate"
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>

        {/* Workspace Split Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Input Panel (Left Column) */}
          <div className="lg:col-span-6 space-y-4">
            <div className="glass-panel p-5 rounded-2xl space-y-4">
              
              {/* Input Type Tabs */}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
                  Input Format
                </label>
                <div className="grid grid-cols-4 gap-1 p-1 bg-slate-900/90 rounded-xl border border-slate-800 text-xs font-medium">
                  {[
                    { id: 'job_posting', label: 'Posting', icon: Briefcase },
                    { id: 'email_thread', label: 'Email', icon: Mail },
                    { id: 'chat_transcript', label: 'Chat', icon: MessageSquare },
                    { id: 'offer_letter', label: 'Offer', icon: FileText }
                  ].map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setInputType(tab.id)}
                      className={`flex items-center justify-center gap-1.5 py-2 rounded-lg transition-all ${
                        inputType === tab.id 
                          ? 'bg-cyan-500 text-white shadow-md' 
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <tab.icon className="w-3.5 h-3.5" />
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Paste Textarea */}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
                  Paste Recruitment Text, Email, or Chat Transcript
                </label>
                <textarea
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  rows={9}
                  placeholder="Paste the full job posting, recruiter email message, WhatsApp/Telegram chat, or assignment instructions here..."
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 font-mono transition-all"
                />
              </div>

              {/* Optional Metadata Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Company Name (Optional)</label>
                  <input
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="e.g. Stripe, Tech Mahindra"
                    className="w-full bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Job or ATS URL (Optional)</label>
                  <input
                    type="text"
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    placeholder="e.g. boards.greenhouse.io/stripe/jobs/..."
                    className="w-full bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  />
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={handleAnalyze}
                disabled={loading || !rawText.trim()}
                className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Domains, ATS & Risk Triggers...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Analyze Recruitment Opportunity</span>
                  </>
                )}
              </button>

              {error && (
                <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

            </div>
          </div>

          {/* Results Panel (Right Column) */}
          <div className="lg:col-span-6 space-y-4">
            {!report && !loading && (
              <div className="glass-panel p-12 rounded-2xl text-center space-y-4 border border-dashed border-slate-800">
                <div className="w-16 h-16 mx-auto rounded-full bg-slate-900 flex items-center justify-center text-slate-600">
                  <ShieldCheck className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-slate-300">Ready to Inspect Opportunity</h3>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                    Paste any job advertisement, recruiter inquiry, or chat transcript on the left or select a 1-click test preset above.
                  </p>
                </div>
              </div>
            )}

            {report && (
              <div className="space-y-4">
                
                {/* Score & Verdict Card */}
                {(() => {
                  const styles = getVerdictStyles(report.trust_score.verdict);
                  return (
                    <div className={`p-6 rounded-2xl border ${styles.bg} space-y-4 relative overflow-hidden`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <span className={`inline-block px-3 py-1 rounded-full text-xs uppercase tracking-wider font-bold mb-2 ${styles.badge}`}>
                            {report.trust_score.verdict.replace(/_/g, ' ')}
                          </span>
                          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                            {report.trust_score.tier}
                          </h2>
                          <p className="text-xs text-slate-300 mt-1">
                            Audited: {report.extracted_job.company_name || 'Organization'} | Request ID: {report.request_id}
                          </p>
                        </div>

                        {/* Circular Score Metric */}
                        <div className={`w-20 h-20 rounded-2xl border-2 flex flex-col items-center justify-center bg-slate-950/60 ${styles.ring}`}>
                          <span className="text-2xl font-black">{report.trust_score.final_score}</span>
                          <span className="text-[10px] uppercase font-mono tracking-wider opacity-75">/ 100</span>
                        </div>
                      </div>

                      {/* Evidence Narration */}
                      <div className="p-3.5 rounded-xl bg-slate-950/50 border border-white/5 text-xs text-slate-200 leading-relaxed">
                        <span className="font-semibold text-cyan-300">Audit Finding: </span>
                        {report.llm_narration}
                      </div>

                      {/* Legal disclaimer */}
                      <p className="text-[10px] text-slate-400 italic">
                        {report.disclaimer}
                      </p>
                    </div>
                  );
                })()}

                {/* Evidence Citation Table (Core Spec Requirement) */}
                <div className="glass-panel p-5 rounded-2xl space-y-3">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                    Evidence Breakdown & Risk Accounting
                  </h3>

                  {/* Penalties */}
                  {report.trust_score.penalties.length > 0 && (
                    <div className="space-y-2">
                      <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">
                        Risk Penalties Deducted
                      </span>
                      {report.trust_score.penalties.map((pen, idx) => (
                        <div key={idx} className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/20 text-xs space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-rose-300 flex items-center gap-1.5">
                              <XCircle className="w-3.5 h-3.5 text-rose-400" />
                              {pen.signal_name}
                            </span>
                            <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono font-bold">
                              -{pen.penalty_points} pts
                            </span>
                          </div>
                          <p className="text-slate-300 text-[11px] font-mono pl-5">
                            "{pen.trigger_text}"
                          </p>
                          <p className="text-slate-400 text-[11px] pl-5 italic">
                            Evidence: {pen.evidence_citation}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Bonuses */}
                  {report.trust_score.bonuses.length > 0 && (
                    <div className="space-y-2 pt-2">
                      <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">
                        Verification Bonuses Awarded
                      </span>
                      {report.trust_score.bonuses.map((bon, idx) => (
                        <div key={idx} className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-xs space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-emerald-300 flex items-center gap-1.5">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                              {bon.signal_name}
                            </span>
                            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold">
                              +{bon.bonus_points} pts
                            </span>
                          </div>
                          <p className="text-slate-400 text-[11px] pl-5 italic">
                            Evidence: {bon.evidence_citation}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {report.trust_score.penalties.length === 0 && report.trust_score.bonuses.length === 0 && (
                    <p className="text-xs text-slate-400 italic">
                      Zero penalty or bonus triggers logged. Base score maintained.
                    </p>
                  )}
                </div>

                {/* Technical Infrastructure (RDAP & DNS) */}
                {report.domain_report && (
                  <div className="glass-panel p-5 rounded-2xl space-y-3">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <Globe className="w-3.5 h-3.5 text-cyan-400" />
                      Domain & Infrastructure Telemetry (RDAP / DNS)
                    </h3>
                    
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                      <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-500 block">Domain</span>
                        <span className="font-mono text-slate-200 truncate block">{report.domain_report.domain}</span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-500 block">Domain Age</span>
                        <span className="font-mono text-slate-200">
                          {report.domain_report.domain_age_days ? `${report.domain_report.domain_age_days} days` : 'Unknown'}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-500 block">DNS MX Status</span>
                        <span className="font-mono text-slate-200">
                          {report.domain_report.has_mx_records ? '✅ Valid' : '⚠️ None'}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-500 block">Typosquatted</span>
                        <span className="font-mono text-slate-200">
                          {report.domain_report.is_typosquatted ? '🔴 Yes' : '🟢 Clean'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Candidate Action Recommendations */}
                {report.recommended_actions.length > 0 && (
                  <div className="glass-panel p-5 rounded-2xl space-y-3">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                      Recommended Next Steps for Candidate
                    </h3>
                    <ul className="space-y-2 text-xs text-slate-300">
                      {report.recommended_actions.map((act, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <ChevronRight className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

              </div>
            )}

          </div>

        </div>

      </main>
    </div>
  );
}
