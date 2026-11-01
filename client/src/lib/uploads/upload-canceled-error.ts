import { ApiError } from "@/lib/api/api-error";

export class UploadCanceledError extends ApiError {
  constructor() {
    super({ status: 0, code: null, message: "Upload canceled." });
    this.name = "UploadCanceledError";
  }
}
