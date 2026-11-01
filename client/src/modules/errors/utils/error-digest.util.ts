export const readErrorDigest = (error: unknown): string | null => {
  if (typeof error !== "object" || error === null || !("digest" in error)) {
    return null;
  }

  return typeof error.digest === "string" ? error.digest : null;
};
