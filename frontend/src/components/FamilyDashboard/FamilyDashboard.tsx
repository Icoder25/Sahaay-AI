"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useI18n } from "@/contexts/I18nContext";
import { ActivityTimeline } from "@/components/ActivityTimeline/ActivityTimeline";
import { HealthScoreCard } from "@/components/HealthScoreCard/HealthScoreCard";
import { getRoutines } from "@/lib/api";
import { computeHealthScore, isToday } from "@/lib/healthScore";
import {
  addElderProfile,
  getActivities,
  getNotifications,
  getWellnessChecks,
  type ElderProfile,
} from "@/lib/store";
import type { Routine } from "@/lib/types";
import { useFamily } from "@/hooks/useFamily";
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

function ElderCard({ profile }: { profile: ElderProfile }) {
  const { tr } = useI18n();
  const [routines, setRoutines] = useState<Routine[]>([]);

  useEffect(() => {
    getRoutines(profile.sessionId)
      .then(setRoutines)
      .catch(() => setRoutines([]));
  }, [profile.sessionId]);

  const activities = getActivities().filter(
    (item) => item.elderProfileId === profile.id,
  );
  const wellness = getWellnessChecks().filter(
    (item) => item.elderProfileId === profile.id,
  );
  const health = computeHealthScore(wellness);

  const todayActivities = activities.filter((item) => isToday(item.timestamp));
  const todayWellness = wellness.find((item) => isToday(item.timestamp));
  const medicationRoutine = routines.some((r) => r.type === "medication");
  const medicineActivity = todayActivities.some(
    (item) =>
      item.activityType === "reminder" ||
      item.title.toLowerCase().includes("medicine"),
  );
  const ateWell = todayWellness
    ? todayWellness.appetite === "good" || todayWellness.appetite === "normal"
    : null;
  const sosToday = todayActivities.some((item) => item.activityType === "sos");

  return (
    <article className={styles.section}>
      <h3 className={styles.sectionTitle}>{profile.displayName}</h3>

      <div className={styles.summaryGrid}>
        <SummaryRow
          label={tr("medicinesToday")}
          value={
            medicineActivity
              ? tr("yes")
              : medicationRoutine
                ? tr("no")
                : tr("unknown")
          }
          alert={medicationRoutine && !medicineActivity}
        />
        <SummaryRow
          label={tr("ateToday")}
          value={ateWell === null ? tr("unknown") : ateWell ? tr("yes") : tr("no")}
          alert={ateWell === false}
        />
        <SummaryRow
          label={tr("feelingToday")}
          value={todayWellness?.mood ?? tr("unknown")}
        />
        <SummaryRow
          label={tr("unusualToday")}
          value={sosToday ? tr("yes") : tr("no")}
          alert={sosToday}
        />
        <SummaryRow
          label={tr("needsAttention")}
          value={health.needsAttention || sosToday ? tr("yes") : tr("no")}
          alert={health.needsAttention || sosToday}
        />
      </div>

      <div style={{ marginTop: 16 }}>
        <HealthScoreCard result={health} />
      </div>
    </article>
  );
}

export function FamilyDashboard() {
  const { tr } = useI18n();
  const family = useFamily();
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    function refresh() {
      setRefreshKey((value) => value + 1);
    }
    window.addEventListener("sahaay-store", refresh);
    return () => window.removeEventListener("sahaay-store", refresh);
  }, []);

  const notifications = useMemo(
    () => getNotifications().slice(0, 8),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [refreshKey],
  );

  const allActivities = useMemo(() => {
    if (!family) {
      return [];
    }
    const ids = new Set(family.elderProfiles.map((profile) => profile.id));
    return getActivities().filter((item) => ids.has(item.elderProfileId));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [family, refreshKey]);

  function handleAddElder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const name = String(form.get("elderName") ?? "").trim();
    const sessionId = String(form.get("sessionId") ?? "").trim();
    if (!name) {
      return;
    }
    addElderProfile(name, sessionId || crypto.randomUUID());
    window.dispatchEvent(new Event("sahaay-store"));
    event.currentTarget.reset();
  }

  if (!family) {
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
        {family.inviteCode ? (
          <p className={styles.invite}>
            {tr("inviteShare")}: <strong>{family.inviteCode}</strong>
          </p>
        ) : null}
      </div>

      {family.elderProfiles.length === 0 ? (
        <p>{tr("noElders")}</p>
      ) : (
        <div className={styles.grid}>
          {family.elderProfiles.map((profile) => (
            <ElderCard key={profile.id} profile={profile} />
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
          <input
            name="sessionId"
            className={styles.input}
            placeholder={tr("sessionId")}
          />
          <button type="submit" className={styles.button}>
            {tr("addElder")}
          </button>
        </form>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>{tr("notifications")}</h2>
        <div className={styles.notifications}>
          {notifications.length === 0 ? (
            <p className={styles.notificationBody}>No notifications yet.</p>
          ) : (
            notifications.map((item) => (
              <div
                key={item.id}
                className={`${styles.notification} ${!item.isRead ? styles.notificationUnread : ""}`}
              >
                <div className={styles.notificationTitle}>{item.title}</div>
                <p className={styles.notificationBody}>{item.body}</p>
              </div>
            ))
          )}
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>{tr("activityTimeline")}</h2>
        <ActivityTimeline activities={allActivities} />
      </section>
    </div>
  );
}
