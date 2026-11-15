import React, { useState } from "react";
import "./App.css";
import { askAssistant, runScenario } from "./api";

// -------------------- DEMO FIXTURES --------------------
// Illustrative UI fixtures matching app.py
const DEMO_RECORDS = [
  {
    "Record ID": "FB-DEMO-001",
    Investigation: "BASS (demo record)",
    Fuel: "PMMA (illustrative)",
    Gravity: "Microgravity",
    "O₂ fraction": "0.21",
    "Pressure (kPa)": "101.3",
    "Evidence class": "A · Direct",
    "Source status": "Demo fixture",
  },
  {
    "Record ID": "FB-DEMO-002",
    Investigation: "SAFFIRE (demo record)",
    Fuel: "Solid material (illustrative)",
    Gravity: "Microgravity",
    "O₂ fraction": "0.24",
    "Pressure (kPa)": "95.0",
    "Evidence class": "B · Interpolation",
    "Source status": "Demo fixture",
  },
  {
    "Record ID": "FB-DEMO-003",
    Investigation: "BASS-II (demo record)",
    Fuel: "Solid material (illustrative)",
    Gravity: "1 g",
    "O₂ fraction": "0.20",
    "Pressure (kPa)": "101.3",
    "Evidence class": "A · Direct",
    "Source status": "Demo fixture",
  },
];

const EVIDENCE_COLORS = {
  "A · Direct": "#35C4E0",
  "B · Interpolation": "#5B8DEF",
  "C · Extrapolation": "#F2A93B",
  "D · Unavailable": "#8A94A6",
};

const WORKSPACE_PAGES = [
  "Overview",
  "Evidence Explorer",
  "Evidence Envelope",
  "Scenario Analysis",
  "AI Assistant",
  "Research Gaps",
  "Methodology",
];

