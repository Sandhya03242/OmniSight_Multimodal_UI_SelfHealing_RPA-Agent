import { useEffect, useState } from "react";

import "./index.css";

const API = "http://localhost:8000";

function App() {
  const [status, setStatus] = useState(null);
  const [issues, setIssues] = useState([]);
  const [optimization, setOptimization] = useState(null);
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState("System ready");

  // QA REVIEW STATE
  const [reviewStatus, setReviewStatus] = useState(null);
  const [reviewLoading, setReviewLoading] = useState(false);

  // ============================================================
  // HELPERS
  // ============================================================

  const getFilename = (path) => {
    if (!path) return null;

    return String(path)
      .replace(/\\/g, "/")
      .split("/")
      .pop();
  };

  const getScreenshotUrl = (path) => {
    const name = getFilename(path);

    if (!name) return null;

    return `${API}/screenshots/${encodeURIComponent(name)}`;
  };

  // ============================================================
  // LOAD DASHBOARD
  // ============================================================

  const loadDashboard = async () => {
    try {
      const [statusRes, issuesRes, optimizationRes] =
        await Promise.all([
          fetch(`${API}/dashboard/status`),
          fetch(`${API}/dashboard/issues`),
          fetch(`${API}/optimization/status`),
        ]);

      if (statusRes.ok) {
        const data = await statusRes.json();

        console.log("DASHBOARD STATUS:", data);

        setStatus(data);
      }

      if (issuesRes.ok) {
        const data = await issuesRes.json();

        console.log("DASHBOARD ISSUES:", data);

        setIssues(data.issues || []);
      }

      if (optimizationRes.ok) {
        const data = await optimizationRes.json();

        console.log("OPTIMIZATION:", data);

        setOptimization(data);
      }

      setMessage("System synchronized");
    } catch (error) {
      console.error(
        "Dashboard connection error:",
        error
      );

      setMessage(
        "Backend connection failed"
      );
    }
  };

  useEffect(() => {
    loadDashboard();

    const timer = setInterval(
      loadDashboard,
      5000
    );

    return () =>
      clearInterval(timer);
  }, []);

  // ============================================================
  // RUN HEALING
  // ============================================================

  const runHealing = async () => {
    setRunning(true);

    setReviewStatus(null);

    setMessage(
      "OmniSight agent is working..."
    );

    try {
      const response = await fetch(
        `${API}/healing/run`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            url: "http://localhost:5173",
            max_attempts: 2,
          }),
        }
      );

      const data =
        await response.json();

      console.log(
        "HEALING RESULT:",
        data
      );

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Healing pipeline failed"
        );
      }

      setMessage(
        "Healing pipeline completed"
      );

      await loadDashboard();
    } catch (error) {
      console.error(error);

      setMessage(
        error.message ||
          "Healing failed"
      );
    } finally {
      setRunning(false);
    }
  };

  // ============================================================
  // APPROVE / REJECT
  // ============================================================

  const reviewIssue = async (
    issue,
    action
  ) => {
    if (reviewLoading) {
      return;
    }

    setReviewLoading(true);
    setReviewStatus(null);

    setMessage(
      action === "approve"
        ? "Submitting approval..."
        : "Submitting rejection..."
    );

    try {
      const endpoint =
        action === "approve"
          ? `${API}/github/pr/approve`
          : `${API}/github/pr/reject`;

      console.log(
        `Submitting ${action.toUpperCase()} request...`
      );

      const response =
        await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            issue_id: issue.id,
            pr_number:
              issue.pr_number ?? 0,
            comment:
              action === "approve"
                ? "Approved from OmniSight QA Dashboard"
                : "Rejected from OmniSight QA Dashboard",
          }),
        });

      const data =
        await response.json();

      console.log(
        `${action.toUpperCase()} RESPONSE:`,
        data
      );

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Review failed"
        );
      }

      // ========================================================
      // SUCCESS
      // ========================================================

      if (action === "approve") {
        setReviewStatus(
          "approved"
        );

        setMessage(
          "✓ AI healing approved successfully"
        );
      } else {
        setReviewStatus(
          "rejected"
        );

        setMessage(
          "✕ AI healing rejected"
        );
      }

      await loadDashboard();
    } catch (error) {
      console.error(
        "Review error:",
        error
      );

      setReviewStatus("error");

      setMessage(
        error.message ||
          "Review failed"
      );
    } finally {
      setReviewLoading(false);
    }
  };

  // ============================================================
  // DASHBOARD DATA
  // ============================================================

  const latestIssue =
    issues[0];

  const issueCount =
    status?.issues_detected ??
    issues.length ??
    0;

  const fixes =
    status?.fixes ||
    latestIssue?.fixes ||
    [];

  const fixesCount =
    status?.fixes_generated ??
    fixes.length ??
    0;

  const verified =
    status?.fixed === true ||
    status?.healing_status ===
      "published" ||
    status?.verification
      ?.fixed === true;

  const githubSuccess =
    status?.github?.status ===
    "success";

  // ============================================================
  // OPTIMIZATION DATA
  // ============================================================

  const imageOptimization =
    optimization?.image_optimization;

  const htmlReduction =
    optimization?.html_reduction;

  const originalHtml =
    htmlReduction?.original_length ??
    0;

  const reducedHtml =
    htmlReduction?.reduced_length ??
    0;

  const reduction =
    originalHtml > 0
      ? Math.round(
          ((originalHtml -
            reducedHtml) /
            originalHtml) *
            100
        )
      : 0;

  // ============================================================
  // BEFORE SCREENSHOT
  // ============================================================

  const beforeScreenshot =
    getScreenshotUrl(
      status?.before_screenshot ||
        status?.before?.screenshot ||
        latestIssue?.before_screenshot ||
        latestIssue?.screenshot
    );

  // ============================================================
  // AFTER SCREENSHOT
  // ============================================================

  const afterScreenshot =
    getScreenshotUrl(
      status?.after_screenshot ||
        status?.after?.screenshot ||
        latestIssue?.after_screenshot ||
        (verified
          ? latestIssue?.screenshot
          : null)
    );

  // ============================================================
  // ACTUAL AI FIX
  // ============================================================

  const latestFix =
    fixes[0];

  const oldCode =
    latestFix?.old ||
    latestFix?.old_code ||
    "";

  const newCode =
    latestFix?.new ||
    latestFix?.new_code ||
    "";

  return (
    <div className="app">

      {/* ======================================================
          BACKGROUND
      ====================================================== */}

      <div className="orb orb-one"></div>
      <div className="orb orb-two"></div>
      <div className="grid-background"></div>

      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <header className="navbar">

        <div className="brand">

          <div className="brand-icon">
            ✦
          </div>

          <div>

            <div className="brand-name">
              OMNISIGHT
            </div>

            <div className="brand-subtitle">
              Autonomous UI Intelligence
            </div>

          </div>

        </div>

        <div className="nav-right">

          <div className="system-status">

            <span className="pulse"></span>

            SYSTEM ONLINE

          </div>

          <div className="version">
            v4.0
          </div>

        </div>

      </header>

      {/* ======================================================
          HERO
      ====================================================== */}

      <section className="hero">

        <div className="hero-content">

          <div className="eyebrow">
            MULTIMODAL AI · RPA · SELF-HEALING QA
          </div>

          <h1>
            AI-Powered
            <span>
              UI Self-Healing
            </span>
          </h1>

          <p>
            Detect visual defects, generate
            intelligent fixes, verify the
            result and publish the healed
            application automatically.
          </p>

          <button
            className={`run-button ${
              running
                ? "running"
                : ""
            }`}
            onClick={runHealing}
            disabled={running}
          >

            <span className="button-icon">

              {running
                ? "◌"
                : "▶"}

            </span>

            {running
              ? "RUNNING HEALING PIPELINE..."
              : "RUN HEALING PIPELINE"}

          </button>

          <div className="system-message">

            <span>
              ●
            </span>

            {message}

          </div>

        </div>

        <div className="hero-visual">

          <div className="ai-ring">

            <div className="ring ring-one"></div>
            <div className="ring ring-two"></div>
            <div className="ring ring-three"></div>

            <div className="ai-core">

              <div className="brain">
                ✦
              </div>

              <span>
                AI
              </span>

            </div>

          </div>

        </div>

      </section>

      {/* ======================================================
          METRICS
      ====================================================== */}

      <section className="metrics">

        <MetricCard
          icon="◈"
          label="ISSUES DETECTED"
          value={String(
            issueCount
          ).padStart(2, "0")}
          accent="purple"
        />

        <MetricCard
          icon="⚡"
          label="FIXES GENERATED"
          value={String(
            fixesCount
          ).padStart(2, "0")}
          accent="blue"
        />

        <MetricCard
          icon="✓"
          label="VERIFICATION"
          value={
            verified
              ? "PASS"
              : "PENDING"
          }
          accent="green"
        />

        <MetricCard
          icon="⌘"
          label="GITHUB"
          value={
            githubSuccess
              ? "PUBLISHED"
              : "READY"
          }
          accent="pink"
        />

      </section>

      {/* ======================================================
          PIPELINE
      ====================================================== */}

      <section className="panel">

        <SectionHeading
          number="01"
          title="SELF-HEALING PIPELINE"
          description="Autonomous Plan → Execute → Evaluate workflow"
        />

        <div className="pipeline">

          <PipelineStep
            icon="◎"
            title="CAPTURE"
            description="Playwright"
            done={true}
          />

          <PipelineLine />

          <PipelineStep
            icon="◉"
            title="ANALYZE"
            description="Qwen Vision"
            done={
              issueCount > 0
            }
          />

          <PipelineLine />

          <PipelineStep
            icon="✦"
            title="HEAL"
            description="AI Fix Engine"
            done={
              fixesCount > 0
            }
          />

          <PipelineLine />

          <PipelineStep
            icon="✓"
            title="VERIFY"
            description="Visual Audit"
            done={verified}
          />

          <PipelineLine />

          <PipelineStep
            icon="⌁"
            title="PUBLISH"
            description="GitHub"
            done={
              githubSuccess
            }
          />

        </div>

      </section>

      {/* ======================================================
          VISUAL HEALING
      ====================================================== */}

      <section className="panel">

        <SectionHeading
          number="02"
          title="VISUAL HEALING"
          description="Before and after visual verification"
        />

        <div className="comparison">

          {/* BEFORE */}

          <div className="screenshot-card">

            <div className="screenshot-header">

              <div>

                <span className="dot red"></span>

                BEFORE HEALING

              </div>

              <span className="badge danger">
                ISSUE FOUND
              </span>

            </div>

            <div className="screenshot-area before">

              {beforeScreenshot ? (

                <img
                  src={beforeScreenshot}
                  alt="Before healing"
                  className="healing-screenshot"
                  onError={(event) => {

                    console.error(
                      "Before screenshot failed:",
                      beforeScreenshot
                    );

                    event.currentTarget.style.display =
                      "none";

                  }}
                />

              ) : (

                <div className="empty-preview">

                  <div className="preview-icon">
                    ◫
                  </div>

                  <span>
                    Waiting for screenshot
                  </span>

                </div>

              )}

              {beforeScreenshot && (

                <div className="issue-marker">

                  <span></span>

                  VISUAL ANOMALY

                </div>

              )}

            </div>

          </div>

          {/* ARROW */}

          <div className="arrow">
            →
          </div>

          {/* AFTER */}

          <div className="screenshot-card">

            <div className="screenshot-header">

              <div>

                <span className="dot green"></span>

                AFTER HEALING

              </div>

              <span className="badge success">

                {verified
                  ? "VERIFIED"
                  : "PENDING"}

              </span>

            </div>

            <div className="screenshot-area after">

              {afterScreenshot ? (

                <img
                  src={afterScreenshot}
                  alt="After healing"
                  className="healing-screenshot"
                  onError={(event) => {

                    console.error(
                      "After screenshot failed:",
                      afterScreenshot
                    );

                    event.currentTarget.style.display =
                      "none";

                  }}
                />

              ) : (

                <div className="empty-preview">

                  <div className="preview-icon">
                    ✦
                  </div>

                  <span>
                    Run the healing pipeline
                  </span>

                </div>

              )}

              {verified &&
                afterScreenshot && (

                  <div className="fixed-overlay">
                    ✓ UI HEALED
                  </div>

                )}

            </div>

          </div>

        </div>

      </section>

      {/* ======================================================
          AI ANALYSIS + SELF HEALING
      ====================================================== */}

      <section className="two-column">

        {/* AI ANALYSIS */}

        <div className="panel">

          <SectionHeading
            number="03"
            title="AI VISION ANALYSIS"
            description="Multimodal screenshot + DOM reasoning"
          />

          {latestIssue ? (

            <div className="analysis-content">

              <div className="severity-row">

                <span className="severity-dot"></span>

                <span>

                  {latestIssue.severity ||
                    "MEDIUM"}{" "}

                  SEVERITY

                </span>

              </div>

              <h3>

                {latestIssue.type ||
                  "Visual UI Issue"}

              </h3>

              <p className="issue-description">

                {latestIssue.description ||
                  "The AI detected a visual anomaly in the application."}

              </p>

              <div className="info-row">

                <span>
                  ELEMENT
                </span>

                <strong>

                  {latestIssue.element ||
                    "UI Component"}

                </strong>

              </div>

              <div className="suggestion">

                <div className="suggestion-title">

                  <span>
                    ✦
                  </span>

                  AI RECOMMENDATION

                </div>

                <p>

                  {latestIssue.suggested_fix ||
                    "The AI will generate an appropriate source-level fix."}

                </p>

              </div>

            </div>

          ) : (

            <EmptyState
              icon="◉"
              text="No visual issues detected yet"
            />

          )}

        </div>

        {/* SELF HEALING FIX */}

        <div className="panel">

          <SectionHeading
            number="04"
            title="SELF-HEALING FIX"
            description="Actual AI-generated source transformation"
          />

          {latestFix ? (

            <>

              <div className="code-window">

                <div className="code-topbar">

                  <div className="window-dots">

                    <i></i>
                    <i></i>
                    <i></i>

                  </div>

                  <span>
                    App.jsx
                  </span>

                  <span className="code-status">
                    AI PATCH
                  </span>

                </div>

                <div className="code-body">

                  <div className="code-line removed">

                    <span>
                      -
                    </span>

                    <code>
                      {oldCode}
                    </code>

                  </div>

                  <div className="code-line added">

                    <span>
                      +
                    </span>

                    <code>
                      {newCode}
                    </code>

                  </div>

                </div>

              </div>

              <div className="fix-status">

                <div>

                  <span className="check">
                    ✓
                  </span>

                  Pattern validated

                </div>

                <div>

                  <span className="check">
                    ✓
                  </span>

                  Source updated

                </div>

                <div>

                  <span className="check">
                    ✓
                  </span>

                  Retest triggered

                </div>

              </div>

            </>

          ) : (

            <EmptyState
              icon="✦"
              text="No AI-generated fix available yet"
            />

          )}

        </div>

      </section>

      {/* ======================================================
          OPTIMIZATION
      ====================================================== */}

      <section className="panel">

        <SectionHeading
          number="05"
          title="OPTIMIZATION ENGINE"
          description="Reduce VLM processing cost and latency"
        />

        <div className="optimization-grid">

          <OptimizationCard
            icon="◫"
            title="IMAGE FOCUS"
            from={
              imageOptimization?.original
                ? `${imageOptimization.original.width} × ${imageOptimization.original.height}`
                : "—"
            }
            to={
              imageOptimization?.focused
                ? `${imageOptimization.focused.width} × ${imageOptimization.focused.height}`
                : "—"
            }
            label="Focused anomaly region"
          />

          <OptimizationCard
            icon="≡"
            title="HTML REDUCTION"
            from={
              originalHtml
                ? originalHtml.toLocaleString()
                : "—"
            }
            to={
              reducedHtml
                ? reducedHtml.toLocaleString()
                : "—"
            }
            label={
              reduction
                ? `${reduction}% less HTML sent to VLM`
                : "Waiting for optimization"
            }
          />

        </div>

      </section>

      {/* ======================================================
          GITHUB & QA REVIEW
      ====================================================== */}

      <section className="panel github-panel">

        <SectionHeading
          number="06"
          title="GITHUB & QA REVIEW"
          description="Human-in-the-loop deployment control"
        />

        <div className="github-content">

          <div className="github-info">

            <div className="github-icon">
              ⌘
            </div>

            <div>

              <div className="github-label">
                REPOSITORY
              </div>

              <h3>
                OmniSight_Multimodal_UI_SelfHealing_RPA-Agent
              </h3>

              <div className="github-meta">

                <span>

                  ●{" "}

                  {status?.github?.branch ||
                    "main"}

                </span>

                <span>

                  {status?.github?.commit?.sha
                    ? `Commit ${status.github.commit.sha.slice(
                        0,
                        8
                      )}`
                    : "Awaiting commit"}

                </span>

              </div>

            </div>

          </div>

          {/* ==================================================
              QA REVIEW
          ================================================== */}

          <div className="qa-actions">

            <div className="qa-label">
              QA MANAGER REVIEW
            </div>

            {/* APPROVED */}

            {reviewStatus === "approved" ? (

              <div className="review-result approved">

                <div className="review-result-icon">
                  ✓
                </div>

                <div>

                  <strong>
                    AI HEALING APPROVED
                  </strong>

                  <span>
                     Pull request approved successfully
                  </span>

                </div>

              </div>

            ) : reviewStatus === "rejected" ? (

              /* REJECTED */

              <div className="review-result rejected">

                <div className="review-result-icon">
                  ×
                </div>

                <div>

                  <strong>
                    AI HEALING REJECTED
                  </strong>

                  <span>
                    Pull request rejected by QA manager
                  </span>

                </div>

              </div>

            ) : reviewStatus === "error" ? (

              /* ERROR */

              <div className="review-result review-error">

                <div className="review-result-icon">
                  !
                </div>

                <div>

                  <strong>
                    REVIEW FAILED
                  </strong>

                  <span>
                    Please try the review action again
                  </span>

                </div>

              </div>

            ) : latestIssue ? (

              /* ACTION BUTTONS */

              <div className="action-buttons">

                <button
                  className="approve"
                  onClick={() =>
                    reviewIssue(
                      latestIssue,
                      "approve"
                    )
                  }
                  disabled={
                    reviewLoading
                  }
                >

                  {reviewLoading
                    ? "APPROVING..."
                    : "✓ APPROVE"}

                </button>

                <button
                  className="reject"
                  onClick={() =>
                    reviewIssue(
                      latestIssue,
                      "reject"
                    )
                  }
                  disabled={
                    reviewLoading
                  }
                >

                  {reviewLoading
                    ? "PLEASE WAIT..."
                    : "× REJECT"}

                </button>

              </div>

            ) : (

              <span className="no-review">
                No pending review
              </span>

            )}

          </div>

        </div>

      </section>

      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer>

        <div>

          <span className="footer-logo">
            ✦
          </span>

          OMNISIGHT

        </div>

        <span>
          Multimodal UI Self-Healing & RPA Agent
        </span>

        <span>
          Powered by Playwright · Qwen · LangGraph · FastAPI
        </span>

      </footer>

    </div>
  );
}

