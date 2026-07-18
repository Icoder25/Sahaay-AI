import type { Activity } from "@/lib/store";
import styles from "./ActivityTimeline.module.css";

interface ActivityTimelineProps {
  activities: Activity[];
}

function formatTime(timestamp: number): string {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(timestamp));
}

export function ActivityTimeline({ activities }: ActivityTimelineProps) {
  if (activities.length === 0) {
    return <p className={styles.empty}>No activity recorded yet.</p>;
  }

  return (
    <ul className={styles.wrapper}>
      {activities.map((activity) => (
        <li key={activity.id} className={styles.item}>
          <div className={styles.header}>
            <span className={styles.title}>{activity.title}</span>
            <time className={styles.time}>{formatTime(activity.timestamp)}</time>
          </div>
          {activity.description ? (
            <p className={styles.description}>{activity.description}</p>
          ) : null}
        </li>
      ))}
    </ul>
  );
}
