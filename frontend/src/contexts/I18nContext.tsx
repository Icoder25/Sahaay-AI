"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
} from "react";
import type { Locale } from "@/lib/i18n/translations";
import { t } from "@/lib/i18n/translations";
import { createCachedPrimitiveSnapshot } from "@/lib/syncSnapshot";

const LOCALE_KEY = "sahaay_locale";

interface I18nContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  tr: (key: Parameters<typeof t>[1]) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

function readLocale(): Locale {
  const stored = localStorage.getItem(LOCALE_KEY);
  if (stored === "hi" || stored === "gu" || stored === "en") {
    return stored;
  }
  return "en";
}

const localeStore = createCachedPrimitiveSnapshot<Locale>(
  readLocale,
  (onStoreChange) => {
    window.addEventListener("sahaay-locale", onStoreChange);
    return () => window.removeEventListener("sahaay-locale", onStoreChange);
  },
  () => "en",
);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const locale = useSyncExternalStore(
    localeStore.subscribe,
    localeStore.getSnapshot,
    localeStore.getServerSnapshot,
  );

  const setLocale = useCallback((next: Locale) => {
    localStorage.setItem(LOCALE_KEY, next);
    window.dispatchEvent(new Event("sahaay-locale"));
  }, []);

  const tr = useCallback(
    (key: Parameters<typeof t>[1]) => t(locale, key),
    [locale],
  );

  const value = useMemo(
    () => ({ locale, setLocale, tr }),
    [locale, setLocale, tr],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within I18nProvider");
  }
  return context;
}
