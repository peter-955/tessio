import { expect } from "@playwright/test";
import { MAILPIT_URL } from "../constants/e2e-environment.constant.ts";
import type { MailpitMessageDetail, MailpitSearchResult } from "../types/mailpit-message.type.ts";

const INVITE_PATH_PATTERN = /\/invite\/[A-Za-z0-9_-]+/;
const MAIL_WAIT_TIMEOUT_MILLISECONDS = 30_000;

const readJson = async <ResponseBody>(path: string): Promise<ResponseBody> => {
  const response = await fetch(`${MAILPIT_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Mailpit ${path} answered ${response.status}`);
  }
  const body: ResponseBody = await response.json();
  return body;
};

export const deleteAllMessages = async (): Promise<void> => {
  const response = await fetch(`${MAILPIT_URL}/api/v1/messages`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(`Mailpit could not delete the messages: ${response.status}`);
  }
};

const findLatestMessageId = async (email: string): Promise<string | null> => {
  const query = encodeURIComponent(`to:"${email}"`);
  const result = await readJson<MailpitSearchResult>(`/api/v1/search?query=${query}`);
  return result.messages[0]?.ID ?? null;
};

export const waitForInvitePath = async (email: string): Promise<string> => {
  let messageId: string | null = null;
  await expect
    .poll(
      async () => {
        messageId = await findLatestMessageId(email);
        return messageId;
      },
      { timeout: MAIL_WAIT_TIMEOUT_MILLISECONDS, message: `No invite email for ${email}` },
    )
    .not.toBeNull();
  if (messageId === null) {
    throw new Error(`No invite email for ${email}`);
  }
  const message = await readJson<MailpitMessageDetail>(`/api/v1/message/${messageId}`);
  const invitePath = INVITE_PATH_PATTERN.exec(message.Text)?.[0];
  if (invitePath === undefined) {
    throw new Error(`The invite email for ${email} has no invite link`);
  }
  return invitePath;
};
