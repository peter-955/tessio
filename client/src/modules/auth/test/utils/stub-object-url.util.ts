import { vi, type Mock } from "vitest";

interface ObjectUrlStubs {
  createObjectURL: Mock<(object: Blob | MediaSource) => string>;
  revokeObjectURL: Mock<(url: string) => void>;
}

export const OBJECT_URL = "blob:tessio-recovery-codes";

export const stubObjectUrl = (): ObjectUrlStubs => {
  const createObjectURL = vi.fn<(object: Blob | MediaSource) => string>(() => {
    return OBJECT_URL;
  });
  const revokeObjectURL = vi.fn<(url: string) => void>();

  URL.createObjectURL = createObjectURL;
  URL.revokeObjectURL = revokeObjectURL;

  return { createObjectURL, revokeObjectURL };
};
