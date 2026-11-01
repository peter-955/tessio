export interface RevealedSecrets {
  revealedValueById: Record<string, string>;
  reveal: (itemId: string) => Promise<void>;
  hide: (itemId: string) => void;
  isRevealing: (itemId: string) => boolean;
}
