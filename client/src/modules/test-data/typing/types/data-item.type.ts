import type { components } from "@/lib/api/openapi.type";

export type DataItem = components["schemas"]["DataItemResponse"];

export type DataItemKind = components["schemas"]["DataItemKind"];

export type CreateDataItemRequest = components["schemas"]["CreateDataItemRequest"];

export type UpdateDataItemRequest = components["schemas"]["UpdateDataItemRequest"];

export type RevealedSecret = components["schemas"]["RevealedSecretResponse"];
