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

export const JIRA_USER_EMAIL = "e2e-bot@example.com";

export const JIRA_API_TOKEN = "fake-jira-api-token";
