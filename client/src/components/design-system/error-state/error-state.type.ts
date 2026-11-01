export type DSErrorStateRetryControl =
  | { onRetry: () => void; retryLabel: string; isRetrying?: boolean }
  | { onRetry?: never; retryLabel?: never; isRetrying?: never };
