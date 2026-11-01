import { createSuccessResult } from "@/modules/auth/test/utils/api-result.util";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import type { ProfileChanges } from "../../typing/types/profile-changes.type";
import { apiPatch } from "../mocks/api-client.mock";

interface PatchOptions {
  body: ProfileChanges;
}

const AVATAR_URL = "https://storage.example.test/avatar.png";

export const respondToProfilePatch = (currentUser: CurrentUser): void => {
  apiPatch.mockImplementation((path, options) => {
    if (path !== "/api/me") {
      return Promise.reject(new Error(`No mocked response for ${path}`));
    }

    const { body } = options as PatchOptions;
    const avatarFileId =
      body.avatarFileId === undefined ? currentUser.avatarFileId : body.avatarFileId;

    return Promise.resolve(
      createSuccessResult({
        ...currentUser,
        name: body.name ?? currentUser.name,
        language: body.language ?? currentUser.language,
        colorScheme: body.colorScheme ?? currentUser.colorScheme,
        avatarFileId,
        avatarUrl: avatarFileId === null ? null : AVATAR_URL,
      }),
    );
  });
};
