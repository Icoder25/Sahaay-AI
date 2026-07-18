export type ChatIntent = "routine_update" | "question" | "chat";

export interface Citation {
  title: string;
  url: string;
  snippet?: string | null;
}

export interface Routine {
  id?: number | null;
  name: string;
  type: string;
  timing?: string | null;
  frequency: string;
  notes?: string | null;
  priority: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  speak?: boolean;
}

export interface ChatResponse {
  reply: string;
  session_id: string;
  routines_updated: Routine[];
  citations: Citation[];
  audio_url: string | null;
  intent: ChatIntent;
}

export interface HealthResponse {
  status: string;
  services: Record<string, boolean>;
}

export interface ReminderDemoResponse {
  message: string;
  routine: Routine | null;
  audio_url: string | null;
  reminder: {
    id: number;
    session_id: string;
    routine_id: number | null;
    message: string;
    scheduled_time: string | null;
    is_demo: boolean;
  } | null;
}

export interface UiChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: ChatIntent;
  citations?: Citation[];
  audioUrl?: string | null;
  timestamp: number;
}
