import type { UploadedFile } from "@/lib/uploads/typing/types/uploaded-file.type";
import type { ResultStatus } from "./manual-run.type";

export interface StepDraft {
  status: ResultStatus | null;
  actualResult: string;
  error: string;
  evidenceFile: UploadedFile | null;
  isUploading: boolean;
}
