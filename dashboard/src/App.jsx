import { useEffect, useState } from "react";
import "./index.css";

const API_URL = "http://localhost:8000";

function App() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const fetchIssues = async () => {
    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/dashboard/issues`);

      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const data = await response.json();

      setIssues(data.issues || []);
    } catch (error) {
      console.error(error);
      setMessage(
        "Unable to connect to OmniSight API. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, []);

  const approvePR = async (issue) => {
    try {
      setMessage("Approving AI-generated fix...");

      const response = await fetch(`${API_URL}/github/pr/approve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          issue_id: issue.id,
          pr_number: issue.pr_number,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Approval failed");
      }

      setMessage("✅ Pull Request approved successfully.");

      fetchIssues();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    }
  };

  const rejectPR = async (issue) => {
    try {
      setMessage("Rejecting AI-generated fix...");

      const response = await fetch(`${API_URL}/github/pr/reject`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          issue_id: issue.id,
          pr_number: issue.pr_number,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Rejection failed");
      }

      setMessage("❌ Pull Request rejected.");

      fetchIssues();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>OmniSight</h1>
          <p>Multimodal UI Self-Healing QA Dashboard</p>
        </div>

        <button className="refresh-button" onClick={fetchIssues}>
          ↻ Refresh
        </button>
      </header>

      <main className="container">
        <section className="summary">
          <div className="summary-card">
            <span className="summary-title">Issues</span>
            <strong>{issues.length}</strong>
          </div>

          <div className="summary-card">
            <span className="summary-title">AI Fixes</span>
            <strong>
              {issues.filter((issue) => issue.fix).length}
            </strong>
          </div>

          <div className="summary-card">
            <span className="summary-title">Pending Review</span>
            <strong>
              {
                issues.filter(
                  (issue) => issue.status === "pending"
                ).length
              }
            </strong>
          </div>
        </section>

        {message && (
          <div className="message">
            {message}
          </div>
        )}

        {loading ? (
          <div className="loading">
            Loading OmniSight results...
          </div>
        ) : issues.length === 0 ? (
          <div className="empty">
            <h2>No AI-generated fixes yet</h2>
            <p>
              Run the OmniSight healing pipeline from FastAPI.
            </p>
          </div>
        ) : (
          <section className="issues">
            {issues.map((issue) => (
              <IssueCard
                key={issue.id}
                issue={issue}
                onApprove={approvePR}
                onReject={rejectPR}
              />
            ))}
          </section>
        )}
      </main>
    </div>
  );
}

function IssueCard({ issue, onApprove, onReject }) {
  return (
    <article className="issue-card">
      <div className="issue-header">
        <div>
          <span className={`severity ${issue.severity || "medium"}`}>
            {(issue.severity || "medium").toUpperCase()}
          </span>

          <h2>{issue.title || "UI Issue Detected"}</h2>
        </div>

        <span className={`status ${issue.status || "pending"}`}>
          {issue.status || "pending"}
        </span>
      </div>

      <div className="issue-content">
        <section>
          <h3>🤖 AI Detection</h3>

          <p>
            {issue.description ||
              issue.issue ||
              "No issue description available."}
          </p>
        </section>

        {issue.screenshot && (
          <section>
            <h3>📸 Screenshot</h3>

            <img
              className="screenshot"
              src={
                issue.screenshot.startsWith("http")
                  ? issue.screenshot
                  : `${API_URL}${issue.screenshot}`
              }
              alt="Detected UI issue"
            />
          </section>
        )}

        {issue.fix && (
          <section>
            <h3>🛠️ AI Proposed Fix</h3>

            <div className="code-change">
              <div className="code-block old">
                <strong>Before</strong>
                <pre>{issue.fix.old}</pre>
              </div>

              <div className="arrow">→</div>

              <div className="code-block new">
                <strong>After</strong>
                <pre>{issue.fix.new}</pre>
              </div>
            </div>
          </section>
        )}

        {issue.pr_number && (
          <section className="pr-section">
            <h3>🔀 GitHub Pull Request</h3>

            <p>
              PR #{issue.pr_number}
            </p>

            {issue.pr_url && (
              <a
                href={issue.pr_url}
                target="_blank"
                rel="noreferrer"
              >
                View Pull Request →
              </a>
            )}
          </section>
        )}
      </div>

      {issue.status === "pending" && (
        <div className="actions">
          <button
            className="approve"
            onClick={() => onApprove(issue)}
          >
            ✓ Approve Fix
          </button>

          <button
            className="reject"
            onClick={() => onReject(issue)}
          >
            ✕ Reject Fix
          </button>
        </div>
      )}
    </article>
  );
}

export default App;