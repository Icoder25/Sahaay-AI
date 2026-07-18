"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
} from "react";
import {
  bootstrapCareContext,
  getMe,
  getStoredCareContext,
  login as apiLogin,
  logoutApi,
  signup as apiSignup,
} from "@/lib/api";
import {
  clearApiSession,
  getCareContext,
  getTokens,
  type ApiCareContext,
} from "@/lib/authStorage";
import { DEMO_CREDENTIALS } from "@/lib/demoCredentials";
import type { Locale } from "@/lib/i18n/translations";
import { createCachedSnapshot } from "@/lib/syncSnapshot";

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
  role: "family_member" | "elder";
  locale: Locale;
}

interface RegisterInput {
  email: string;
  password: string;
  fullName: string;
  role: "family_member" | "elder";
  locale: Locale;
  familyName?: string;
  inviteCode?: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  care: ApiCareContext | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (input: RegisterInput) => Promise<AuthUser>;
  logout: () => Promise<void>;
  refreshCare: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function readUser(): AuthUser | null {
  const tokens = getTokens();
  const care = getCareContext();
  if (!tokens?.access_token || !care) return null;
  return {
    id: care.profile.id,
    email: care.profile.email ?? "",
    fullName: care.profile.full_name,
    role: care.role,
    locale: (care.profile.preferred_language as Locale) || "en",
  };
}

const authStore = createCachedSnapshot<AuthUser | null>(
  readUser,
  (onStoreChange) => {
    window.addEventListener("sahaay-auth", onStoreChange);
    window.addEventListener("sahaay-store", onStoreChange);
    return () => {
      window.removeEventListener("sahaay-auth", onStoreChange);
      window.removeEventListener("sahaay-store", onStoreChange);
    };
  },
  () => null,
);

const careStore = createCachedSnapshot<ApiCareContext | null>(
  getStoredCareContext,
  (onStoreChange) => {
    window.addEventListener("sahaay-store", onStoreChange);
    window.addEventListener("sahaay-auth", onStoreChange);
    return () => {
      window.removeEventListener("sahaay-store", onStoreChange);
      window.removeEventListener("sahaay-auth", onStoreChange);
    };
  },
  () => null,
);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const user = useSyncExternalStore(
    authStore.subscribe,
    authStore.getSnapshot,
    authStore.getServerSnapshot,
  );
  const care = useSyncExternalStore(
    careStore.subscribe,
    careStore.getSnapshot,
    careStore.getServerSnapshot,
  );

  const login = useCallback(async (email: string, password: string) => {
    const normalized = email.trim().toLowerCase();
    await apiLogin(normalized, password);
    const profile = await getMe();
    const isDemo = normalized === DEMO_CREDENTIALS.email;
    const role =
      isDemo || profile.account_type === "elder" ? "elder" : "family_member";
    await bootstrapCareContext({
      fullName: isDemo
        ? DEMO_CREDENTIALS.fullName
        : profile.full_name || normalized.split("@")[0],
      role,
      locale: (profile.preferred_language as Locale) || "en",
    });
  }, []);

  const register = useCallback(async (input: RegisterInput) => {
    const email = input.email.trim().toLowerCase();
    await apiSignup(email, input.password);
    await apiLogin(email, input.password);
    await bootstrapCareContext({
      fullName: input.fullName.trim(),
      role: input.role,
      familyName: input.familyName,
      locale: input.locale,
    });
    const ctx = getCareContext();
    if (!ctx) {
      throw new Error("Could not create care profile after signup.");
    }
    return {
      id: ctx.profile.id,
      email,
      fullName: ctx.profile.full_name,
      role: input.role,
      locale: input.locale,
    } satisfies AuthUser;
  }, []);

  const logout = useCallback(async () => {
    await logoutApi();
    clearApiSession();
  }, []);

  const refreshCare = useCallback(() => {
    window.dispatchEvent(new Event("sahaay-store"));
  }, []);

  const value = useMemo(
    () => ({
      user,
      care,
      isAuthenticated: Boolean(getTokens()?.access_token && care),
      login,
      register,
      logout,
      refreshCare,
    }),
    [user, care, login, register, logout, refreshCare],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
