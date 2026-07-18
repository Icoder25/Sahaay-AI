"use client";

import { useEffect, useRef } from "react";
import { ChatMessage } from "@/components/ChatMessage/ChatMessage";
import { useI18n } from "@/contexts/I18nContext";
import type { UiChatMessage } from "@/lib/types";
import styles from "./ChatThread.module.css";

interface ChatThreadProps {
  messages: UiChatMessage[];
  isLoading?: boolean;
  error?: string | null;
}

export function ChatThread({
  messages,
  isLoading = false,
  error = null,
}: ChatThreadProps) {
  const { tr } = useI18n();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, error]);

  return (
    <div className={styles.wrapper} aria-live="polite" aria-busy={isLoading}>
      {messages.length === 0 ? (
        <div className={styles.empty}>
          <p className={styles.emptyTitle}>{tr("chatEmptyTitle")}</p>
          <p className={styles.emptyText}>{tr("chatEmptyText")}</p>
        </div>
      ) : (
        <div className={styles.messages}>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </div>
      )}

      {isLoading ? (
        <div className={styles.loading} role="status">
          <span className={styles.loadingDots} aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          {tr("thinking")}
        </div>
      ) : null}

      {error ? (
        <div className={styles.error} role="alert">
          {error}
        </div>
      ) : null}

      <div ref={bottomRef} />
    </div>
  );
}
