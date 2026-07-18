"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";
import styles from "./HealthIndicator.module.css";

type HealthState = "loading" | "ok" | "degraded" | "offline";

/** Services required for the elder chat demo to work. */
const CORE_SERVICES = ["anthropic", "database"] as const;

function deriveState(result: HealthResponse): Exclude<HealthState, "loading" | "offline"> {
  if (result.status === "degraded") {
    return "degraded";
  }
  const coreOk = CORE_SERVICES.every((key) => result.services[key] !== false);
  return coreOk ? "ok" : "degraded";
}

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
        setState(deriveState(result));
      } catch {
        if (!cancelled) {
          setState("offline");
        }
      }
    }

    checkHealth();
    const timer = window.setInterval(checkHealth, 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  const label =
    state === "loading"
      ? "Checking backend…"
      : state === "ok"
        ? "Backend connected"
        : state === "degraded"
          ? "Backend connected (some services unavailable)"
          : "Backend offline — start API on :8000";

  return (
    <div className={styles.wrapper} title={label}>
      <span
        className={`${styles.dot} ${styles[state]}`}
        aria-hidden="true"
      />
      <span className={styles.label}>{label}</span>
      {health && state !== "offline" ? (
        <span className={styles.services}>
          {Object.entries(health.services)
            .filter(([name]) =>
              ["anthropic", "exa", "elevenlabs", "database"].includes(name),
            )
            .map(([name, available]) => (
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
