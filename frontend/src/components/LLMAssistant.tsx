import { useState } from "react";
import { api, SimulateResponse } from "../api/client";

interface LLMAssistantProps {
  simulation: SimulateResponse | null;
}

export function LLMAssistant({ simulation }: LLMAssistantProps) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("Explain the current model result.");
  const [answer, setAnswer] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true);
    setAnswer(null);
    setError(null);
    try {
      const result = await api.llmExplain({
        question,
        context: simulation
          ? {
              qnet_C_per_F: simulation.qnet_C_per_F,
              apd90_ms: simulation.apd90_ms,
              phi_C_per_F: simulation.phi_C_per_F,
              credibility: simulation.credibility,
            }
          : undefined,
      });
      setAnswer(result.answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "LLM request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`llm-assistant ${open ? "is-open" : ""}`}>
      {open && (
        <div className="llm-panel" role="dialog" aria-label="Ask Twin">
          <div className="llm-panel-head">
            <div>
              <span className="eyebrow">Optional research aid</span>
              <h2>Ask Twin</h2>
            </div>
            <button className="llm-close" onClick={() => setOpen(false)} aria-label="Close Ask Twin">×</button>
          </div>
          <textarea value={question} onChange={(event) => setQuestion(event.target.value)} maxLength={2000} rows={3} aria-label="Question" />
          <button className="primary llm-ask" onClick={ask} disabled={loading || !question.trim()}>
            {loading ? "Thinking..." : "Ask"}
          </button>
          {error && <div className="llm-error">{error}</div>}
          {answer && <div className="llm-answer">{answer}</div>}
          <p className="llm-disclaimer">Research explanation only. Not clinically validated or for clinical decision-making.</p>
        </div>
      )}
      <button className="llm-launch" onClick={() => setOpen((value) => !value)} aria-label="Open Ask Twin">
        <span aria-hidden="true">✦</span> Ask Twin
      </button>
    </div>
  );
}