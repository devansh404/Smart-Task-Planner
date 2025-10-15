import { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

type Task = {
  id: number;
  name: string;
  timeline: string;
  dependencies: string[];
};

const TaskBreakdown = ({
  tasks,
  onBack,
}: {
  tasks: Task[];
  onBack: () => void;
}) => {
  return (
    <div className="task-breakdown-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="app-title generated-plan-title">Generated Task Plan</h2>
        <button className="btn btn-secondary export-button" onClick={onBack}>
          &larr; New Plan
        </button>
      </div>

      {Array.isArray(tasks) &&
        tasks.map((task, index) => (
          <div key={task.id || index} className="task-card">
            <p className="task-name mb-2">{task.name}</p>
            <p className="task-details mb-0 text-white-50">
              <strong>Timeline:</strong> {task.timeline}
            </p>
          </div>
        ))}
    </div>
  );
};

const App = () => {
  const [goal, setGoal] = useState<string>("");
  const [deadline, setDeadline] = useState<string>("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [showBreakdown, setShowBreakdown] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGeneratePlan = async () => {
    if (!goal) {
      setError("Please enter a goal before generating a plan.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/generate-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal, deadline }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Backend error: ${response.status} ${text}`);
      }

      const data = await response.json();

      // Basic validation: expect an array
      if (Array.isArray(data)) {
        setTasks(data as Task[]);
        setShowBreakdown(true);
      } else {
        throw new Error("Unexpected response format from backend");
      }
    } catch (err) {
      console.error("Error generating plan:", err);
      setError(
        "Sorry, something went wrong while generating the plan. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    setShowBreakdown(false);
    setTasks([]);
    setError(null);
  };

  return (
    <>
      <div className="app-body">
        <header className="app-header text-center">
          <h1 className="app-title">Smart Task Planner</h1>
          <p className="app-subtitle">
            Turn a goal into a clear, dependency-aware task plan with a
            timeline. Just state your goal and deadline.
          </p>
        </header>

        <main className="container">
          <div className="main-container">
            <div className="mb-4">
              <label htmlFor="goal" className="custom-form-label">
                Goal
              </label>
              <textarea
                id="goal"
                className="form-control custom-form-control"
                rows={4}
                placeholder="e.g., Launch a product"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
              ></textarea>
              <small className="form-text custom-form-text">
                Be specific about scope and constraints for sharper tasks.
              </small>
            </div>

            <div className="mb-4">
              <label htmlFor="deadline" className="custom-form-label">
                Deadline
              </label>
              <div className="date-input-container">
                <input
                  type="text"
                  id="deadline"
                  className="form-control custom-form-control date-input"
                  placeholder="in 2 weeks"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                />
              </div>
            </div>

            <div className="d-flex gap-2">
              <button
                className="btn btn-primary generate-button"
                onClick={handleGeneratePlan}
                disabled={isLoading}
              >
                {isLoading ? "Generating..." : "Generate Plan"}
              </button>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="container mt-3">
              <div className="alert alert-danger">{error}</div>
            </div>
          )}

          {/* Tasks breakdown view */}
          {showBreakdown && <TaskBreakdown tasks={tasks} onBack={handleBack} />}
        </main>
      </div>
    </>
  );
};

export default App;
