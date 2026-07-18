import { API_BASE_URL } from "./config";
import {
  clearApiSession,
  getCareContext,
  getTokens,
  setCareContext,
  setTokens,
  type ApiCareContext,
  type ApiProfile,
  type ApiTokens,
} from "./authStorage";
import type { Routine, UiChatMessage } from "./types";

const API_PREFIX = "/api/v1";

export interface AuthSessionResponse {
  access_token: string;
  refresh_token: string;
  expires_in?: number;
  token_type?: string;
  user?: { id: string; email?: string };
}

export interface ApiReminder {
  id: string;
  elder_id: string;
  type: string;
  title: string;
  description?: string | null;
  note?: string | null;
  local_time?: string;
  timezone?: string;
  frequency?: string;
  status?: string;
  next_run_at?: string | null;
}

export interface ApiMessage {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  metadata_json?: { citations?: Array<{ title: string; url: string; snippet?: string }> } | null;
  audio_url?: string | null;
  created_at?: string;
}

function parseErrorDetail(raw: string, status: number, statusText: string): string {
  try {
    const parsed = JSON.parse(raw) as { detail?: unknown };
    if (typeof parsed.detail === "string") return parsed.detail;
    if (Array.isArray(parsed.detail)) {
      return parsed.detail
        .map((item) =>
          typeof item === "object" && item && "msg" in item
            ? String((item as { msg: string }).msg)
            : JSON.stringify(item),
        )
        .join("; ");
    }
  } catch {
    // ignore
  }
  return raw || `Request failed (${status} ${statusText})`;
}

async function rawFetch(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<Response> {
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
  try {
    return await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error(`Cannot reach backend at ${API_BASE_URL}. Is the API running?`);
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const tokens = getTokens();
  if (!tokens?.refresh_token) return null;
  const response = await rawFetch(`${API_PREFIX}/auth/refresh`, {
    method: "POST",
    body: JSON.stringify({ refresh_token: tokens.refresh_token }),
  });
  if (!response.ok) {
    clearApiSession();
    return null;
  }
  const data = (await response.json()) as AuthSessionResponse;
  persistSession(data);
  return data.access_token;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const fullPath =
    path.startsWith("/api/") || path === "/health" || path.startsWith("/static/")
      ? path
      : `${API_PREFIX}${path.startsWith("/") ? path : `/${path}`}`;
  let token = auth ? getTokens()?.access_token : null;

  let response = await rawFetch(fullPath, options, token);
  if (auth && response.status === 401) {
    token = await refreshAccessToken();
    if (!token) {
      throw new Error("Session expired. Please log in again.");
    }
    response = await rawFetch(fullPath, options, token);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(parseErrorDetail(detail, response.status, response.statusText));
  }

  return response.json() as Promise<T>;
}

export function persistSession(data: AuthSessionResponse): ApiTokens {
  const tokens: ApiTokens = {
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    expires_at: data.expires_in
      ? Date.now() + data.expires_in * 1000
      : undefined,
  };
  setTokens(tokens);
  return tokens;
}

export async function signup(email: string, password: string): Promise<AuthSessionResponse | Record<string, unknown>> {
  return apiFetch(`${API_PREFIX}/auth/signup`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  }, false);
}

export async function login(email: string, password: string): Promise<AuthSessionResponse> {
  const data = await apiFetch<AuthSessionResponse>(
    `${API_PREFIX}/auth/login`,
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    },
    false,
  );
  if (!data.access_token) {
    throw new Error("Login did not return an access token. Check Supabase email confirmation settings.");
  }
  persistSession(data);
  return data;
}

export async function logoutApi(): Promise<void> {
  try {
    await apiFetch(`${API_PREFIX}/auth/logout`, { method: "POST" });
  } catch {
    // still clear local session
  }
  clearApiSession();
}

export async function getMe(): Promise<ApiProfile> {
  return apiFetch<ApiProfile>(`${API_PREFIX}/auth/me`);
}

