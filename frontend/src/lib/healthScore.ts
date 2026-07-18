import type { WellnessCheck } from "@/lib/store";

const moodScores: Record<string, number> = {
  great: 100,
  good: 85,
  okay: 70,
  low: 50,
  poor: 35,
};

const appetiteScores: Record<string, number> = {
  good: 100,
  normal: 80,
  poor: 55,
  skipped: 40,
};

const sleepScores: Record<string, number> = {
  good: 100,
  fair: 75,
  poor: 50,
  restless: 45,
};

export interface HealthScoreResult {
  score: number;
  summary: string;
  needsAttention: boolean;
}

export function computeHealthScore(
  wellnessChecks: WellnessCheck[],
): HealthScoreResult {
  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);

  const recent = wellnessChecks.filter(
    (check) => check.timestamp >= todayStart.getTime() - 7 * 86400000,
  );

  let wellnessScore = 75;
  if (recent.length > 0) {
    const latest = recent[0];
    wellnessScore =
      (moodScores[latest.mood] ?? 70) * 0.4 +
      (appetiteScores[latest.appetite] ?? 70) * 0.3 +
      (sleepScores[latest.sleepQuality] ?? 70) * 0.3;
  }

  const score = Math.round(wellnessScore);
  const needsAttention = score < 60;

  let summary = "Mostly stable with gentle monitoring.";
  if (score >= 85) {
    summary = "Doing well overall. Routines and wellness look stable.";
  } else if (score < 60) {
    summary = "Needs attention — consider a caring check-in today.";
  }

  return { score, summary, needsAttention };
}

export function isToday(timestamp: number): boolean {
  const date = new Date(timestamp);
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}
