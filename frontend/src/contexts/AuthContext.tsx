"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
} from "react";
import type { StoredUser } from "@/lib/store";
import {
  createFamily,
  findUser,
  getCurrentUser,
  joinFamily,
  saveUser,
  setCurrentUser,
} from "@/lib/store";
import type { Locale } from "@/lib/i18n/translations";
import { getOrCreateSessionId } from "@/lib/session";
import { addElderProfile } from "@/lib/store";
import { createCachedSnapshot } from "@/lib/syncSnapshot";

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
  user: StoredUser | null;
  login: (email: string, password: string) => boolean;
  register: (input: RegisterInput) => StoredUser;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const authStore = createCachedSnapshot<StoredUser | null>(
  getCurrentUser,
  (onStoreChange) => {
    window.addEventListener("sahaay-auth", onStoreChange);
    return () => window.removeEventListener("sahaay-auth", onStoreChange);
  },
  () => null,
);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const user = useSyncExternalStore(
    authStore.subscribe,
    authStore.getSnapshot,
    authStore.getServerSnapshot,
  );

  const login = useCallback((email: string, password: string) => {
    const found = findUser(email, password);
    if (!found) {
      return false;
    }
    setCurrentUser(found);
    window.dispatchEvent(new Event("sahaay-auth"));
    return true;
  }, []);

  const register = useCallback((input: RegisterInput) => {
    const newUser: StoredUser = {
      id: crypto.randomUUID(),
      email: input.email.trim().toLowerCase(),
      password: input.password,
      fullName: input.fullName.trim(),
      role: input.role,
      locale: input.locale,
    };
    saveUser(newUser);
    setCurrentUser(newUser);

    if (input.inviteCode) {
      joinFamily(input.inviteCode);
    } else if (input.role === "family_member") {
      createFamily(input.familyName?.trim() || `${newUser.fullName}'s family`);
    } else {
      createFamily(`${newUser.fullName}'s family`);
      addElderProfile(newUser.fullName, getOrCreateSessionId(), input.locale);
    }

    window.dispatchEvent(new Event("sahaay-auth"));
    window.dispatchEvent(new Event("sahaay-store"));
    return newUser;
  }, []);

  const logout = useCallback(() => {
    setCurrentUser(null);
    window.dispatchEvent(new Event("sahaay-auth"));
  }, []);

  const value = useMemo(
    () => ({ user, login, register, logout }),
    [user, login, register, logout],
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
