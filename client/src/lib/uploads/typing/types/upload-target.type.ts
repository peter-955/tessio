import type { UploadKind } from "./upload-kind.type";

export interface ProjectUploadTarget {
  kind: UploadKind;
  projectKey: string;
  allowedFileTypes: readonly string[];
}

export interface AvatarUploadTarget {
  kind: "avatar";
}

export type UploadTarget = ProjectUploadTarget | AvatarUploadTarget;
