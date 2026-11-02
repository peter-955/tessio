import type { components } from "@/lib/api/openapi.type";

export type SharedStep = components["schemas"]["SharedStepResponse"];

export type SharedStepVersion = components["schemas"]["SharedStepVersionResponse"];

export type SharedStepAction = components["schemas"]["SharedStepActionResponse"];

export type SharedStepUsage = components["schemas"]["SharedStepUsageResponse"];

export type CreateSharedStepRequest = components["schemas"]["CreateSharedStepRequest"];

export type UpdateSharedStepRequest = components["schemas"]["UpdateSharedStepRequest"];

export type SharedStepActionRequest = components["schemas"]["SharedStepActionRequest"];
