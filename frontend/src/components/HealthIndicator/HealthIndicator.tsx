"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";
import styles from "./HealthIndicator.module.css";

type HealthState = "loading" | "ok" | "degraded" | "offline";

export function HealthIndicator() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [state, setState] = useState<HealthState>("loading");

  useEffect(() => {
    let cancelled = false;

    async function checkHealth() {
      try {
        const result = await getHealth();
        if (cancelled) {
          return;
        }
        setHealth(result);
        const services = Object.values(result.services);
        const allUp = services.length > 0 && services.every(Boolean);
        setState(allUp ? "ok" : "degraded");
      } catch {
        if (!cancelled) {
          setState("offline");
        }
      }
    }

    checkHealth();
    return () => {
      cancelled = true;
    };
  }, []);

  const label =
    state === "loading"
      ? "Checking backend…"
      : state === "ok"
        ? "Backend connected"
        : state === "degraded"
          ? "Backend connected (some services unavailable)"
          : "Backend offline";

  return (
    <div className={styles.wrapper} title={label}>
      <span
        className={`${styles.dot} ${styles[state]}`}
        aria-hidden="true"
      />
      <span className={styles.label}>{label}</span>
      {health && state !== "offline" ? (
        <span className={styles.services}>
          {Object.entries(health.services).map(([name, available]) => (
            <span
              key={name}
              className={`${styles.service} ${available ? styles.available : styles.unavailable}`}
            >
              {name}
            </span>
          ))}
        </span>
      ) : null}
    </div>
  );
}
