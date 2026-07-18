"use client";

import { useMemo } from "react";
import { SosButton } from "@/components/SosButton/SosButton";
import { WellnessForm } from "@/components/WellnessForm/WellnessForm";
import { ensureElderProfile } from "@/hooks/useFamily";
import { useAuth } from "@/contexts/AuthContext";
import styles from "./ElderSidebar.module.css";

interface ElderSidebarProps {
  sessionId: string;
}

export function ElderSidebar({ sessionId }: ElderSidebarProps) {
  const { user } = useAuth();

  const profile = useMemo(() => {
    if (!sessionId) {
      return null;
    }
    return ensureElderProfile(sessionId, user?.fullName ?? "Elder");
  }, [sessionId, user?.fullName]);

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
