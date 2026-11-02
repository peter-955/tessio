import englishAuth from "@/lib/i18n/locales/en/auth.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import englishNotificationPreferences from "@/lib/i18n/locales/en/notificationPreferences.json";
import englishProfile from "@/lib/i18n/locales/en/profile.json";
import type { UseSignedUploadResult } from "@/lib/uploads/hooks/use-signed-upload";
import { UploadPhase } from "@/lib/uploads/typing/enums/upload-phase.enum";
import type { UploadedFile } from "@/lib/uploads/typing/types/uploaded-file.type";
import { GET_CURRENT_USER_KEY } from "@/modules/auth/hooks/queries/use-get-current-user";
import { routerReplace } from "@/modules/auth/test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createNoContentResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { stubObjectUrl } from "@/modules/auth/test/utils/stub-object-url.util";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { buildDefaultNotificationPreferences } from "@/modules/notification-preferences/test/utils/notification-preference-fixture.util";
import type { QueryClient } from "@tanstack/react-query";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ProfilePage } from "./profile";
import { apiGet, apiPatch, apiPost, apiPut } from "./test/mocks/api-client.mock";
import { createSignedInUser } from "./test/utils/current-user.fixture";
import { respondToProfilePatch } from "./test/utils/profile-patch.util";
import { renderSignedIn } from "./test/utils/render-signed-in.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

const { cropImageToSquare, uploadAvatar } = vi.hoisted(() => {
  return {
    cropImageToSquare: vi.fn<(file: File) => Promise<File>>(),
    uploadAvatar: vi.fn<(file: File) => Promise<UploadedFile>>(),
  };
});

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

vi.mock("./utils/crop-image-to-square.util", () => {
  return { cropImageToSquare };
});

vi.mock("@/lib/uploads/hooks/use-avatar-upload", () => {
  return {
    useAvatarUpload: (): UseSignedUploadResult => {
      return {
        upload: uploadAvatar,
        cancel: vi.fn<() => void>(),
        reset: vi.fn<() => void>(),
        phase: UploadPhase.IDLE,
        progress: null,
        uploadedFile: undefined,
        error: null,
        isUploading: false,
        rules: { maxSizeInBytes: 2097152, acceptedTypes: ["image/png"] },
      };
    },
  };
});

const NEW_PASSWORD = "a brand new long password";
const RECOVERY_CODES = Array.from({ length: 10 }, (_value, index) => {
  return `code${index}-abcde`;
});
const UPLOADED_AVATAR: UploadedFile = {
  id: "5e1b7c55-2f0a-4d7c-8c1d-3b9a6f2e4d10",
  kind: "avatar",
  fileName: "photo.png",
  contentType: "image/png",
  size: 1024,
  status: "uploaded",
  createdAt: "2026-11-01T10:00:00Z",
};

const readCachedUser = (queryClient: QueryClient): CurrentUser | undefined => {
  return queryClient.getQueryData<CurrentUser>([GET_CURRENT_USER_KEY]);
};

const fillPasswordForm = async (currentPassword: string): Promise<void> => {
  const user = userEvent.setup();
  await user.type(
    screen.getByLabelText(new RegExp(`^${englishProfile.password.current}`)),
    currentPassword,
  );
  await user.type(
    screen.getByLabelText(new RegExp(`^${englishProfile.password.new}`)),
    NEW_PASSWORD,
  );
  await user.type(
    screen.getByLabelText(new RegExp(`^${englishProfile.password.confirm}`)),
    NEW_PASSWORD,
  );
  await user.click(screen.getByRole("button", { name: englishProfile.password.submit }));
};

const confirmWithPassword = async (actionLabel: string): Promise<HTMLElement> => {
  const user = userEvent.setup();
  await user.click(screen.getByRole("button", { name: actionLabel }));
  const dialog = await screen.findByRole("dialog", { name: actionLabel });
  await user.type(
    within(dialog).getByLabelText(new RegExp(`^${englishProfile.twoFactor.passwordLabel}`)),
    "my current password",
  );
  await user.click(within(dialog).getByRole("button", { name: englishProfile.twoFactor.confirm }));

  return dialog;
};

