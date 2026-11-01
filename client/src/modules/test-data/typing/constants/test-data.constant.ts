import type { DataItemKind } from "../types/data-item.type";

export const SECRET_REVEAL_DURATION_IN_MILLISECONDS = 30000;

export const SECRET_MASK = "••••••••";

export const DATA_ITEM_KEY_PATTERN = /^[A-Za-z][A-Za-z0-9_.-]{0,99}$/;

export const MAX_DATA_ITEM_VALUE_LENGTH = 10000;

export const MAX_IMPORT_SIZE_IN_BYTES = 1048576;

export const IMPORT_FILE_EXTENSIONS: readonly string[] = [".env", ".json", ".yaml", ".yml"];

export const DOTENV_FILE_NAME_PREFIX = ".env.";

export const JSON_FILE_EXTENSION = ".json";

export const JSON_CONTENT_TYPE = "application/json";

export const TEXT_CONTENT_TYPE = "text/plain";

export const PROJECT_SCOPE_ID = "project";

export const DATA_ITEM_KINDS: readonly DataItemKind[] = ["variable", "endpoint", "secret"];

export const DATA_GRID_SKELETON_ROW_COUNT = 5;

export const ENDPOINT_LINK_PATTERN = /^https?:\/\//i;
