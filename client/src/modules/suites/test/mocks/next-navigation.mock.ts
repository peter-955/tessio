import { vi } from "vitest";

export const routerPush = vi.fn<(href: string) => void>();

export const routerReplace = vi.fn<(href: string) => void>();

const router = { push: routerPush, replace: routerReplace, back: vi.fn(), refresh: vi.fn() };

export const nextNavigationMock = {
  useRouter: (): typeof router => {
    return router;
  },
  usePathname: (): string => {
    return "/projects/SHOP/suites";
  },
  useSearchParams: (): URLSearchParams => {
    return new URLSearchParams();
  },
};