describe("ProfilePage", () => {
  beforeEach(() => {
    apiPatch.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
    cropImageToSquare.mockReset();
    uploadAvatar.mockReset();
    window.localStorage.clear();
    stubScrollIntoView();
    respondToProfilePatch(createSignedInUser());
    respondWithRoutes(apiGet, {
      "/api/me/notification-preferences": createSuccessResult(
        buildDefaultNotificationPreferences(),
      ),
    });
  });

  it("renders every section without axe violations", async () => {
    const { container } = renderSignedIn(<ProfilePage />);

    expect(screen.getByRole("heading", { name: englishProfile.title })).toBeInTheDocument();
    expect(screen.getByText("ada@example.test")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: englishProfile.sessions.title }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: englishNotificationPreferences.card.title }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("table", { name: englishNotificationPreferences.card.tableLabel }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: englishProfile.avatar.remove }),
    ).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("saves the name and updates the cached user", async () => {
    const user = userEvent.setup();
    const { queryClient } = renderSignedIn(<ProfilePage />);
    const saveButton = screen.getByRole("button", { name: englishProfile.details.save });
    expect(saveButton).toBeDisabled();

    const nameInput = screen.getByRole("textbox", { name: englishProfile.details.name });
    await user.clear(nameInput);
    await user.type(nameInput, "  Ada King ");
    await user.click(saveButton);

    expect(apiPatch).toHaveBeenCalledWith("/api/me", { body: { name: "Ada King" } });
    expect(await screen.findByText(englishProfile.details.saved)).toBeInTheDocument();
    expect(readCachedUser(queryClient)?.name).toBe("Ada King");
    expect(nameInput).toHaveValue("Ada King");
    expect(saveButton).toBeDisabled();
  });

  it("does not save an empty name", async () => {
    const user = userEvent.setup();
    renderSignedIn(<ProfilePage />);

    await user.clear(screen.getByRole("textbox", { name: englishProfile.details.name }));
    await user.click(screen.getByRole("button", { name: englishProfile.details.save }));

    expect(await screen.findByText(englishProfile.details.nameRequired)).toBeInTheDocument();
    expect(apiPatch).not.toHaveBeenCalled();
  });

  it("crops, uploads and saves a new photo", async () => {
    const user = userEvent.setup();
    const { createObjectURL } = stubObjectUrl();
    const sourceFile = new File(["source"], "photo.png", { type: "image/png" });
    const croppedFile = new File(["cropped"], "photo.png", { type: "image/png" });
    cropImageToSquare.mockResolvedValue(croppedFile);
    uploadAvatar.mockResolvedValue(UPLOADED_AVATAR);
    const { queryClient } = renderSignedIn(<ProfilePage />);

    await user.click(screen.getByRole("button", { name: englishProfile.avatar.change }));
    const dialog = await screen.findByRole("dialog", { name: englishProfile.avatar.dialogTitle });
    const saveButton = within(dialog).getByRole("button", { name: englishProfile.avatar.save });
    expect(saveButton).toBeDisabled();
    const fileInput = dialog.querySelector<HTMLInputElement>('input[type="file"]');
    if (fileInput === null) {
      throw new Error("The dropzone has no file input.");
    }
    await user.upload(fileInput, sourceFile);

    await waitFor(() => {
      expect(saveButton).toBeEnabled();
    });
    expect(cropImageToSquare).toHaveBeenCalledWith(sourceFile);
    expect(createObjectURL).toHaveBeenCalledWith(croppedFile);
    expect(await axe(dialog)).toHaveNoViolations();

    await user.click(saveButton);

    expect(uploadAvatar).toHaveBeenCalledWith(croppedFile);
    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith("/api/me", {
        body: { avatarFileId: UPLOADED_AVATAR.id },
      });
    });
    expect(await screen.findByText(englishProfile.avatar.saved)).toBeInTheDocument();
    expect(readCachedUser(queryClient)?.avatarFileId).toBe(UPLOADED_AVATAR.id);
    expect(
      await screen.findByRole("button", { name: englishProfile.avatar.remove }),
    ).toBeInTheDocument();
  });

  it("shows an inline error when the image cannot be cropped", async () => {
    const user = userEvent.setup();
    stubObjectUrl();
    cropImageToSquare.mockRejectedValue(new Error("unreadable"));
    renderSignedIn(<ProfilePage />);

    await user.click(screen.getByRole("button", { name: englishProfile.avatar.change }));
    const dialog = await screen.findByRole("dialog", { name: englishProfile.avatar.dialogTitle });
    const fileInput = dialog.querySelector<HTMLInputElement>('input[type="file"]');
    if (fileInput === null) {
      throw new Error("The dropzone has no file input.");
    }
    await user.upload(fileInput, new File(["broken"], "broken.png", { type: "image/png" }));

    expect(await within(dialog).findByRole("alert")).toHaveTextContent(
      englishProfile.avatar.cropFailed,
    );
    expect(uploadAvatar).not.toHaveBeenCalled();
  });

  it("removes the photo", async () => {
    const user = userEvent.setup();
    const currentUser = createSignedInUser({
      avatarFileId: UPLOADED_AVATAR.id,
      avatarUrl: "https://storage.example.test/avatar.png",
    });
    respondToProfilePatch(currentUser);
    const { queryClient } = renderSignedIn(<ProfilePage />, currentUser);

    await user.click(screen.getByRole("button", { name: englishProfile.avatar.remove }));

    expect(apiPatch).toHaveBeenCalledWith("/api/me", { body: { avatarFileId: null } });
    expect(await screen.findByText(englishProfile.avatar.removed)).toBeInTheDocument();
    expect(readCachedUser(queryClient)?.avatarFileId).toBeNull();
    expect(
      screen.queryByRole("button", { name: englishProfile.avatar.remove }),
    ).not.toBeInTheDocument();
  });

  it("saves the theme and the language to the profile", async () => {
    const user = userEvent.setup();
    renderSignedIn(<ProfilePage />);

    await user.click(screen.getByText("Dark"));

    expect(apiPatch).toHaveBeenCalledWith("/api/me", { body: { colorScheme: "dark" } });

    await user.click(screen.getByRole("combobox", { name: englishProfile.preferences.language }));
    await user.click(await screen.findByRole("option", { name: "Français", hidden: true }));

    expect(apiPatch).toHaveBeenCalledWith("/api/me", { body: { language: "fr" } });
    expect(await screen.findByRole("heading", { name: "Profil" })).toBeInTheDocument();
  });

  it("shows a wrong current password on the current password field", async () => {
    respondWithRoutes(apiPut, {
      "/api/me/password": createErrorResult(400, "INVALID_CURRENT_PASSWORD"),
    });
    renderSignedIn(<ProfilePage />);

    await fillPasswordForm("wrong password");

    expect(apiPut).toHaveBeenCalledWith("/api/me/password", {
      body: { currentPassword: "wrong password", newPassword: NEW_PASSWORD },
    });
    expect(await screen.findByText(englishErrors.api.INVALID_CURRENT_PASSWORD)).toBeInTheDocument();
    expect(
      screen.getByLabelText(new RegExp(`^${englishProfile.password.current}`)),
    ).toHaveAccessibleDescription(englishErrors.api.INVALID_CURRENT_PASSWORD);
  });

  it.each(["WEAK_PASSWORD", "PASSWORD_BREACHED"] as const)(
    "shows %s on the new password field",
    async (code) => {
      respondWithRoutes(apiPut, { "/api/me/password": createErrorResult(400, code) });
      renderSignedIn(<ProfilePage />);

      await fillPasswordForm("my current password");

      expect(await screen.findByText(englishErrors.api[code])).toBeInTheDocument();
      expect(
        screen.getByLabelText(new RegExp(`^${englishProfile.password.new}`)),
      ).toHaveAccessibleDescription(expect.stringContaining(englishErrors.api[code]));
    },
  );

  it("changes the password and clears the form", async () => {
    respondWithRoutes(apiPut, { "/api/me/password": createNoContentResult() });
    renderSignedIn(<ProfilePage />);

    await fillPasswordForm("my current password");

    expect(await screen.findByText(englishProfile.password.changed)).toBeInTheDocument();
    expect(screen.getByText(englishProfile.password.otherDevicesSignedOut)).toBeInTheDocument();
    expect(screen.getByLabelText(new RegExp(`^${englishProfile.password.current}`))).toHaveValue(
      "",
    );
  });

  it("regenerates recovery codes after the password and shows 10 codes", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/me/recovery-codes": createSuccessResult({ recoveryCodes: RECOVERY_CODES }),
    });
    renderSignedIn(<ProfilePage />);

    await confirmWithPassword(englishProfile.twoFactor.regenerate);

    expect(apiPost).toHaveBeenCalledWith("/api/me/recovery-codes", {
      body: { password: "my current password" },
    });
    const list = await screen.findByRole("list", { name: englishAuth.recoveryCodes.listLabel });
    expect(list.querySelectorAll("li")).toHaveLength(10);
    expect(
      screen.getByRole("button", { name: englishAuth.recoveryCodes.copy }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: englishAuth.recoveryCodes.download }),
    ).toBeInTheDocument();

    const codesDialog = list.closest<HTMLElement>('[role="dialog"]');
    if (codesDialog === null) {
      throw new Error("The recovery codes are not in a dialog.");
    }
    expect(
      within(codesDialog).getByRole("button", { name: englishAuth.recoveryCodes.copy }),
    ).toBeInTheDocument();
    expect(
      within(codesDialog).getByRole("button", { name: englishAuth.recoveryCodes.download }),
    ).toBeInTheDocument();
    await user.click(
      within(codesDialog).getByRole("checkbox", { name: englishAuth.recoveryCodes.saved }),
    );
    await user.click(
      within(codesDialog).getByRole("button", { name: englishAuth.recoveryCodes.continue }),
    );

    await waitFor(() => {
      expect(
        screen.queryByRole("list", { name: englishAuth.recoveryCodes.listLabel }),
      ).not.toBeInTheDocument();
    });
  });

  it("shows a wrong password inline in the confirm dialog", async () => {
    respondWithRoutes(apiPost, {
      "/api/me/recovery-codes": createErrorResult(400, "INVALID_CURRENT_PASSWORD"),
    });
    renderSignedIn(<ProfilePage />);

    const dialog = await confirmWithPassword(englishProfile.twoFactor.regenerate);

    expect(await within(dialog).findByRole("alert")).toHaveTextContent(
      englishErrors.api.INVALID_CURRENT_PASSWORD,
    );
  });

  it("resets the authenticator and goes to the setup step", async () => {
    respondWithRoutes(apiPost, {
      "/api/me/two-factor/reset": createSuccessResult({ nextStep: "two_factor_setup_required" }),
    });
    const { queryClient } = renderSignedIn(<ProfilePage />);

    const dialog = await confirmWithPassword(englishProfile.twoFactor.reset);

    expect(within(dialog).getByText(englishProfile.twoFactor.resetWarning)).toBeInTheDocument();
    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/two-factor/setup?next=%2Fprofile");
    });
    expect(apiPost).toHaveBeenCalledWith("/api/me/two-factor/reset", {
      body: { password: "my current password" },
    });
    expect(readCachedUser(queryClient)).toMatchObject({
      nextStep: "two_factor_setup_required",
      isTwoFactorSetUp: false,
    });
  });

  it("signs out of all devices after confirmation", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { "/api/auth/sign-out-all": createNoContentResult() });
    const { queryClient } = renderSignedIn(<ProfilePage />);
    queryClient.setQueryData(["GET_PROJECTS_KEY", false], []);

    await user.click(screen.getByRole("button", { name: englishProfile.sessions.action }));
    const dialog = await screen.findByRole("dialog", { name: englishProfile.signOutAll.title });
    expect(await axe(dialog)).toHaveNoViolations();
    await user.click(
      within(dialog).getByRole("button", { name: englishProfile.signOutAll.confirm }),
    );

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/sign-in");
    });
    expect(apiPost).toHaveBeenCalledWith("/api/auth/sign-out-all");
    expect(readCachedUser(queryClient)).toBeUndefined();
    expect(queryClient.getQueryData(["GET_PROJECTS_KEY", false])).toBeUndefined();
  });
});
