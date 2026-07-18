/** Persisted Supabase session + care context for /api/v1. */

const TOKENS_KEY = "sahaay_api_tokens";
const CONTEXT_KEY = "sahaay_api_context";

export interface ApiTokens {
  access_token: string;
  refresh_token: string;
  expires_at?: number;
}

export interface ApiProfile {
  id: string;
  full_name: string;
  email?: string | null;
  account_type?: string;
  preferred_language?: string;
}

export interface ApiCareContext {
  profile: ApiProfile;
  familyId: string;
  elderId: string;
  conversationId: string;
  role: "family_member" | "elder";
}

export function getTokens(): ApiTokens | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(TOKENS_KEY);
    return raw ? (JSON.parse(raw) as ApiTokens) : null;
  } catch {
    return null;
  }
}

export function setTokens(tokens: ApiTokens | null): void {
  if (tokens) {
    localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens));
  } else {
    localStorage.removeItem(TOKENS_KEY);
  }
  window.dispatchEvent(new Event("sahaay-auth"));
}

export function getCareContext(): ApiCareContext | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(CONTEXT_KEY);
    return raw ? (JSON.parse(raw) as ApiCareContext) : null;
  } catch {
    return null;
  }
}

export function setCareContext(ctx: ApiCareContext | null): void {
  if (ctx) {
    localStorage.setItem(CONTEXT_KEY, JSON.stringify(ctx));
  } else {
    localStorage.removeItem(CONTEXT_KEY);
  }
  window.dispatchEvent(new Event("sahaay-store"));
}

export function clearApiSession(): void {
  localStorage.removeItem(TOKENS_KEY);
  localStorage.removeItem(CONTEXT_KEY);
  window.dispatchEvent(new Event("sahaay-auth"));
  window.dispatchEvent(new Event("sahaay-store"));
}