export async function updateProfile(body: {
  full_name?: string;
  account_type?: "family" | "elder" | "both";
  preferred_language?: "en" | "hi" | "gu";
}): Promise<ApiProfile> {
  return apiFetch<ApiProfile>(`${API_PREFIX}/profiles/me`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function createFamily(name: string): Promise<{ id: string; name: string }> {
  return apiFetch(`${API_PREFIX}/families`, {
    method: "POST",
    body: JSON.stringify({ name, timezone: "Asia/Kolkata" }),
  });
}

export async function listFamilies(): Promise<Array<{ id: string; name: string }>> {
  return apiFetch(`${API_PREFIX}/families`);
}

export async function createElder(
  familyId: string,
  body: {
    full_name: string;
    user_id?: string | null;
    preferred_language?: "en" | "hi" | "gu";
  },
): Promise<{ id: string; full_name: string; user_id?: string | null }> {
  return apiFetch(`${API_PREFIX}/families/${familyId}/elders`, {
    method: "POST",
    body: JSON.stringify({
      preferred_language: "en",
      timezone: "Asia/Kolkata",
      consent_to_family_monitoring: true,
      ...body,
    }),
  });
}

export async function listElders(familyId: string): Promise<Array<{ id: string; full_name: string; user_id?: string | null }>> {
  return apiFetch(`${API_PREFIX}/families/${familyId}/elders`);
}

export async function getMyElder(): Promise<{ id: string; full_name: string } | null> {
  try {
    return await apiFetch(`${API_PREFIX}/elders/me`);
  } catch {
    return null;
  }
}

export async function createConversation(elderId: string, title = "Sahaay chat"): Promise<{ id: string }> {
  return apiFetch(`${API_PREFIX}/conversations`, {
    method: "POST",
    body: JSON.stringify({ elder_id: elderId, title }),
  });
}

export async function getConversation(conversationId: string): Promise<{
  id: string;
  messages: ApiMessage[];
}> {
  return apiFetch(`${API_PREFIX}/conversations/${conversationId}`);
}

export async function sendConversationMessage(
  conversationId: string,
  content: string,
  options: { speak?: boolean; use_search?: boolean } = {},
): Promise<ApiMessage> {
  return apiFetch(`${API_PREFIX}/conversations/${conversationId}/messages`, {
    method: "POST",
    body: JSON.stringify({
      content,
      speak: options.speak ?? true,
      use_search: options.use_search ?? true,
    }),
  });
}

export async function listReminders(elderId: string): Promise<ApiReminder[]> {
  return apiFetch(`${API_PREFIX}/elders/${elderId}/reminders`);
}

export async function createReminder(
  elderId: string,
  body: {
    type: "medicine" | "meal" | "sleep" | "appointment" | "exercise" | "hydration" | "other";
    title: string;
    local_time: string; // HH:MM:SS
    frequency?: "once" | "daily" | "weekly" | "monthly" | "custom";
    description?: string;
  },
): Promise<ApiReminder> {
  return apiFetch(`${API_PREFIX}/elders/${elderId}/reminders`, {
    method: "POST",
    body: JSON.stringify({
      frequency: "daily",
      timezone: "Asia/Kolkata",
      ...body,
    }),
  });
}

export async function getHealth(): Promise<{
  status: string;
  database?: string;
  services: Record<string, boolean>;
}> {
  return apiFetch("/health", {}, false);
}

export function resolveAudioUrl(relativePath: string | null | undefined): string | null {
  if (!relativePath) return null;
  if (relativePath.startsWith("http")) return relativePath;
  return `${API_BASE_URL}${relativePath.startsWith("/") ? relativePath : `/${relativePath}`}`;
}

export function reminderToRoutine(reminder: ApiReminder): Routine {
  const time = reminder.local_time
    ? reminder.local_time.slice(0, 5)
    : reminder.next_run_at
      ? new Date(reminder.next_run_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false })
      : null;
  const typeMap: Record<string, string> = {
    medicine: "medication",
    appointment: "appointment",
    meal: "habit",
    sleep: "habit",
    exercise: "habit",
    hydration: "habit",
    other: "habit",
  };
  return {
    id: null,
    name: reminder.title,
    type: typeMap[reminder.type] ?? "habit",
    timing: time,
    frequency: reminder.frequency ?? "daily",
    notes: reminder.description ?? reminder.note ?? null,
    priority: reminder.type === "medicine" ? "critical" : "normal",
  };
}

export function messageToUi(message: ApiMessage): UiChatMessage {
  const citations = message.metadata_json?.citations ?? [];
  return {
    id: message.id,
    role: message.role === "assistant" ? "assistant" : "user",
    content: message.content,
    citations,
    audioUrl: resolveAudioUrl(message.audio_url),
    timestamp: message.created_at ? Date.parse(message.created_at) : Date.now(),
  };
}

/** After login/signup: ensure family, elder, and conversation exist. */
export async function bootstrapCareContext(input: {
  fullName: string;
  role: "family_member" | "elder";
  familyName?: string;
  locale?: "en" | "hi" | "gu";
}): Promise<ApiCareContext> {
  const existing = getCareContext();
  if (existing?.conversationId && existing.elderId) {
    try {
      await getConversation(existing.conversationId);
      return existing;
    } catch {
      // recreate below
    }
  }

  const profile = await updateProfile({
    full_name: input.fullName,
    account_type: input.role === "elder" ? "elder" : "family",
    preferred_language: input.locale ?? "en",
  });

  let families = await listFamilies();
  let familyId = families[0]?.id;
  if (!familyId) {
    const family = await createFamily(
      input.familyName?.trim() || `${input.fullName}'s family`,
    );
    familyId = family.id;
    families = [family];
  }

  let elders = await listElders(familyId);
  let elder = elders.find((e) => e.user_id === profile.id) ?? elders[0];
  if (!elder) {
    elder = await createElder(familyId, {
      full_name: input.fullName,
      user_id: input.role === "elder" ? profile.id : null,
      preferred_language: input.locale ?? "en",
    });
  } else if (input.role === "elder" && !elder.user_id) {
    // already have an elder row; use it
  }

  const conversation = await createConversation(elder.id, "Sahaay companion");

  const ctx: ApiCareContext = {
    profile: {
      id: profile.id,
      full_name: profile.full_name || input.fullName,
      email: profile.email,
      account_type: profile.account_type,
      preferred_language: profile.preferred_language,
    },
    familyId,
    elderId: elder.id,
    conversationId: conversation.id,
    role: input.role,
  };
  setCareContext(ctx);
  return ctx;
}

export function getStoredCareContext(): ApiCareContext | null {
  return getCareContext();
}
