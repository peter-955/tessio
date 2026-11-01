import { defineConfig, devices } from "@playwright/test";
import { BASE_URL } from "./support/constants/e2e-environment.constant.ts";

export default defineConfig({
  testDir: "tests",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  maxFailures: 1,
  timeout: 90_000,
  expect: { timeout: 15_000 },
  reporter: [["list"], ["html", { open: "never" }]],
  globalSetup: "./support/global-setup.ts",
  use: {
    baseURL: BASE_URL,
    locale: "en-US",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
