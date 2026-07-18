"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useI18n } from "@/contexts/I18nContext";
import { useAuth } from "@/contexts/AuthContext";
import {
  createElder,
  listElders,
  listReminders,
  reminderToRoutine,
} from "@/lib/api";
import type { Routine } from "@/lib/types";
import styles from "./FamilyDashboard.module.css";

function SummaryRow({
  label,
  value,
  alert = false,
}: {
  label: string;
  value: string;
  alert?: boolean;
}) {
  return (
    <div className={styles.summaryItem}>
      <span className={styles.summaryLabel}>{label}</span>
      <span className={`${styles.summaryValue} ${alert ? styles.attention : ""}`}>
        {value}
      </span>
    </div>
  );
}

function ElderCard({
  elderId,
  displayName,
}: {
  elderId: string;
  displayName: string;
}) {
  const { tr } = useI18n();
  const [routines, setRoutines] = useState<Routine[]>([]);

  useEffect(() => {
    listReminders(elderId)
      .then((rows) => setRoutines(rows.map(reminderToRoutine)))
      .catch(() => setRoutines([]));
  }, [elderId]);

  const medicationRoutine = routines.some((r) => r.type === "medication");

  return (
    <article className={styles.section}>
      <h3 className={styles.sectionTitle}>{displayName}</h3>

      <div className={styles.summaryGrid}>
        <SummaryRow
          label={tr("medicinesToday")}
          value={medicationRoutine ? `${routines.filter((r) => r.type === "medication").length} set` : tr("unknown")}
        />
        <SummaryRow
          label={tr("yourRoutines")}
          value={String(routines.length)}
        />
      </div>

      {routines.length > 0 ? (
        <ul style={{ marginTop: 12, paddingLeft: 18 }}>
          {routines.slice(0, 6).map((routine) => (
            <li key={`${routine.name}-${routine.timing}`}>
              {routine.name}
              {routine.timing ? ` · ${routine.timing}` : ""}
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ marginTop: 12 }}>No reminders yet for this elder.</p>
      )}
    </article>
  );
}

export function FamilyDashboard() {
  const { tr } = useI18n();
  const router = useRouter();
  const { care, isAuthenticated, user } = useAuth();
  const [elders, setElders] = useState<Array<{ id: string; full_name: string }>>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    if (!care?.familyId) return;
    const rows = await listElders(care.familyId);
    setElders(rows.map((e) => ({ id: e.id, full_name: e.full_name })));
  }, [care?.familyId]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    refresh().catch((err) =>
      setError(err instanceof Error ? err.message : "Failed to load elders"),
    );
  }, [isAuthenticated, refresh, router]);

  async function handleAddElder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!care?.familyId) return;
    const form = new FormData(event.currentTarget);
    const name = String(form.get("elderName") ?? "").trim();
    if (!name) return;
    setBusy(true);
    setError(null);
    try {
      await createElder(care.familyId, { full_name: name });
      event.currentTarget.reset();
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add elder");
    } finally {
      setBusy(false);
    }
  }

  if (!care) {
    return (
      <div className={styles.page}>
        <p>{tr("noElders")}</p>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>{tr("familyWelcome")}</h1>
        <p className={styles.invite}>
          Signed in as <strong>{user?.fullName ?? user?.email}</strong>
        </p>
      </div>

      {error ? <p className={styles.notificationBody}>{error}</p> : null}

      {elders.length === 0 ? (
        <p>{tr("noElders")}</p>
      ) : (
        <div className={styles.grid}>
          {elders.map((elder) => (
            <ElderCard
              key={elder.id}
              elderId={elder.id}
              displayName={elder.full_name}
            />
          ))}
        </div>
      )}

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>{tr("addElder")}</h2>
        <form className={styles.form} onSubmit={handleAddElder}>
          <input
            name="elderName"
            className={styles.input}
            placeholder={tr("elderName")}
            required
          />
          <button type="submit" className={styles.button} disabled={busy}>
            {busy ? "Saving…" : tr("addElder")}
          </button>
        </form>
      </section>
    </div>
  );
}
