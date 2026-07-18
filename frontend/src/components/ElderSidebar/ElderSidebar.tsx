"use client";

import { useEffect } from "react";
import { SosButton } from "@/components/SosButton/SosButton";
import { WellnessForm } from "@/components/WellnessForm/WellnessForm";
import { ensureElderProfile, useElderProfile } from "@/hooks/useFamily";
import { useAuth } from "@/contexts/AuthContext";
import styles from "./ElderSidebar.module.css";

interface ElderSidebarProps {
  sessionId: string;
}

export function ElderSidebar({ sessionId }: ElderSidebarProps) {
  const { user } = useAuth();
  const profile = useElderProfile(sessionId);

  useEffect(() => {
    if (!sessionId || profile) return;
    ensureElderProfile(sessionId, user?.fullName ?? "Elder");
  }, [sessionId, profile, user?.fullName]);

  if (!profile) {
    return null;
  }

  return (
    <aside className={styles.sidebar} aria-label="Elder care tools">
      <SosButton elderProfileId={profile.id} elderName={profile.displayName} />
      <WellnessForm elderProfileId={profile.id} />
    </aside>
  );
}
