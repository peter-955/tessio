import { ApiError } from "@/lib/api/api-error";
import englishAuth from "@/lib/i18n/locales/en/auth.json";
import { apiGet } from "@/modules/auth/test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "@/modules/auth/test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { createCurrentUser } from "@/modules/auth/test/utils/current-user.fixture";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { act, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { FC } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useCurrentUser } from "./hooks/use-current-user";
import { SessionGuard } from "./session-guard";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("@/modules/auth/test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

const { useLiveEvents } = vi.hoisted(() => {
  return {
    useLiveEvents: vi.fn<(options: { isEnabled: boolean; onStreamClosed: () => void }) => void>(),
  };
});

vi.mock("@/shared/hooks/use-live-events", () => {
  return { useLiveEvents };
});

const CurrentUserName: FC = () => {
  const currentUser = useCurrentUser();

  return <p>{currentUser.name}</p>;
};

const countCurrentUserCalls = (): number => {
  return apiGet.mock.calls.filter(([path]) => {
    return path === "/api/auth/me";
  }).length;
};

describe("SessionGuard", () => {
  beforeEach(() => {
    apiGet.mockReset();
    setNavigation("/projects/SHOP/runs", "status=failed");
  });

  it("shows a loader while the session loads", () => {
    apiGet.mockReturnValue(new Promise(() => {}));
    renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );

    expect(document.querySelector(".mantine-Loader-root")).toBeInTheDocument();
    expect(screen.queryByText("Ada Lovelace")).not.toBeInTheDocument();
  });

  it("renders children with the current user once signed in and enables live events", async () => {
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("signed_in")),
    });
    renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );

    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
    expect(routerReplace).not.toHaveBeenCalled();
    expect(useLiveEvents).toHaveBeenLastCalledWith(expect.objectContaining({ isEnabled: true }));
  });

  it.each([
    ["two_factor_required", "/two-factor?next=%2Fprojects%2FSHOP%2Fruns%3Fstatus%3Dfailed"],
    [
      "two_factor_setup_required",
      "/two-factor/setup?next=%2Fprojects%2FSHOP%2Fruns%3Fstatus%3Dfailed",
    ],
  ] as const)("redirects a %s half session with next", async (nextStep, expectedPath) => {
    respondWithRoutes(apiGet, { "/api/auth/me": createSuccessResult(createCurrentUser(nextStep)) });
    renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(expectedPath);
    });
    expect(screen.queryByText("Ada Lovelace")).not.toBeInTheDocument();
    expect(useLiveEvents).toHaveBeenLastCalledWith(expect.objectContaining({ isEnabled: false }));
  });

  it("redirects a 401 to sign in as expired", async () => {
    respondWithRoutes(apiGet, { "/api/auth/me": createErrorResult(401, "NOT_SIGNED_IN") });
    renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(
        "/sign-in?next=%2Fprojects%2FSHOP%2Fruns%3Fstatus%3Dfailed&reason=expired",
      );
    });
    expect(screen.queryByText("Ada Lovelace")).not.toBeInTheDocument();
  });

  it("shows an error state for a 500 and retries", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/auth/me": createErrorResult(500, "CONFLICT") });
    renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );

    expect(await screen.findByText(englishAuth.session.loadFailed)).toBeInTheDocument();
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("signed_in")),
    });
    await user.click(screen.getByRole("button", { name: englishAuth.session.retry }));

    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
    expect(countCurrentUserCalls()).toBe(2);
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("refetches the session when another query fails with 401 and then redirects", async () => {
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("signed_in")),
    });
    const { queryClient } = renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );
    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
    respondWithRoutes(apiGet, { "/api/auth/me": createErrorResult(401, "NOT_SIGNED_IN") });

    await act(async () => {
      await queryClient
        .fetchQuery({
          queryKey: ["GET_PROJECTS_KEY"],
          queryFn: () => {
            return Promise.reject(
              new ApiError({ status: 401, code: "NOT_SIGNED_IN", message: "Not signed in." }),
            );
          },
        })
        .catch(() => {
          return null;
        });
    });

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(
        "/sign-in?next=%2Fprojects%2FSHOP%2Fruns%3Fstatus%3Dfailed&reason=expired",
      );
    });
    expect(countCurrentUserCalls()).toBe(2);
  });

  it("refetches the session when a mutation fails with 401", async () => {
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("signed_in")),
    });
    const { queryClient } = renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );
    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();

    await act(async () => {
      await queryClient
        .getMutationCache()
        .build(queryClient, {
          mutationFn: () => {
            return Promise.reject(
              new ApiError({ status: 401, code: "NOT_SIGNED_IN", message: "Not signed in." }),
            );
          },
        })
        .execute(undefined)
        .catch(() => {
          return null;
        });
    });

    await waitFor(() => {
      expect(countCurrentUserCalls()).toBe(2);
    });
  });

  it("invalidates the session when the live events stream closes", async () => {
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("signed_in")),
    });
    renderWithProviders(
      <SessionGuard>
        <CurrentUserName />
      </SessionGuard>,
    );
    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();

    act(() => {
      useLiveEvents.mock.lastCall?.[0].onStreamClosed();
    });

    await waitFor(() => {
      expect(countCurrentUserCalls()).toBe(2);
    });
  });

  it("throws when useCurrentUser is used outside the guard", () => {
    vi.spyOn(console, "error").mockImplementation(() => {
      return;
    });

    expect(() => {
      return renderWithProviders(<CurrentUserName />);
    }).toThrow("useCurrentUser must be used inside SessionGuard.");
  });
});
