import type { ApiTokenScope } from "../types/api-token.type";

export const MAX_ACTIVE_API_TOKENS = 10;

export const MAX_API_TOKEN_NAME_LENGTH = 100;

export const TOKEN_LIFETIME_DAYS = ["7", "30", "60", "90"] as const;

export const DEFAULT_TOKEN_LIFETIME = "30";

export const API_TOKEN_START = "tsio_";

export const API_TOKEN_SCOPES = ["mcp", "api"] as const satisfies readonly ApiTokenScope[];

export const DEFAULT_API_TOKEN_SCOPE: ApiTokenScope = "mcp";

export const JUNIT_IMPORT_EXAMPLE_FILE = "results.xml";

export const JUNIT_IMPORT_EXAMPLE_ENVIRONMENT = "Staging";
