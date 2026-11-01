import { afterEach, describe, expect, it, vi } from "vitest";
import { LAST_PROJECT_KEY_STORAGE_KEY } from "../typing/constants/last-project-key.constant";
import {
  readLastProjectKey,
  removeLastProjectKey,
  storeLastProjectKey,
  subscribeToLastProjectKey,
} from "./last-project-key.util";

afterEach(() => {
  window.localStorage.clear();
});

describe("last project key", () => {
  it("stores and reads the key back", () => {
    expect(readLastProjectKey()).toBeNull();

    storeLastProjectKey("SHOP");

    expect(readLastProjectKey()).toBe("SHOP");
    expect(window.localStorage.getItem(LAST_PROJECT_KEY_STORAGE_KEY)).toBe("SHOP");
  });

  it("removes the key only when it is the stored one", () => {
    storeLastProjectKey("SHOP");

    removeLastProjectKey("DOCS");
    expect(readLastProjectKey()).toBe("SHOP");

    removeLastProjectKey("SHOP");
    expect(readLastProjectKey()).toBeNull();
  });

  it("notifies subscribers on writes and on storage events until unsubscribed", () => {
    const listener = vi.fn<() => void>();
    const unsubscribe = subscribeToLastProjectKey(listener);

    storeLastProjectKey("SHOP");
    window.dispatchEvent(new StorageEvent("storage", { key: LAST_PROJECT_KEY_STORAGE_KEY }));
    window.dispatchEvent(new StorageEvent("storage", { key: "another-key" }));

    expect(listener).toHaveBeenCalledTimes(2);

    unsubscribe();
    storeLastProjectKey("DOCS");

    expect(listener).toHaveBeenCalledTimes(2);
  });

  it("fails silently when the storage throws", () => {
    const throwStorageError = (): never => {
      throw new Error("Storage is blocked");
    };
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(throwStorageError);
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(throwStorageError);
    vi.spyOn(Storage.prototype, "removeItem").mockImplementation(throwStorageError);

    expect(readLastProjectKey()).toBeNull();
    expect(() => {
      storeLastProjectKey("SHOP");
    }).not.toThrow();
    expect(() => {
      removeLastProjectKey("SHOP");
    }).not.toThrow();
  });
});
