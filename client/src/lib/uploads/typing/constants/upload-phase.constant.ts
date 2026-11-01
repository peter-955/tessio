import { UploadPhase } from "../enums/upload-phase.enum";

export const ACTIVE_UPLOAD_PHASES: readonly UploadPhase[] = [
  UploadPhase.SIGNING,
  UploadPhase.UPLOADING,
  UploadPhase.COMPLETING,
];
