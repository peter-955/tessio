export const PROJECT_KEY = "SHOP";

export const PROJECT_NAME = "Shop";

export const ENVIRONMENT = {
  name: "Staging",
  url: "https://staging.shop.test",
};

export const CASE = {
  title: "Pay with a saved card at checkout",
  priority: "High",
  criterionCode: "AC1",
  steps: [
    { action: "Open the checkout page", expectedResult: "The saved card is listed" },
    { action: "Pay with the saved card", expectedResult: "The order confirmation is shown" },
  ],
};

export const FAILED_STEP_ACTUAL_RESULT = "Payment was declined with error 502";

export const GAP_QUESTION =
  "Which cards count as saved: only cards from past orders, or also wallet cards?";

export const GAP_ANSWER = "Only cards saved from past orders. Wallet cards come in a later story.";

export const CLAUDE_GAP_QUESTION =
  "Which carriers get a tracking link: every carrier, or only the ones we have a contract with?";

export const CLAUDE_GAP_ANSWER =
  "Only contracted carriers (DHL and UPS). Other parcels show the status without a link.";

export const CLAUDE_TOKEN_NAME = "E2E Claude Code";

export const REGRESSION_LABEL = "regression";

export const SUITE_NAME = "Checkout regression";

export const SUITE_GAP_QUESTION =
  "Must the saved card still work after the customer changes their billing address?";

export const SUITE_GAP_ANSWER =
  "Yes. The saved card stays valid; only a new card asks for the address again.";

export const PLAN_NAME = "Release 1.0";

export const JIRA_USER_EMAIL = "e2e-bot@example.com";

export const JIRA_API_TOKEN = "fake-jira-api-token";
