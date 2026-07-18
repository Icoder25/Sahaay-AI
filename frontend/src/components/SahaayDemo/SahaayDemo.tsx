"use client";

import { useCallback, useEffect, useState } from "react";
import { ChatInput } from "@/components/ChatInput/ChatInput";
import { ChatThread } from "@/components/ChatThread/ChatThread";
import { HealthIndicator } from "@/components/HealthIndicator/HealthIndicator";
import { RoutinesPanel } from "@/components/RoutinesPanel/RoutinesPanel";
import {
  getDemoReminder,
  getRoutines,
  resolveAudioUrl,
  sendChat,
} from "@/lib/api";
import type { Routine, UiChatMessage } from "@/lib/types";
import { useSession } from "@/hooks/useSession";
import styles from "./SahaayDemo.module.css";

function createMessageId(): string {
  return crypto.randomUUID();
}

function mergeRoutines(existing: Routine[], updated: Routine[]): Routine[] {
  const byKey = new Map<string, Routine>();

  for (const routine of existing) {
    const key = routine.id != null ? String(routine.id) : routine.name;
    byKey.set(key, routine);
  }

  for (const routine of updated) {
    const key = routine.id != null ? String(routine.id) : routine.name;
    byKey.set(key, routine);
  }

  return Array.from(byKey.values()).sort((a, b) => {
    const timeA = a.timing ?? "99:99";
    const timeB = b.timing ?? "99:99";
    return timeA.localeCompare(timeB);
  });
}

export function SahaayDemo() {
  const sessionId = useSession();
  const [messages, setMessages] = useState<UiChatMessage[]>([]);
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [routinesLoading, setRoutinesLoading] = useState(false);
  const [reminderLoading, setReminderLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [speakEnabled, setSpeakEnabled] = useState(true);

  const refreshRoutines = useCallback(async (id: string, showLoading = false) => {
    if (showLoading) {
      setRoutinesLoading(true);
    }
    try {
      const result = await getRoutines(id);
      setRoutines(result);
    } catch {
      // Routines panel can stay on last known data if refresh fails.
    } finally {
      if (showLoading) {
        setRoutinesLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    let cancelled = false;

    getRoutines(sessionId)
      .then((result) => {
        if (!cancelled) {
          setRoutines(result);
        }
      })
      .catch(() => {
        // Keep empty state when the backend is unavailable on first load.
      });

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleSend = useCallback(
    async (text: string) => {
      if (!sessionId) {
        return;
      }

      setError(null);
      setChatLoading(true);

      const userMessage: UiChatMessage = {
        id: createMessageId(),
        role: "user",
        content: text,
        timestamp: Date.now(),
      };
      setMessages((current) => [...current, userMessage]);

      try {
        const response = await sendChat({
          session_id: sessionId,
          message: text,
          speak: speakEnabled,
        });

        const assistantMessage: UiChatMessage = {
          id: createMessageId(),
          role: "assistant",
          content: response.reply,
          intent: response.intent,
          citations: response.citations,
          audioUrl: resolveAudioUrl(response.audio_url),
          timestamp: Date.now(),
        };

        setMessages((current) => [...current, assistantMessage]);

        if (response.routines_updated.length > 0) {
          setRoutines((current) =>
            mergeRoutines(current, response.routines_updated),
          );
        } else {
          await refreshRoutines(sessionId);
        }
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "Something went wrong. Is the backend running on port 8000?";
        setError(message);
      } finally {
        setChatLoading(false);
      }
    },
    [sessionId, speakEnabled, refreshRoutines],
  );

  const handleDemoReminder = useCallback(async () => {
    if (!sessionId) {
      return;
    }

    setError(null);
    setReminderLoading(true);

    try {
      const response = await getDemoReminder(sessionId, speakEnabled);
      const assistantMessage: UiChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: response.message,
        intent: "chat",
        audioUrl: resolveAudioUrl(response.audio_url),
        timestamp: Date.now(),
      };
      setMessages((current) => [...current, assistantMessage]);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Could not trigger demo reminder.";
      setError(message);
    } finally {
      setReminderLoading(false);
    }
  }, [sessionId, speakEnabled]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <div className={styles.logo} aria-hidden="true">
            🙏
          </div>
          <div>
            <h1 className={styles.title}>Sahaay</h1>
            <p className={styles.tagline}>
              Your gentle care companion — routines, answers, and reminders.
            </p>
          </div>
        </div>
        <HealthIndicator />
      </header>

      <div className={styles.layout}>
        <section className={styles.chatSection} aria-label="Chat with Sahaay">
          <ChatThread
            messages={messages}
            isLoading={chatLoading}
            error={error}
          />
          <ChatInput
            onSend={handleSend}
            disabled={chatLoading || reminderLoading}
            speakEnabled={speakEnabled}
            onSpeakToggle={setSpeakEnabled}
          />
        </section>

        <RoutinesPanel
          routines={routines}
          isLoading={routinesLoading}
          onDemoReminder={handleDemoReminder}
          reminderLoading={reminderLoading}
        />
      </div>
    </div>
  );
}
