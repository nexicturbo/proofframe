"use client";

import { useMemo, useState } from "react";

type RunState = "ready" | "running" | "verified";

const candidates = [
  {
    id: "01",
    score: 74,
    status: "rejected",
    note: "Headline contrast below 4.5:1",
    cost: "$0.018",
    time: "8.4s",
    tone: "violet",
  },
  {
    id: "02",
    score: 86,
    status: "refined",
    note: "Logo safe-zone clipped by 6px",
    cost: "$0.019",
    time: "8.1s",
    tone: "coral",
  },
  {
    id: "03",
    score: 96,
    status: "accepted",
    note: "All policy checks passed",
    cost: "$0.020",
    time: "7.8s",
    tone: "mint",
  },
];

const trace = [
  {
    index: "01",
    label: "Generate",
    detail: "genblaze / image-v3",
    meta: "seed 48122",
  },
  {
    index: "02",
    label: "Evaluate",
    detail: "brand-policy.json",
    meta: "6 checks",
  },
  {
    index: "03",
    label: "Refine",
    detail: "feedback → prompt",
    meta: "2 retries",
  },
  {
    index: "04",
    label: "Commit",
    detail: "Backblaze B2",
    meta: "sha256",
  },
];

const checks = [
  ["Typography legibility", "100", "pass"],
  ["Brand palette match", "98", "pass"],
  ["Safe-zone compliance", "96", "pass"],
  ["Required object present", "94", "pass"],
  ["Prompt fidelity", "92", "pass"],
  ["Content safety", "100", "pass"],
];

