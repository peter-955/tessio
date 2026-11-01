import type { Environment } from "./environment.type";

export type EnvironmentModalState = { mode: "create" } | { mode: "edit"; environment: Environment };
