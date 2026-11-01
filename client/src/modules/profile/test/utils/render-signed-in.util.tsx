import { GET_CURRENT_USER_KEY } from "@/modules/auth/hooks/queries/use-get-current-user";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import type { QueryClient } from "@tanstack/react-query";
import type { RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";
import { CachedSessionProvider } from "./cached-session-provider";
import { createSignedInUser } from "./current-user.fixture";

interface Result extends RenderResult {
  queryClient: QueryClient;
}

export const renderSignedIn = (
  element: ReactElement,
  currentUser: CurrentUser = createSignedInUser(),
): Result => {
  const queryClient = createTestQueryClient();
  queryClient.setQueryData([GET_CURRENT_USER_KEY], currentUser);

  return renderWithProviders(<CachedSessionProvider>{element}</CachedSessionProvider>, {
    queryClient,
  });
};
