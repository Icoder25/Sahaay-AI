"use client";

import { useSyncExternalStore } from "react";
import { getOrCreateSessionId } from "@/lib/session";

function subscribe() {
  return () => {};
}

function getSnapshot() {
  return getOrCreateSessionId();
}

function getServerSnapshot() {
  return "";
}

export function useSession() {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
