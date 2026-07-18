"use client";

import { useState } from "react";
import { useI18n } from "@/contexts/I18nContext";
import {
  addNotification,
  getFamily,
  logActivity,
} from "@/lib/store";
import styles from "./SosButton.module.css";

interface SosButtonProps {
  elderProfileId: string;
  elderName: string;
}

export function SosButton({ elderProfileId, elderName }: SosButtonProps) {
  const { tr } = useI18n();
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  function handleSos() {
    if (!window.confirm(tr("sosConfirm"))) {
      return;
    }

    setLoading(true);
    const family = getFamily();
    logActivity(
      elderProfileId,
      "sos",
      "SOS alert sent",
      `${elderName} requested urgent help.`,
    );
    addNotification({
      title: `SOS from ${elderName}`,
      body: `${elderName} pressed the emergency button and may need immediate help.`,
      notificationType: "sos",
      elderProfileId,
    });
    if (family) {
      window.dispatchEvent(new Event("sahaay-store"));
    }
    setSent(true);
    setLoading(false);
  }

  return (
    <div>
      <button
        type="button"
        className={styles.button}
        onClick={handleSos}
        disabled={loading || sent}
      >
        {tr("sos")}
      </button>
      {sent ? <p className={styles.sent}>{tr("sosSent")}</p> : null}
    </div>
  );
}
