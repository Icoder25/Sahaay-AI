"use client";

import { useEffect, useState } from "react";
import { useI18n } from "@/contexts/I18nContext";
import { getRoutines } from "@/lib/api";
import { useSession } from "@/hooks/useSession";
import type { Routine } from "@/lib/types";
import styles from "./CalendarView.module.css";

function formatTime(timing: string | null | undefined): string {
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

export function CalendarView() {
  const { tr } = useI18n();
  const sessionId = useSession();
  const [routines, setRoutines] = useState<Routine[]>([]);

  useEffect(() => {
    if (!sessionId) {
      return;
    }
    getRoutines(sessionId)
      .then(setRoutines)
      .catch(() => setRoutines([]));
  }, [sessionId]);

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>{tr("calendarTitle")}</h1>

      {routines.length === 0 ? (
        <p className={styles.empty}>{tr("calendarEmpty")}</p>
      ) : (
        <ul className={styles.grid}>
          {routines.map((routine) => (
            <li
              key={routine.id ?? `${routine.name}-${routine.timing}`}
              className={styles.event}
            >
              <div className={styles.eventTitle}>{routine.name}</div>
              <div className={styles.eventMeta}>
                {formatTime(routine.timing)} · {routine.frequency}
              </div>
              <span className={styles.badge}>{routine.type}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
