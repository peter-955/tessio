import englishAuth from "@/lib/i18n/locales/en/auth.json";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

export const VALID_PASSWORD = "a long enough password";

export const submitNewPassword = async (
  password: string,
  confirmation: string,
  submitLabel: string,
): Promise<void> => {
  const user = userEvent.setup();
  await user.type(
    screen.getByLabelText(new RegExp(`^${englishAuth.newPassword.password}`)),
    password,
  );
  await user.type(
    screen.getByLabelText(new RegExp(`^${englishAuth.newPassword.confirm}`)),
    confirmation,
  );
  await user.click(screen.getByRole("button", { name: submitLabel }));
};
