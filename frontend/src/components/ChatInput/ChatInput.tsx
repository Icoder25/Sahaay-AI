"use client";

import { FormEvent, useState } from "react";
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSend: (message: string) => Promise<void> | void;
  disabled?: boolean;
  speakEnabled: boolean;
  onSpeakToggle: (enabled: boolean) => void;
}

const SUGGESTIONS = [
  "Hi, I'm Rajesh. I take BP medicine at 8 AM every day.",
  "What should diabetics eat for breakfast?",
  "I also need to pay my electricity bill on the 5th of every month.",
];

export function ChatInput({
  onSend,
  disabled = false,
  speakEnabled,
  onSpeakToggle,
}: ChatInputProps) {
  const [value, setValue] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) {
      return;
    }
    setValue("");
    await onSend(trimmed);
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.suggestions}>
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            className={styles.suggestion}
            disabled={disabled}
            onClick={() => onSend(suggestion)}
          >
            {suggestion}
          </button>
        ))}
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        <label htmlFor="chat-input" className={styles.srOnly}>
          Message Sahaay
        </label>
        <textarea
          id="chat-input"
          className={styles.input}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Type a message…"
          rows={2}
          disabled={disabled}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
        />
        <div className={styles.actions}>
          <label className={styles.speakToggle}>
            <input
              type="checkbox"
              checked={speakEnabled}
              onChange={(event) => onSpeakToggle(event.target.checked)}
              disabled={disabled}
            />
            Voice replies
          </label>
          <button
            type="submit"
            className={styles.sendButton}
            disabled={disabled || !value.trim()}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
