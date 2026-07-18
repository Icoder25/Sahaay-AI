"use client";

import { useI18n } from "@/contexts/I18nContext";
import type { HealthScoreResult } from "@/lib/healthScore";
import styles from "./HealthScoreCard.module.css";

interface HealthScoreCardProps {
  result: HealthScoreResult;
}

export function HealthScoreCard({ result }: HealthScoreCardProps) {
  const { tr } = useI18n();

  return (
    <div className={styles.card}>
      <div className={styles.scoreValue}>{result.score}</div>
      <div className={styles.scoreLabel}>{tr("healthScore")}</div>
      <p className={styles.summary}>{result.summary}</p>
      {result.needsAttention ? (
        <p className={styles.alert}>
          {tr("needsAttention")}: {tr("yes")}
        </p>
      ) : null}
    </div>
  );
}
