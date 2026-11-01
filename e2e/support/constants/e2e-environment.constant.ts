import path from "node:path";

const E2E_ROOT_DIRECTORY = path.resolve(import.meta.dirname, "..", "..");
const STATE_DIRECTORY = path.join(E2E_ROOT_DIRECTORY, ".state");

export const BASE_URL = process.env.E2E_BASE_URL ?? "http://localhost:3211";

export const MAILPIT_URL = process.env.E2E_MAILPIT_URL ?? "http://localhost:3217";

export const FAKE_JIRA_SITE_URL = process.env.E2E_FAKE_JIRA_SITE_URL ?? "http://fake-jira:3000";

export const SEED_MODE = process.env.E2E_SEED_MODE === "local" ? "local" : "compose";

export const IS_REUSING_STATE = process.env.E2E_REUSE_STATE === "1";

export const LOCAL_DATABASE_URL = process.env.E2E_DATABASE_URL ?? "";

export const E2E_PATHS = {
  root: E2E_ROOT_DIRECTORY,
  composeFile: path.join(E2E_ROOT_DIRECTORY, "compose.e2e.yml"),
  serverDirectory: path.resolve(E2E_ROOT_DIRECTORY, "..", "server"),
  stateDirectory: STATE_DIRECTORY,
  runState: path.join(STATE_DIRECTORY, "run-state.json"),
};

export const STORAGE_STATE_PATHS = {
  owner: path.join(STATE_DIRECTORY, "owner.json"),
  qc: path.join(STATE_DIRECTORY, "qc.json"),
  dev: path.join(STATE_DIRECTORY, "dev.json"),
};
