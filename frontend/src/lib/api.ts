import { API_BASE_URL } from "./config";
import type {
  ChatRequest,
  ChatResponse,
  HealthResponse,
  ReminderDemoResponse,
  Routine,
} from "./types";

export function resolveAudioUrl(relativePath: string | null): string | null {
  if (!relativePath) {
    return null;
  }
  if (relativePath.startsWith("http")) {
    return relativePath;
  }
  return `${API_BASE_URL}${relativePath}`;
}

async function fetchJson<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(
      detail || `Request failed (${response.status} ${response.statusText})`,
    );
  }

  return response.json() as Promise<T>;
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>("/health");
}

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  return fetchJson<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getRoutines(sessionId: string): Promise<Routine[]> {
  return fetchJson<Routine[]>(`/routines/${sessionId}`);
}

export async function getDemoReminder(
  sessionId: string,
  speak = true,
): Promise<ReminderDemoResponse> {
  const params = new URLSearchParams({
    session_id: sessionId,
    speak: String(speak),
  });
  return fetchJson<ReminderDemoResponse>(`/reminders/demo?${params}`);
}
