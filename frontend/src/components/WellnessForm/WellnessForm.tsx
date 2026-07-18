"use client";

import { FormEvent } from "react";
import { useI18n } from "@/contexts/I18nContext";
import { saveWellnessCheck } from "@/lib/store";
import styles from "./WellnessForm.module.css";

interface WellnessFormProps {
  elderProfileId: string;
  onSaved?: () => void;
}

export function WellnessForm({ elderProfileId, onSaved }: WellnessFormProps) {
  const { tr } = useI18n();

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    saveWellnessCheck({
      elderProfileId,
      mood: String(form.get("mood")),
      appetite: String(form.get("appetite")),
      sleepQuality: String(form.get("sleepQuality")),
    });
    event.currentTarget.reset();
    window.dispatchEvent(new Event("sahaay-store"));
    onSaved?.();
  }

  return (
    <section className={styles.wrapper}>
      <h2 className={styles.title}>{tr("wellnessTitle")}</h2>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.field}>
          <label className={styles.label} htmlFor="mood">
            {tr("mood")}
          </label>
          <select id="mood" name="mood" className={styles.select} defaultValue="good">
            <option value="great">Great</option>
            <option value="good">Good</option>
            <option value="okay">Okay</option>
            <option value="low">Low</option>
            <option value="poor">Poor</option>
          </select>
        </div>
        <div className={styles.field}>
          <label className={styles.label} htmlFor="appetite">
            {tr("appetite")}
          </label>
          <select id="appetite" name="appetite" className={styles.select} defaultValue="normal">
            <option value="good">Good</option>
            <option value="normal">Normal</option>
            <option value="poor">Poor</option>
            <option value="skipped">Skipped meals</option>
          </select>
        </div>
        <div className={styles.field}>
          <label className={styles.label} htmlFor="sleepQuality">
            {tr("sleep")}
          </label>
          <select id="sleepQuality" name="sleepQuality" className={styles.select} defaultValue="fair">
            <option value="good">Good</option>
            <option value="fair">Fair</option>
            <option value="poor">Poor</option>
            <option value="restless">Restless</option>
          </select>
        </div>
        <button type="submit" className={styles.submit}>
          {tr("wellnessSubmit")}
        </button>
      </form>
    </section>
  );
}
