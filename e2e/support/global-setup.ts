import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync } from "node:fs";
import {
  BASE_URL,
  E2E_PATHS,
  IS_REUSING_STATE,
  LOCAL_DATABASE_URL,
  MAILPIT_URL,
  SEED_MODE,
} from "./constants/e2e-environment.constant.ts";
import { OWNER } from "./constants/e2e-users.constant.ts";
import { deleteAllMessages } from "./utils/mailpit.util.ts";

const SEED_ARGUMENTS = [
  "-m",
  "app.commands.seed_e2e",
  "--owner-email",
  OWNER.email,
  "--owner-name",
  OWNER.name,
  "--owner-password",
  OWNER.password,
  "--owner-totp-key",
  OWNER.totpKey,
];

const probe = async (url: string): Promise<void> => {
  try {
    const response = await fetch(url);
    if (response.status >= 500) {
      throw new Error(`status ${response.status}`);
    }
  } catch (error) {
    throw new Error(
      `${url} is not reachable (${String(error)}). Start the stack with \`npm run stack:up\` first.`,
    );
  }
};

const seed = (): void => {
  if (SEED_MODE === "local") {
    if (LOCAL_DATABASE_URL === "") {
      throw new Error("E2E_SEED_MODE=local needs E2E_DATABASE_URL pointing at a *_e2e database.");
    }
    execFileSync("uv", ["run", "python", ...SEED_ARGUMENTS], {
      cwd: E2E_PATHS.serverDirectory,
      env: { ...process.env, DATABASE_URL: LOCAL_DATABASE_URL },
      stdio: "inherit",
    });
    return;
  }
  execFileSync(
    "docker",
    ["compose", "-f", E2E_PATHS.composeFile, "exec", "-T", "api", "python", ...SEED_ARGUMENTS],
    { stdio: "inherit" },
  );
};

const globalSetup = async (): Promise<void> => {
  if (IS_REUSING_STATE) {
    await probe(`${BASE_URL}/sign-in`);
    return;
  }
  rmSync(E2E_PATHS.stateDirectory, { recursive: true, force: true });
  mkdirSync(E2E_PATHS.stateDirectory, { recursive: true });
  await probe(`${BASE_URL}/sign-in`);
  await probe(`${MAILPIT_URL}/api/v1/info`);
  seed();
  await deleteAllMessages();
};

export default globalSetup;