// ============================================================
// COMPONENTS
// ============================================================

function MetricCard({
  icon,
  label,
  value,
  accent,
}) {
  return (
    <div
      className={`metric-card ${accent}`}
    >

      <div className="metric-icon">
        {icon}
      </div>

      <div>

        <div className="metric-label">
          {label}
        </div>

        <div className="metric-value">
          {value}
        </div>

      </div>

      <div className="metric-glow"></div>

    </div>
  );
}

function SectionHeading({
  number,
  title,
  description,
}) {
  return (
    <div className="section-heading">

      <div className="section-number">
        {number}
      </div>

      <div>

        <h2>
          {title}
        </h2>

        <p>
          {description}
        </p>

      </div>

    </div>
  );
}

function PipelineStep({
  icon,
  title,
  description,
  done,
}) {
  return (
    <div
      className={`pipeline-step ${
        done ? "done" : ""
      }`}
    >

      <div className="pipeline-icon">
        {done
          ? "✓"
          : icon}
      </div>

      <strong>
        {title}
      </strong>

      <span>
        {description}
      </span>

    </div>
  );
}

function PipelineLine() {
  return (
    <div className="pipeline-line">
      <span></span>
    </div>
  );
}

function OptimizationCard({
  icon,
  title,
  from,
  to,
  label,
}) {
  return (
    <div className="optimization-card">

      <div className="optimization-icon">
        {icon}
      </div>

      <div className="optimization-title">
        {title}
      </div>

      <div className="optimization-values">

        <div>

          <span>
            ORIGINAL
          </span>

          <strong>
            {from}
          </strong>

        </div>

        <div className="optimization-arrow">
          →
        </div>

        <div>

          <span>
            OPTIMIZED
          </span>

          <strong>
            {to}
          </strong>

        </div>

      </div>

      <div className="optimization-label">
        ✓ {label}
      </div>

    </div>
  );
}

function EmptyState({
  icon,
  text,
}) {
  return (
    <div className="empty-state">

      <div>
        {icon}
      </div>

      <span>
        {text}
      </span>

    </div>
  );
}

export default App;