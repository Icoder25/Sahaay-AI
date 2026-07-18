"use client";

import { useEffect, useRef } from "react";
import styles from "./AudioPlayer.module.css";

interface AudioPlayerProps {
  src: string;
  autoPlay?: boolean;
  label?: string;
}

export function AudioPlayer({
  src,
  autoPlay = true,
  label = "Play voice reply",
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (autoPlay && audioRef.current) {
      audioRef.current.play().catch(() => {
        // Autoplay may be blocked until user interaction.
      });
    }
  }, [src, autoPlay]);

  return (
    <div className={styles.wrapper}>
      <span className={styles.icon} aria-hidden="true">
        🔊
      </span>
      <audio ref={audioRef} controls src={src} className={styles.audio}>
        {label}
      </audio>
    </div>
  );
}
