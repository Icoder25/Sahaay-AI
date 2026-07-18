import { AudioPlayer } from "@/components/AudioPlayer/AudioPlayer";
import { Citations } from "@/components/Citations/Citations";
import type { UiChatMessage } from "@/lib/types";
import styles from "./ChatMessage.module.css";

interface ChatMessageProps {
  message: UiChatMessage;
}

function formatTime(timestamp: number): string {
  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(timestamp));
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const showCitations =
    !isUser &&
    message.intent === "question" &&
    message.citations &&
    message.citations.length > 0;

  return (
    <article
      className={`${styles.message} ${isUser ? styles.user : styles.assistant}`}
      aria-label={isUser ? "Your message" : "Sahaay reply"}
    >
      {!isUser ? (
        <div className={styles.avatar} aria-hidden="true">
          S
        </div>
      ) : null}
      <div className={styles.content}>
        <div className={styles.bubble}>
          <p className={styles.text}>{message.content}</p>
        </div>
        {showCitations ? (
          <Citations citations={message.citations!} />
        ) : null}
        {!isUser && message.audioUrl ? (
          <AudioPlayer src={message.audioUrl} />
        ) : null}
        <time className={styles.time} dateTime={new Date(message.timestamp).toISOString()}>
          {formatTime(message.timestamp)}
        </time>
      </div>
    </article>
  );
}
