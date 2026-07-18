"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useI18n } from "@/contexts/I18nContext";
import { useAuth } from "@/contexts/AuthContext";
import { listReminders, reminderToRoutine } from "@/lib/api";
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
  const router = useRouter();
  const { care, isAuthenticated } = useAuth();
  const [routines, setRoutines] = useState<Routine[]>([]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    if (!care?.elderId) return;
    listReminders(care.elderId)
      .then((rows) => setRoutines(rows.map(reminderToRoutine)))
      .catch(() => setRoutines([]));
  }, [care?.elderId, isAuthenticated, router]);

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
