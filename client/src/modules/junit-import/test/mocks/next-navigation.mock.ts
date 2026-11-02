import { vi } from "vitest";

export const routerPush = vi.fn<(href: string) => void>();

const router = { push: routerPush, replace: vi.fn(), back: vi.fn(), refresh: vi.fn() };

export const nextNavigationMock = {
  useRouter: (): typeof router => {
    return router;
  },
  usePathname: (): string => {
    return "/projects/SHOP/runs";
  },
  useSearchParams: (): URLSearchParams => {
    return new URLSearchParams();
  },
};