export default function Home() {
  const [runState, setRunState] = useState<RunState>("verified");
  const [prompt, setPrompt] = useState(
    "Editorial launch poster for an orbital greenhouse, deep navy field, warm red horizon, crisp product typography",
  );
  const [strictMode, setStrictMode] = useState(true);
  const [activeCandidate, setActiveCandidate] = useState(2);
  const [runNumber, setRunNumber] = useState(2847);

  const runId = useMemo(
    () => `pf_2026_07_${String(runNumber).padStart(4, "0")}`,
    [runNumber],
  );

  function runProof() {
    if (runState === "running") return;
    setRunState("running");
    setActiveCandidate(0);
    window.setTimeout(() => setActiveCandidate(1), 420);
    window.setTimeout(() => setActiveCandidate(2), 840);
    window.setTimeout(() => {
      setRunNumber((value) => value + 1);
      setRunState("verified");
    }, 1260);
  }

  const stateLabel =
    runState === "running"
      ? "Agent loop running"
      : runState === "verified"
        ? "Manifest verified"
        : "Ready to generate";

  return (
    <main className="site-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="ProofFrame home">
          <span className="brand-mark" aria-hidden="true">
            PF
          </span>
          <span>ProofFrame</span>
        </a>
        <div className="topbar-meta">
          <span className="integration-pill">Genblaze × B2</span>
          <span className={`live-state ${runState}`}>
            <span className="status-dot" aria-hidden="true" />
            {stateLabel}
          </span>
        </div>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow">
          <span>GENERATIVE MEDIA CONTROL PLANE</span>
          <span className="eyebrow-line" />
          <span>RUN {runId}</span>
        </div>
        <div className="hero-copy">
          <h1>
            Generate until it passes.
            <span> Prove every pixel.</span>
          </h1>
          <p>
            ProofFrame turns generative media into a reviewable production
            system: policy-gated retries, immutable lineage, and content-addressed
            evidence on Backblaze B2.
          </p>
        </div>
        <div className="hero-stats" aria-label="Current run metrics">
          <div>
            <span className="stat-value">03</span>
            <span className="stat-label">attempts</span>
          </div>
          <div>
            <span className="stat-value">96</span>
            <span className="stat-label">quality score</span>
          </div>
          <div>
            <span className="stat-value">$0.057</span>
            <span className="stat-label">total cost</span>
          </div>
          <div>
            <span className="stat-value">24.3s</span>
            <span className="stat-label">wall time</span>
          </div>
        </div>
      </section>

      <section className="workbench" aria-label="ProofFrame generation workbench">
        <div className="brief-panel panel">
          <div className="panel-heading">
            <div>
              <span className="panel-index">01</span>
              <h2>Define the proof</h2>
            </div>
            <span className="panel-kicker">INPUT + POLICY</span>
          </div>

          <label className="field-label" htmlFor="creative-brief">
            Creative brief
          </label>
          <textarea
            id="creative-brief"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={5}
          />

          <div className="policy-heading">
            <span>Acceptance policy</span>
            <span>brand-launch-v4.json</span>
          </div>
          <div className="policy-grid">
            <label>
              <input type="checkbox" defaultChecked />
              <span>
                <strong>Contrast</strong>
                <small>WCAG AA · 4.5:1</small>
              </span>
            </label>
            <label>
              <input type="checkbox" defaultChecked />
              <span>
                <strong>Brand colors</strong>
                <small>ΔE ≤ 8</small>
              </span>
            </label>
            <label>
              <input type="checkbox" defaultChecked />
              <span>
                <strong>Object check</strong>
                <small>greenhouse ≥ 0.90</small>
              </span>
            </label>
            <label>
              <input type="checkbox" defaultChecked />
              <span>
                <strong>Safe zones</strong>
                <small>48px minimum</small>
              </span>
            </label>
          </div>

          <div className="run-controls">
            <label className="strict-toggle">
              <input
                type="checkbox"
                checked={strictMode}
                onChange={(event) => setStrictMode(event.target.checked)}
              />
              <span className="toggle-track" aria-hidden="true">
                <span />
              </span>
              Strict gate
            </label>
            <button
              className="run-button"
              type="button"
              onClick={runProof}
              disabled={runState === "running" || prompt.trim().length < 8}
            >
              <span>{runState === "running" ? "Running proof" : "Run proof"}</span>
              <span aria-hidden="true">↗</span>
            </button>
          </div>
        </div>

        <div className="result-panel panel">
          <div className="panel-heading">
            <div>
              <span className="panel-index">02</span>
              <h2>Compare the evidence</h2>
            </div>
            <span className="panel-kicker">AGENT LOOP</span>
          </div>

          <div className="candidate-stage">
            <div className={`artboard artboard-${candidates[activeCandidate].tone}`}>
              <span className="art-orbit orbit-one" />
              <span className="art-orbit orbit-two" />
              <div className="art-copy">
                <small>ORBITAL SYSTEMS / 2026</small>
                <strong>GROW<br />BEYOND</strong>
                <span>Closed-loop agriculture for the next frontier.</span>
              </div>
              <div className="frame-corners" aria-hidden="true">
                <i />
                <i />
                <i />
                <i />
              </div>
              <span className="watermark">PROOF {candidates[activeCandidate].id}</span>
            </div>
            <div className="score-card">
              <span>POLICY SCORE</span>
              <strong>{candidates[activeCandidate].score}</strong>
              <small>/ 100</small>
              <div className="score-bar">
                <span
                  style={{ width: `${candidates[activeCandidate].score}%` }}
                />
              </div>
            </div>
          </div>

          <div className="candidate-tabs" role="tablist" aria-label="Generated candidates">
            {candidates.map((candidate, index) => (
              <button
                key={candidate.id}
                className={activeCandidate === index ? "active" : ""}
                type="button"
                role="tab"
                aria-selected={activeCandidate === index}
                onClick={() => setActiveCandidate(index)}
              >
                <span className={`mini-art mini-${candidate.tone}`} />
                <span>
                  <strong>Frame {candidate.id}</strong>
                  <small>{candidate.note}</small>
                </span>
                <span className={`candidate-state ${candidate.status}`}>
                  {candidate.status}
                </span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="trace-section">
        <div className="section-intro">
          <span className="panel-index">03</span>
          <div>
            <h2>One decision. Complete lineage.</h2>
            <p>
              Every retry remains inspectable; only the passing artifact is
              promoted to the release path.
            </p>
          </div>
          <span className="hash-chip">SHA256 · 6f91…c2ae</span>
        </div>

        <div className="trace-rail">
          {trace.map((item, index) => (
            <div className="trace-node" key={item.index}>
              <span className="trace-number">{item.index}</span>
              <span className="trace-icon" aria-hidden="true">
                {index < 3 ? "✓" : "◆"}
              </span>
              <div>
                <strong>{item.label}</strong>
                <span>{item.detail}</span>
                <small>{item.meta}</small>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="evidence-grid">
        <div className="checks-card panel">
          <div className="panel-heading compact">
            <div>
              <span className="panel-index">04</span>
              <h2>Evaluator report</h2>
            </div>
            <span className="pass-pill">6 / 6 PASS</span>
          </div>
          <div className="check-list">
            {checks.map(([label, score, state]) => (
              <div className="check-row" key={label}>
                <span className="check-mark" aria-hidden="true">
                  ✓
                </span>
                <span>{label}</span>
                <span className="micro-bar">
                  <i style={{ width: `${score}%` }} />
                </span>
                <strong>{score}</strong>
                <small>{state}</small>
              </div>
            ))}
          </div>
        </div>

        <div className="manifest-card panel">
          <div className="panel-heading compact">
            <div>
              <span className="panel-index">05</span>
              <h2>B2 release manifest</h2>
            </div>
            <span className="manifest-status">
              <span className="status-dot" /> VERIFIED
            </span>
          </div>
          <dl>
            <div>
              <dt>Bucket</dt>
              <dd>proofframe-production</dd>
            </div>
            <div>
              <dt>Object</dt>
              <dd>assets/6f/91/6f91c2ae…e2.png</dd>
            </div>
            <div>
              <dt>Manifest</dt>
              <dd>manifests/{runId}.json</dd>
            </div>
            <div>
              <dt>Lineage</dt>
              <dd>root → 8ce1 → 19fd → 6f91</dd>
            </div>
            <div>
              <dt>Retention</dt>
              <dd>Object Lock · 30 days</dd>
            </div>
          </dl>
          <a
            className="manifest-button"
            href="/manifest-demo.json"
            target="_blank"
            rel="noreferrer"
          >
            <span>Inspect canonical manifest</span>
            <span aria-hidden="true">↗</span>
          </a>
        </div>
      </section>

      <footer>
        <div className="footer-brand">
          <span className="brand-mark" aria-hidden="true">
            PF
          </span>
          <span>
            <strong>ProofFrame</strong>
            <small>Media reliability infrastructure</small>
          </span>
        </div>
        <p>
          Powered by <strong>Genblaze</strong> orchestration and{" "}
          <strong>Backblaze B2</strong> evidence storage.
        </p>
        <span>BUILD 0.9.0 · 2026</span>
      </footer>
    </main>
  );
}
