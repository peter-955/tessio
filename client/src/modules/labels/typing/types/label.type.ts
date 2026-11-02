import type { components } from "@/lib/api/openapi.type";

export type Label = components["schemas"]["LabelResponse"];

export type CaseLabel = components["schemas"]["CaseLabelResponse"];

export type LabelColor = components["schemas"]["LabelColor"];

export type CreateLabelRequest = components["schemas"]["CreateLabelRequest"];

export type UpdateLabelRequest = components["schemas"]["UpdateLabelRequest"];
