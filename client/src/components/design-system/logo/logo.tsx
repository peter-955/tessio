import { useId, type FC } from "react";
import styles from "./logo.module.scss";

interface Props {
  size?: number;
  hasWordmark?: boolean;
}

export const DSLogo: FC<Props> = ({ size = 28, hasWordmark = false }) => {
  const gradientId = useId();

  return (
    <span className={styles.logo}>
      <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="Tessio">
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#3b82f6" />
            <stop offset="1" stopColor="#1d4ed8" />
          </linearGradient>
        </defs>
        <rect width="64" height="64" rx="16" fill={`url(#${gradientId})`} />
        <circle
          cx="30"
          cy="34"
          r="15"
          fill="none"
          stroke="#ffffff"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray="74 20.25"
        />
        <path
          d="M22 34 L29 41 L50 17"
          fill="none"
          stroke="#ffffff"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {hasWordmark && <span className={styles.wordmark}>Tessio</span>}
    </span>
  );
};
