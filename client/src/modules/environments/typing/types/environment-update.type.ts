import type { EnvironmentRequest } from "./environment.type";

export interface EnvironmentUpdate {
  environmentId: string;
  body: EnvironmentRequest;
}
