import { vi } from "vitest";

const router = { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn(), back: vi.fn() };

export const nextNavigationMock = {
  useRouter: (): typeof router => {
    return router;
  },
  usePathname: (): string => {
    return "/users";
  },
  useSearchParams: (): URLSearchParams => {
    return new URLSearchParams();
  },
};
