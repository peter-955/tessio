import {
  LAST_PROJECT_KEY_CHANGE_EVENT,
  LAST_PROJECT_KEY_STORAGE_KEY,
} from "../typing/constants/last-project-key.constant";

const notifyLastProjectKeyChange = (): void => {
  window.dispatchEvent(new Event(LAST_PROJECT_KEY_CHANGE_EVENT));
};

export const readLastProjectKey = (): string | null => {
  try {
    return window.localStorage.getItem(LAST_PROJECT_KEY_STORAGE_KEY);
  } catch {
    return null;
  }
};

export const storeLastProjectKey = (projectKey: string): void => {
  try {
    window.localStorage.setItem(LAST_PROJECT_KEY_STORAGE_KEY, projectKey);
  } catch {
    return;
  }

  notifyLastProjectKeyChange();
};

export const removeLastProjectKey = (projectKey: string): void => {
  if (readLastProjectKey() !== projectKey) {
    return;
  }

  try {
    window.localStorage.removeItem(LAST_PROJECT_KEY_STORAGE_KEY);
  } catch {
    return;
  }

  notifyLastProjectKeyChange();
};

export const subscribeToLastProjectKey = (listener: () => void): (() => void) => {
  const handleStorage = (event: StorageEvent): void => {
    if (event.key === null || event.key === LAST_PROJECT_KEY_STORAGE_KEY) {
      listener();
    }
  };

  window.addEventListener("storage", handleStorage);
  window.addEventListener(LAST_PROJECT_KEY_CHANGE_EVENT, listener);

  return () => {
    window.removeEventListener("storage", handleStorage);
    window.removeEventListener(LAST_PROJECT_KEY_CHANGE_EVENT, listener);
  };
};
