import { vi } from "vitest";

interface NavigationState {
  pathname: string;
  searchParams: URLSearchParams;
}

export const routerReplace = vi.fn<(href: string) => void>();

const router = { replace: routerReplace, push: vi.fn(), back: vi.fn(), refresh: vi.fn() };

export const navigationState: NavigationState = {
  pathname: "/",
  searchParams: new URLSearchParams(),
};

export const setNavigation = (pathname: string, query = ""): void => {
  navigationState.pathname = pathname;
  navigationState.searchParams = new URLSearchParams(query);
};

export const nextNavigationMock = {
  useRouter: (): typeof router => {
    return router;
  },
  usePathname: (): string => {
    return navigationState.pathname;
  },
  useSearchParams: (): URLSearchParams => {
    return navigationState.searchParams;
  },
};
