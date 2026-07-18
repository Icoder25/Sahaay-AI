"use client";

import Link from "next/link";
import { useI18n } from "@/contexts/I18nContext";
import styles from "./Landing.module.css";

export function Landing() {
  const { tr } = useI18n();

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>{tr("landingTitle")}</h1>
        <p className={styles.subtitle}>{tr("landingSubtitle")}</p>
        <div className={styles.actions}>
          <Link href="/elder" className={styles.primary}>
            {tr("landingElderCta")}
          </Link>
          <Link href="/family" className={styles.secondary}>
            {tr("landingFamilyCta")}
          </Link>
        </div>
        <Link href="/elder" className={styles.tertiary}>
          {tr("landingDemoCta")} →
        </Link>
      </div>
    </div>
  );
}
