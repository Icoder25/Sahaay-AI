"use client";

import { useSyncExternalStore } from "react";
import { createCachedPrimitiveSnapshot } from "@/lib/syncSnapshot";
import { getOrCreateSessionId } from "@/lib/session";

const sessionStore = createCachedPrimitiveSnapshot<string>(
  getOrCreateSessionId,
  () => () => {},
  () => "",
);

export function useSession() {
  return useSyncExternalStore(
    sessionStore.subscribe,
    sessionStore.getSnapshot,
    sessionStore.getServerSnapshot,
  );
}
