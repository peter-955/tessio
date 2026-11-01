import createClient from "openapi-fetch";
import type { paths } from "./openapi.type";

export const apiClient = createClient<paths>({ baseUrl: "", credentials: "same-origin" });