// -------------------- REUSABLE COMPONENTS --------------------
function Header({ title, subtitle, scenario }) {
  return (
    <div style={{ marginBottom: "16px" }}>
      <div className="eyebrow">FLAMEBOUND / RESEARCH WORKSPACE</div>
      <h1 style={{ margin: "5px 0 0 0" }}>{title}</h1>
      <p className="small-muted" style={{ marginTop: "5px" }}>
        {subtitle}
      </p>
      {scenario.active && (
        <div className="alert alert-info">
          <span>🧪</span>
          <span>
            Active scenario · O₂ fraction {scenario.oxygen} · Pressure{" "}
            {scenario.pressure} kPa absolute
          </span>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value, note }) {
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-note">{note}</div>
    </div>
  );
}

function Footer() {
  return (
    <footer style={{ marginTop: "40px" }}>
      <hr className="divider" />
      <p className="caption">
        FlameBound is a research and evidence-analysis tool. It is not a
        fire-safety certification system. · NASA is a data source, not a project
        partner or endorser.
      </p>
    </footer>
  );
}

function EvidenceBarChart() {
  const data = [
    { label: "A · Direct", count: 2, color: EVIDENCE_COLORS["A · Direct"] },
    { label: "B · Interpolation", count: 1, color: EVIDENCE_COLORS["B · Interpolation"] },
    { label: "C · Extrapolation", count: 0, color: EVIDENCE_COLORS["C · Extrapolation"] },
    { label: "D · Unavailable", count: 0, color: EVIDENCE_COLORS["D · Unavailable"] },
  ];
  const maxVal = 2;

  return (
    <svg viewBox="0 0 560 220" style={{ width: "100%", height: "230px", display: "block" }}>
      {/* Horizontal grid lines */}
      {[0, 1, 2].map((tick) => {
        const y = 175 - (tick / maxVal) * 140;
        return (
          <g key={tick}>
            <line x1="45" y1={y} x2="540" y2={y} stroke="#263349" strokeDasharray="3 3" />
            <text x="32" y={y + 4} fill="#9AA8BF" fontSize="11" textAnchor="end">
              {tick}
            </text>
          </g>
        );
      })}
      {/* Bars */}
      {data.map((d, i) => {
        const barWidth = 76;
        const x = 70 + i * 120;
        const barHeight = (d.count / maxVal) * 140;
        const y = 175 - barHeight;
        return (
          <g key={d.label}>
            {d.count > 0 && (
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                fill={d.color}
                rx="4"
              />
            )}
            <text
              x={x + barWidth / 2}
              y="198"
              fill="#9AA8BF"
              fontSize="11"
              textAnchor="middle"
            >
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function EnvelopeScatterPlot() {
  const points = [
    { o2: 0.18, p: 90, cls: "A · Direct" },
    { o2: 0.2, p: 101.3, cls: "A · Direct" },
    { o2: 0.21, p: 95, cls: "B · Interpolation" },
    { o2: 0.23, p: 101.3, cls: "A · Direct" },
    { o2: 0.24, p: 95, cls: "B · Interpolation" },
  ];

  // Domain mappings
  const minX = 0.17, maxX = 0.25;
  const minY = 88, maxY = 104;
  const plotLeft = 65, plotRight = 680, plotTop = 25, plotBottom = 310;

  const mapX = (val) =>
    plotLeft + ((val - minX) / (maxX - minX)) * (plotRight - plotLeft);
  const mapY = (val) =>
    plotBottom - ((val - minY) / (maxY - minY)) * (plotBottom - plotTop);

  return (
    <div className="panel" style={{ margin: "12px 0" }}>
      <div style={{ display: "flex", justifyContent: "flex-end", gap: "18px", fontSize: "0.8rem", marginBottom: "6px" }}>
        <span>
          <span className="dot" style={{ background: EVIDENCE_COLORS["A · Direct"] }} />
          A · Direct
        </span>
        <span>
          <span className="dot" style={{ background: EVIDENCE_COLORS["B · Interpolation"] }} />
          B · Interpolation
        </span>
      </div>
      <svg viewBox="0 0 720 360" style={{ width: "100%", height: "380px", display: "block" }}>
        {/* Y-axis grid */}
        {[90, 95, 100].map((pTick) => {
          const y = mapY(pTick);
          return (
            <g key={pTick}>
              <line x1={plotLeft} y1={y} x2={plotRight} y2={y} stroke="#263349" />
              <text x={plotLeft - 10} y={y + 4} fill="#9AA8BF" fontSize="11" textAnchor="end">
                {pTick}
              </text>
            </g>
          );
        })}
        {/* X-axis grid */}
        {[0.18, 0.2, 0.22, 0.24].map((oTick) => {
          const x = mapX(oTick);
          return (
            <g key={oTick}>
              <line x1={x} y1={plotTop} x2={x} y2={plotBottom} stroke="#263349" />
              <text x={x} y={plotBottom + 20} fill="#9AA8BF" fontSize="11" textAnchor="middle">
                {oTick.toFixed(2)}
              </text>
            </g>
          );
        })}
        {/* Axis titles */}
        <text
          x={(plotLeft + plotRight) / 2}
          y={plotBottom + 42}
          fill="#E6EDF7"
          fontSize="12"
          textAnchor="middle"
        >
          Oxygen fraction
        </text>
        <text
          x="18"
          y={(plotTop + plotBottom) / 2}
          fill="#E6EDF7"
          fontSize="12"
          textAnchor="middle"
          transform={`rotate(-90, 18, ${(plotTop + plotBottom) / 2})`}
        >
          Pressure (kPa)
        </text>

        {/* Data points */}
        {points.map((pt, i) => (
          <circle
            key={i}
            cx={mapX(pt.o2)}
            cy={mapY(pt.p)}
            r="6.5"
            fill={EVIDENCE_COLORS[pt.cls]}
          >
            <title>
              O₂: {pt.o2} | Pressure: {pt.p} kPa | {pt.cls}
            </title>
          </circle>
        ))}
      </svg>
    </div>
  );
}

// -------------------- MAIN APP --------------------
export default function App() {
  const [page, setPage] = useState("Overview");
  const [expertMode, setExpertMode] = useState(false);

  // Global Scenario Session State
  const [scenario, setScenario] = useState({
    active: false,
    oxygen: 0.21,
    pressure: 101.3,
  });

  // Form inputs for Scenario Analysis
  const [oxygenInput, setOxygenInput] = useState(0.21);
  const [pressureInput, setPressureInput] = useState(101.3);
  const [scenarioCalculation, setScenarioCalculation] = useState(null);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [scenarioError, setScenarioError] = useState("");

  // Evidence Explorer Filters
  const [fuelFilter, setFuelFilter] = useState("All");
  const [gravityFilter, setGravityFilter] = useState("All");
  const [eclassFilter, setEclassFilter] = useState("All");
  const [selectedRecordId, setSelectedRecordId] = useState(
    DEMO_RECORDS[0]["Record ID"]
  );

  // AI Assistant State
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

  // Methodology Tabs State
  const [activeTab, setActiveTab] = useState("Pipeline");

  // Filtered view for Evidence Explorer
  const filteredRecords = DEMO_RECORDS.filter((r) => {
    if (fuelFilter !== "All" && r.Fuel !== fuelFilter) return false;
    if (gravityFilter !== "All" && r.Gravity !== gravityFilter) return false;
    if (eclassFilter !== "All" && r["Evidence class"] !== eclassFilter)
      return false;
    return true;
  });

  const selectedRecord =
    DEMO_RECORDS.find((r) => r["Record ID"] === selectedRecordId) ||
    DEMO_RECORDS[0];

  const handleCalculateScenario = async (e) => {
    e.preventDefault();
    setScenarioLoading(true);
    setScenarioError("");
    try {
      const result = await runScenario({
        oxygen_mole_fraction: Number(oxygenInput),
        total_pressure: Number(pressureInput),
        pressure_unit: "kPa",
        pressure_basis: "absolute",
      });
      setScenario({ active: true, oxygen: Number(oxygenInput), pressure: Number(pressureInput) });
      setScenarioCalculation(result);
    } catch (error) {
      setScenarioError(error.message);
    } finally {
      setScenarioLoading(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    const question = chatInput.trim();
    if (!question || chatLoading) return;
    const priorHistory = chatHistory.map((item) => ({
      role: item.who,
      content: item.msg,
    })).slice(-8);
    setChatHistory((prev) => [...prev, { who: "user", msg: question }]);
    setChatInput("");
    setChatLoading(true);
    setChatError("");
    try {
      const response = await askAssistant(question, priorHistory);
      setChatHistory((prev) => [...prev, {
        who: "assistant",
        msg: response.explanation,
        status: response.status,
        bases: response.bases,
        citations: response.citations,
        calculation: response.calculation,
      }]);
    } catch (error) {
      setChatError(error.message);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="app-shell">
      {/* -------------------- SIDEBAR -------------------- */}
      <aside className="sidebar">
        <div className="brand-title">🔥 FlameBound</div>
        <div className="caption">Evidence Before Extrapolation</div>
        <hr className="divider" />

        <span className="sidebar-section-label">WORKSPACE</span>
        <div className="nav-list">
          {WORKSPACE_PAGES.map((item) => {
            const isActive = page === item;
            return (
              <div
                key={item}
                className={`nav-radio-item ${isActive ? "active" : ""}`}
                onClick={() => setPage(item)}
              >
                <span className="radio-dot">
                  {isActive && <span className="radio-dot-inner" />}
                </span>
                <span>{item}</span>
              </div>
            );
          })}
        </div>

        <hr className="divider" />
        <span className="sidebar-section-label">EVIDENCE LEGEND</span>
        <div className="legend">
          <div>
            <span className="dot" style={{ background: "#35C4E0" }} />A · Direct
            experimental
          </div>
          <div>
            <span className="dot" style={{ background: "#5B8DEF" }} />B ·
            Interpolation
          </div>
          <div>
            <span className="dot" style={{ background: "#F2A93B" }} />C ·
            Extrapolation
          </div>
          <div>
            <span className="dot" style={{ background: "#8A94A6" }} />D ·
            Unavailable
          </div>
        </div>

        <div
          className="toggle-row"
          onClick={() => setExpertMode((prev) => !prev)}
        >
          <div className={`toggle-track ${expertMode ? "on" : ""}`}>
            <div className="toggle-thumb" />
          </div>
          <span>Expert mode</span>
        </div>

        <hr className="divider" />
        <span className="sidebar-section-label">SYSTEM STATUS</span>
        <div className="caption">● UI running</div>
        <div className="caption">○ NASA data connection — not connected</div>
        <div className="caption">Atmospheric engine: backend API (requires local backend)</div>
        <div className="caption">Assistant API: local Ollama + PSI source lookup</div>
        <div className="caption">Data version: DEMO-0.1</div>
      </aside>

      {/* -------------------- MAIN WORKSPACE -------------------- */}
      <main className="main-area">
        {/* 1. OVERVIEW */}
        {page === "Overview" && (
          <div>
            <Header
              title="Evidence overview"
              subtitle="Explore experimental fire research, inspect evidence coverage and understand where the evidence ends."
              scenario={scenario}
            />
            <div className="hero">
              <div className="eyebrow">WELCOME TO FLAMEBOUND</div>
              <h2 style={{ margin: "8px 0" }}>
                Evidence first. Extrapolation second.
              </h2>
              <p
                style={{
                  color: "#B7C5D9",
                  maxWidth: "760px",
                  margin: 0,
                  lineHeight: 1.55,
                }}
              >
                A research workspace concept connecting NASA BASS, BASS-II and
                SAFFIRE evidence with transparent calculations, uncertainty and
                source-grounded explanations.
              </p>
            </div>

            <div className="grid-4">
              <Metric
                label="Investigations"
                value="—"
                note="Awaiting verified dataset"
              />
              <Metric
                label="Test records"
                value="3 demo"
                note="Illustrative UI fixtures"
              />
              <Metric
                label="Evidence classes"
                value="4"
                note="A · B · C · D"
              />
              <Metric
                label="Gravity classes"
                value="2"
                note="1 g and microgravity in demo fixtures"
              />
            </div>

            <h3 className="section-title">Evidence coverage snapshot</h3>
            <div className="grid-overview-split">
              <div className="panel">
                <div style={{ fontWeight: 700, marginBottom: "10px" }}>
                  Evidence records by class
                </div>
                <EvidenceBarChart />
                <div className="caption">
                  Illustrative demo counts only — not NASA dataset statistics.
                </div>
              </div>

              <div className="panel">
                <div style={{ fontWeight: 700, marginBottom: "12px" }}>
                  Data status
                </div>
                <div style={{ fontSize: "0.9rem", marginTop: "8px" }}>
                  NASA source connection
                </div>
                <div className="alert alert-warning">Not connected</div>

                <div style={{ fontSize: "0.9rem", marginTop: "12px" }}>
                  Record verification
                </div>
                <div className="alert alert-info">Demo fixtures only</div>

                <div style={{ fontSize: "0.9rem", marginTop: "12px" }}>
                  Scientific calculations
                </div>
                <div className="alert alert-info">
                  One basic equation demonstrated
                </div>
              </div>
            </div>

            <h3 className="section-title">Research workflow</h3>
            <div className="grid-3">
              <div className="panel">
                <div className="eyebrow">01 / COLLECT</div>
                <h3 style={{ marginTop: "8px" }}>Organise evidence</h3>
                <p className="small-muted" style={{ margin: 0 }}>
                  Bring BASS, BASS-II and SAFFIRE records together with
                  traceable sources.
                </p>
              </div>
              <div className="panel">
                <div className="eyebrow">02 / ANALYSE</div>
                <h3 style={{ marginTop: "8px" }}>Inspect conditions</h3>
                <p className="small-muted" style={{ margin: 0 }}>
                  Calculate physical quantities and compare scenarios with
                  tested conditions.
                </p>
              </div>
              <div className="panel">
                <div className="eyebrow">03 / EXPLAIN</div>
                <h3 style={{ marginTop: "8px" }}>Show limitations</h3>
                <p className="small-muted" style={{ margin: 0 }}>
                  Expose evidence gaps and provide source-grounded explanations.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 2. EVIDENCE EXPLORER */}
        {page === "Evidence Explorer" && (
          <div>
            <Header
              title="Evidence explorer"
              subtitle="Browse investigation records, filter conditions and inspect source provenance."
              scenario={scenario}
            />

            <div className="grid-3">
              <div className="field-group">
                <label className="field-label">Fuel / material</label>
                <select
                  className="select-input"
                  value={fuelFilter}
                  onChange={(e) => setFuelFilter(e.target.value)}
                >
                  <option value="All">All</option>
                  <option value="PMMA (illustrative)">
                    PMMA (illustrative)
                  </option>
                  <option value="Solid material (illustrative)">
                    Solid material (illustrative)
                  </option>
                </select>
              </div>

              <div className="field-group">
                <label className="field-label">Gravity condition</label>
                <select
                  className="select-input"
                  value={gravityFilter}
                  onChange={(e) => setGravityFilter(e.target.value)}
                >
                  <option value="All">All</option>
                  <option value="Microgravity">Microgravity</option>
                  <option value="1 g">1 g</option>
                </select>
              </div>

              <div className="field-group">
                <label className="field-label">Evidence class</label>
                <select
                  className="select-input"
                  value={eclassFilter}
                  onChange={(e) => setEclassFilter(e.target.value)}
                >
                  <option value="All">All</option>
                  <option value="A · Direct">A · Direct</option>
                  <option value="B · Interpolation">B · Interpolation</option>
                  <option value="C · Extrapolation">C · Extrapolation</option>
                  <option value="D · Unavailable">D · Unavailable</option>
                </select>
              </div>
            </div>

            <div className="caption">
              {filteredRecords.length} illustrative records shown · Replace
              these fixtures with verified dataset records.
            </div>

            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Record ID</th>
                    <th>Investigation</th>
                    <th>Fuel</th>
                    <th>Gravity</th>
                    <th>O₂ fraction</th>
                    <th>Pressure (kPa)</th>
                    <th>Evidence class</th>
                    <th>Source status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((rec) => (
                    <tr key={rec["Record ID"]}>
                      <td>{rec["Record ID"]}</td>
                      <td>{rec.Investigation}</td>
                      <td>{rec.Fuel}</td>
                      <td>{rec.Gravity}</td>
                      <td>{rec["O₂ fraction"]}</td>
                      <td>{rec["Pressure (kPa)"]}</td>
                      <td>{rec["Evidence class"]}</td>
                      <td>{rec["Source status"]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h3 className="section-title">Record details</h3>
            <div className="field-group" style={{ maxWidth: "360px" }}>
              <label className="field-label">Choose a record</label>
              <select
                className="select-input"
                value={selectedRecordId}
                onChange={(e) => setSelectedRecordId(e.target.value)}
              >
                {DEMO_RECORDS.map((r) => (
                  <option key={r["Record ID"]} value={r["Record ID"]}>
                    {r["Record ID"]}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid-2">
              <div className="panel" style={{ lineHeight: 1.8 }}>
                <div style={{ fontWeight: 700, marginBottom: "6px" }}>
                  {selectedRecord["Record ID"]}
                </div>
                <div>Investigation: {selectedRecord.Investigation}</div>
                <div>Fuel: {selectedRecord.Fuel}</div>
                <div>Gravity: {selectedRecord.Gravity}</div>
                <div>Evidence: {selectedRecord["Evidence class"]}</div>
              </div>

              <div className="panel">
                <div style={{ fontWeight: 700, marginBottom: "8px" }}>
                  Provenance
                </div>
                <div className="alert alert-info">
                  This is a UI demonstration record. No original NASA source
                  document or verified record is attached.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 3. EVIDENCE ENVELOPE */}
        {page === "Evidence Envelope" && (
          <div>
            <Header
              title="Evidence envelope"
              subtitle="Visualise the available tested-condition space. This demo chart is illustrative, not measured NASA data."
              scenario={scenario}
            />
            <div className="alert alert-info">
              A real evidence envelope must be generated from verified records
              and validated analysis outputs.
            </div>

            <EnvelopeScatterPlot />

            <div className="caption">
              Points are synthetic placeholders for layout demonstration. They
              do not represent experimental measurements.
            </div>

            <div style={{ fontWeight: 700, marginTop: "20px" }}>
              What the envelope should communicate
            </div>
            <ul className="bullet-list">
              <li>Which conditions have direct experimental support.</li>
              <li>Where interpolation is being used.</li>
              <li>Where a scenario lies outside available evidence.</li>
              <li>Data density, uncertainty and limitations.</li>
            </ul>
          </div>
        )}

        {/* 4. SCENARIO ANALYSIS */}
        {page === "Scenario Analysis" && (
          <div>
            <Header
              title="Scenario analysis"
              subtitle="Calculate oxygen partial pressure and compare the input with the available evidence."
              scenario={scenario}
            />
            <div className="alert alert-info">
              The calculation below demonstrates p(O₂) = X(O₂) × P. It is not a
              prediction of ignition, flame spread or fire safety.
            </div>

            <form
              onSubmit={handleCalculateScenario}
              className="panel"
              style={{ marginTop: "14px" }}
            >
              <div className="grid-2">
                <div className="field-group">
                  <label className="field-label">
                    Oxygen mole fraction (0–1)
                  </label>
                  <input
                    type="number"
                    className="number-input"
                    min="0"
                    max="1"
                    step="0.01"
                    value={oxygenInput}
                    onChange={(e) => setOxygenInput(e.target.value)}
                    required
                  />
                </div>
                <div className="field-group">
                  <label className="field-label">Total pressure (kPa absolute)</label>
                  <input
                    type="number"
                    className="number-input"
                    min="0.1"
                    max="2000"
                    step="0.001"
                    value={pressureInput}
                    onChange={(e) => setPressureInput(e.target.value)}
                    required
                  />
                </div>
              </div>
              <button type="submit" className="btn-primary" disabled={scenarioLoading}>
                {scenarioLoading ? "Calculating…" : "Calculate scenario"}
              </button>
            </form>

            {scenarioError && <div className="alert alert-error" role="alert">{scenarioError}</div>}
            {scenario.active && scenarioCalculation ? (
              <div>
                <h3 className="section-title">Calculation result</h3>
                <Metric
                  label="Oxygen partial pressure"
                  value={`${scenarioCalculation.outputs.oxygen_partial_pressure_kpa} kPa`}
                  note={`${scenario.oxygen} × ${scenario.pressure} kPa absolute`}
                />
                <pre className="calculation-envelope">{JSON.stringify(scenarioCalculation, null, 2)}</pre>
                <div className="latex-block">p(O₂) = X(O₂) × P</div>

                <h3 className="section-title">Evidence comparison</h3>
                <div className="alert alert-warning">
                  No verified experimental dataset is connected. Evidence match,
                  distance and extrapolation class cannot yet be determined.
                </div>
                <div className="caption">
                  Do not interpret this calculated quantity as a fire-behaviour
                  prediction.
                </div>
              </div>
            ) : (
              <div className="caption" style={{ marginTop: "12px" }}>
                Enter a scenario and select Calculate scenario to see the
                calculation.
              </div>
            )}
          </div>
        )}

        {/* 5. AI ASSISTANT */}
        {page === "AI Assistant" && (
          <div>
            <Header
              title="AI research assistant"
              subtitle="Ask questions about evidence, methods and documented limitations."
              scenario={scenario}
            />
            <div className="alert alert-warning">
              Atmospheric calculations run deterministically on the backend. PSI passages are retrieved from local, hash-checked files; citations are unreviewed. Image-only scans and the sensitive local-only workbook are excluded from search.
            </div>

            <div className="chat-history">
              {chatHistory.map((item, idx) => (
                <div key={idx} className="chat-bubble">
                  <div className="chat-avatar">
                    {item.who === "user" ? "🧑" : "🤖"}
                  </div>
                  <div style={{ lineHeight: 1.5, fontSize: "0.92rem" }}>
                    {item.msg}
                    {item.status && <div className="caption">Status: {item.status}{item.bases?.length ? ` · Basis: ${item.bases.join(", ")}` : ""}</div>}
                    {item.calculation && <details><summary>Calculation details</summary><pre className="calculation-envelope">{JSON.stringify(item.calculation, null, 2)}</pre></details>}
                    {item.citations?.length > 0 && <ul>{item.citations.map((citation) => <li key={citation.citation_id}>{citation.title}, {citation.location_label || `p. ${citation.page}`} ({citation.review_status})</li>)}</ul>}
                  </div>
                </div>
              ))}
            </div>
            {chatLoading && <div className="caption" role="status">Assistant is responding…</div>}
            {chatError && <div className="alert alert-error" role="alert">{chatError}</div>}

            <form onSubmit={handleChatSubmit} className="chat-form">
              <input
                type="text"
                className="chat-text-input"
                placeholder="Example: What does oxygen partial pressure mean?"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                disabled={chatLoading}
              />
              <button
                type="submit"
                className="btn-primary"
                style={{ width: "auto" }}
                disabled={chatLoading || !chatInput.trim()}
              >
                {chatLoading ? "Sending…" : "Send"}
              </button>
            </form>

            <div className="caption" style={{ marginTop: "10px" }}>
              Requests are stateless. Recent conversation text is sent as untrusted context; calculation inputs must be explicit in the current question.
            </div>
          </div>
        )}

        {/* 6. RESEARCH GAPS */}
        {page === "Research Gaps" && (
          <div>
            <Header
              title="Research gaps"
              subtitle="Identify missing coverage and avoid over-interpreting sparse experimental evidence."
              scenario={scenario}
            />
            <div className="alert alert-info">
              Gap rankings require verified records and a defined analysis
              method. No real gap score is shown here.
            </div>

            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Dimension</th>
                    <th>Current status</th>
                    <th>Evidence note</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    "Oxygen fraction",
                    "Total pressure",
                    "Airflow",
                    "Fuel / geometry",
                  ].map((dim) => (
                    <tr key={dim}>
                      <td>{dim}</td>
                      <td>Requires dataset</td>
                      <td>Not assessed</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h3 className="section-title">Questions this page should answer</h3>
            <ul className="bullet-list">
              <li>
                Which combinations of conditions have little or no direct
                evidence?
              </li>
              <li>Which fuels and geometries are underrepresented?</li>
              <li>
                Where does the analysis rely on interpolation or extrapolation?
              </li>
              <li>What additional experiments would reduce uncertainty?</li>
            </ul>
          </div>
        )}

        {/* 7. METHODOLOGY */}
        {page === "Methodology" && (
          <div>
            <Header
              title="Methodology & system status"
              subtitle="Understand the data pipeline, scientific boundaries and current implementation status."
              scenario={scenario}
            />

            <div className="tabs-bar">
              {["Pipeline", "Scientific boundary", "Data status"].map((tab) => (
                <button
                  key={tab}
                  className={`tab-btn ${activeTab === tab ? "active" : ""}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>

            {activeTab === "Pipeline" && (
              <div>
                {[
                  ["01", "NASA PSI source audit", "INCOMPLETE"],
                  ["02", "Verified harmonised test points", "NOT AVAILABLE"],
                  ["03", "Atmospheric calculation API", "AVAILABLE"],
                  ["04", "Evidence coverage + uncertainty", "NOT AVAILABLE"],
                  ["05", "Assistant + web dashboard", "LOCAL DEMO"],
                  ["06", "Local PSI passage search", "UNREVIEWED"],
                ].map(([num, label, status]) => (
                  <div
                    key={num}
                    className="panel"
                    style={{
                      marginBottom: "9px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <b style={{ color: "#35C4E0", marginRight: "14px" }}>
                        {num}
                      </b>
                      <span>{label}</span>
                    </div>
                    <span style={{ color: "#9AA8BF", fontSize: "0.8rem" }}>
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {activeTab === "Scientific boundary" && (
              <div className="panel">
                <div style={{ fontWeight: 700, marginBottom: "10px" }}>
                  Supported demonstration calculation
                </div>
                <div className="latex-block">p(O₂) = X(O₂) × P</div>
                <p style={{ fontSize: "0.92rem" }}>
                  Oxygen partial pressure is calculated from oxygen mole
                  fraction and total pressure.
                </p>
                <div className="alert alert-error">
                  This equation does not predict ignition, flame spread or
                  whether a scenario is safe.
                </div>
                <p style={{ fontSize: "0.92rem", marginBottom: 0 }}>
                  Scientific calculations must be deterministic Python
                  functions, not generated by the language model.
                </p>
              </div>
            )}

            {activeTab === "Data status" && (
              <div className="panel" style={{ lineHeight: 2, fontSize: "0.92rem" }}>
                <div>Structured records: not connected</div>
                <div>NASA source provenance: not connected</div>
                <div>Vector passage index: not connected</div>
                <div>Ollama: optional local provider for general answers; connection not monitored</div>
                <div>
                  Visible records and chart points are illustrative demo fixtures, not experimental observations.
                </div>
              </div>
            )}
          </div>
        )}

        <Footer />
      </main>
    </div>
  );
}
