import { vi } from "vitest";

export const routerReplace = vi.fn<(href: string) => void>();

export const routerPush = vi.fn<(href: string) => void>();

const router = { replace: routerReplace, push: routerPush, back: vi.fn(), refresh: vi.fn() };

export const nextNavigationMock = {
  useRouter: (): typeof router => {
    return router;
  },
  usePathname: (): string => {
    return "/";
  },
  useSearchParams: (): URLSearchParams => {
    return new URLSearchParams();
  },
};
