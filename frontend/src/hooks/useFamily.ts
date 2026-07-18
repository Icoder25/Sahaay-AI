"use client";

import { useSyncExternalStore } from "react";
import { createCachedSnapshot } from "@/lib/syncSnapshot";
import { getFamily } from "@/lib/store";
import type { ElderProfile, Family } from "@/lib/store";
import { getOrCreateSessionId } from "@/lib/session";
import { addElderProfile } from "@/lib/store";

const familyStore = createCachedSnapshot<Family | null>(
  getFamily,
  (onStoreChange) => {
    window.addEventListener("sahaay-store", onStoreChange);
    return () => window.removeEventListener("sahaay-store", onStoreChange);
  },
  () => null,
);

export function useFamily() {
  return useSyncExternalStore(
    familyStore.subscribe,
    familyStore.getSnapshot,
    familyStore.getServerSnapshot,
  );
}

export function useElderProfile(sessionId: string): ElderProfile | null {
  const family = useFamily();

  if (!sessionId) {
    return null;
  }

  return (
    family?.elderProfiles.find((profile) => profile.sessionId === sessionId) ??
    null
  );
}

export function ensureElderProfile(
  sessionId: string,
  displayName = "Elder",
): ElderProfile {
  const family = getFamily();
  const existing = family?.elderProfiles.find(
    (profile) => profile.sessionId === sessionId,
  );
  if (existing) {
    return existing;
  }
  const profile = addElderProfile(
    displayName,
    sessionId || getOrCreateSessionId(),
  );
  window.dispatchEvent(new Event("sahaay-store"));
  return profile;
}
