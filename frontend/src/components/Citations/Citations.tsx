import styles from "./Citations.module.css";
import type { Citation } from "@/lib/types";

interface CitationsProps {
  citations: Citation[];
}

export function Citations({ citations }: CitationsProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className={styles.wrapper}>
      <p className={styles.heading}>Sources</p>
      <ul className={styles.list}>
        {citations.map((citation) => (
          <li key={citation.url} className={styles.item}>
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.link}
            >
              {citation.title}
            </a>
            {citation.snippet ? (
              <p className={styles.snippet}>{citation.snippet}</p>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
