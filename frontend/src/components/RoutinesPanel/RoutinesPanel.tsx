import type { Routine } from "@/lib/types";
import styles from "./RoutinesPanel.module.css";

interface RoutinesPanelProps {
  routines: Routine[];
  isLoading?: boolean;
  onDemoReminder: () => void;
  reminderLoading?: boolean;
}

function formatTiming(timing: string | null | undefined): string {
  if (!timing) {
    return "Any time";
  }
  const [hours, minutes] = timing.split(":");
  const hour = Number(hours);
  if (Number.isNaN(hour)) {
    return timing;
  }
  const date = new Date();
  date.setHours(hour, Number(minutes) || 0, 0, 0);
  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function priorityLabel(priority: string): string {
  if (priority === "critical") {
    return "Important";
  }
  if (priority === "high") {
    return "High";
  }
  return "Normal";
}

export function RoutinesPanel({
  routines,
  isLoading = false,
  onDemoReminder,
  reminderLoading = false,
}: RoutinesPanelProps) {
  return (
    <aside className={styles.panel} aria-label="Your routines">
      <div className={styles.header}>
        <h2 className={styles.title}>Your routines</h2>
        <p className={styles.subtitle}>
          Sahaay remembers what you share — medicines, bills, and daily habits.
        </p>
      </div>

      <button
        type="button"
        className={styles.reminderButton}
        onClick={onDemoReminder}
        disabled={reminderLoading || routines.length === 0}
      >
        {reminderLoading ? "Sending reminder…" : "Try demo reminder"}
      </button>

      {routines.length === 0 ? (
        <div className={styles.empty}>
          <p>No routines yet.</p>
          <p className={styles.emptyHint}>
            Tell Sahaay about your medicines or daily tasks in the chat.
          </p>
        </div>
      ) : (
        <ul className={styles.list}>
          {routines.map((routine) => (
            <li
              key={routine.id ?? `${routine.name}-${routine.timing}`}
              className={styles.card}
            >
              <div className={styles.cardHeader}>
                <span className={styles.name}>{routine.name}</span>
                <span
                  className={`${styles.priority} ${styles[routine.priority] ?? styles.normal}`}
                >
                  {priorityLabel(routine.priority)}
                </span>
              </div>
              <dl className={styles.meta}>
                <div>
                  <dt>Type</dt>
                  <dd>{routine.type}</dd>
                </div>
                <div>
                  <dt>When</dt>
                  <dd>{formatTiming(routine.timing)}</dd>
                </div>
                <div>
                  <dt>Frequency</dt>
                  <dd>{routine.frequency}</dd>
                </div>
              </dl>
              {routine.notes ? (
                <p className={styles.notes}>{routine.notes}</p>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {isLoading ? (
        <p className={styles.loading} role="status">
          Refreshing routines…
        </p>
      ) : null}
    </aside>
  );
}
