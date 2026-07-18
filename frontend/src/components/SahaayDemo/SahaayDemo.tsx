"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChatInput } from "@/components/ChatInput/ChatInput";
import { ChatThread } from "@/components/ChatThread/ChatThread";
import { ElderSidebar } from "@/components/ElderSidebar/ElderSidebar";
import { HealthIndicator } from "@/components/HealthIndicator/HealthIndicator";
import { RoutinesPanel } from "@/components/RoutinesPanel/RoutinesPanel";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import {
  getConversation,
  listReminders,
  messageToUi,
  reminderToRoutine,
  sendConversationMessage,
} from "@/lib/api";
import type { Routine, UiChatMessage } from "@/lib/types";
import styles from "./SahaayDemo.module.css";

function createMessageId(): string {
  return crypto.randomUUID();
}

export function SahaayDemo() {
  const router = useRouter();
  const { tr } = useI18n();
  const { care, isAuthenticated, user } = useAuth();
  const [messages, setMessages] = useState<UiChatMessage[]>([]);
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [routinesLoading, setRoutinesLoading] = useState(false);
  const [reminderLoading, setReminderLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [speakEnabled, setSpeakEnabled] = useState(true);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || !care) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [isAuthenticated, care, router]);

  const refreshReminders = useCallback(async () => {
    if (!care?.elderId) return;
    setRoutinesLoading(true);
    try {
      const reminders = await listReminders(care.elderId);
      setRoutines(reminders.map(reminderToRoutine));
    } catch {
      // keep last known
    } finally {
      setRoutinesLoading(false);
    }
  }, [care?.elderId]);

  useEffect(() => {
    if (!care?.conversationId) return;
    let cancelled = false;

    (async () => {
      try {
        const conversation = await getConversation(care.conversationId);
        if (cancelled) return;
        setMessages(conversation.messages.map(messageToUi));
      } catch {
        // empty thread until first message
      }
      await refreshReminders();
    })();

    return () => {
      cancelled = true;
    };
  }, [care?.conversationId, refreshReminders]);

  const handleSend = useCallback(
    async (text: string) => {
      if (!care?.conversationId) return;

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
        const response = await sendConversationMessage(
          care.conversationId,
          text,
          { speak: speakEnabled, use_search: true },
        );

        const assistantMessage = messageToUi(response);
        setMessages((current) => [...current, assistantMessage]);
        await refreshReminders();
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "Something went wrong talking to Sahaay.";
        setError(message);
      } finally {
        setChatLoading(false);
      }
    },
    [care?.conversationId, speakEnabled, refreshReminders],
  );

  const handleNextReminder = useCallback(async () => {
    if (!care?.conversationId || !care.elderId) return;

    setError(null);
    setReminderLoading(true);
    try {
      const reminders = await listReminders(care.elderId);
      const active = reminders.find((r) => r.status === "active") ?? reminders[0];
      if (!active) {
        setError("No reminders yet. Ask Sahaay to help set one up in chat.");
        return;
      }

      const timeBit = active.local_time
        ? ` at ${active.local_time.slice(0, 5)}`
        : "";
      const prompt = `Please give me a warm spoken reminder now for: ${active.title}${timeBit}.`;
      const response = await sendConversationMessage(
        care.conversationId,
        prompt,
        { speak: speakEnabled, use_search: false },
      );

      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "user",
          content: `Remind me: ${active.title}`,
          timestamp: Date.now(),
        },
        messageToUi(response),
      ]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not trigger reminder.",
      );
    } finally {
      setReminderLoading(false);
    }
  }, [care?.conversationId, care?.elderId, speakEnabled]);

  if (!ready || !care) {
    return (
      <div className={styles.page}>
        <p className={styles.tagline}>Connecting to Sahaay…</p>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <div className={styles.logo} aria-hidden="true">
            🙏
          </div>
          <div>
            <h1 className={styles.title}>{tr("appName")}</h1>
            <p className={styles.tagline}>
              {user?.fullName
                ? `Namaste, ${user.fullName}`
                : tr("elderWelcome")}
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
          onDemoReminder={handleNextReminder}
          reminderLoading={reminderLoading}
        />

        <ElderSidebar sessionId={care.elderId} />
      </div>
    </div>
  );
}
