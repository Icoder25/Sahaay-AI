"use client";

import { useEffect, useRef } from "react";
import { ChatMessage } from "@/components/ChatMessage/ChatMessage";
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
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, error]);

  return (
    <div className={styles.wrapper} aria-live="polite" aria-busy={isLoading}>
      {messages.length === 0 ? (
        <div className={styles.empty}>
          <p className={styles.emptyTitle}>Namaste — welcome to Sahaay</p>
          <p className={styles.emptyText}>
            Share your daily routines or ask a health question. Sahaay listens
            gently and remembers what matters to you.
          </p>
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
          Sahaay is thinking…
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
