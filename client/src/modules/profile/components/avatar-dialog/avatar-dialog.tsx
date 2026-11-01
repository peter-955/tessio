"use client";

import { DSAlert, DSAvatar, DSDropzone, DSModal, DSStack } from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useAvatarUpload } from "@/lib/uploads/hooks/use-avatar-upload";
import {
  AVATAR_CONTENT_TYPES,
  MAX_FILE_SIZE_IN_BYTES,
} from "@/lib/uploads/typing/constants/upload-limits.constant";
import type { UploadedFile } from "@/lib/uploads/typing/types/uploaded-file.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useEffect, useRef, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchMe } from "../../hooks/mutations/use-patch-me";
import { cropImageToSquare } from "../../utils/crop-image-to-square.util";
import styles from "./avatar-dialog.module.scss";

interface Props {
  isOpened: boolean;
  onClose: () => void;
}

interface CroppedImage {
  file: File;
  previewUrl: string;
}

export const AvatarDialog: FC<Props> = ({ isOpened, onClose }) => {
  const { t } = useTranslation("profile");
  const currentUser = useCurrentUser();
  const { showSuccessToast } = useShowToast();
  const { upload, cancel, reset: resetUpload, isUploading } = useAvatarUpload();
  const { mutate: patchMe, isPending: isSaving, reset: resetPatch } = usePatchMe();
  const [croppedImage, setCroppedImage] = useState<CroppedImage | null>(null);
  const [isCropping, setIsCropping] = useState(false);
  const [isCropFailed, setIsCropFailed] = useState(false);
  const previewUrlRef = useRef<string | null>(null);
  const cropAttemptRef = useRef(0);

  const replacePreview = (nextImage: CroppedImage | null): void => {
    if (previewUrlRef.current !== null) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    previewUrlRef.current = nextImage?.previewUrl ?? null;
    setCroppedImage(nextImage);
  };

  useEffect(() => {
    return (): void => {
      if (previewUrlRef.current !== null) {
        URL.revokeObjectURL(previewUrlRef.current);
        previewUrlRef.current = null;
      }
    };
  }, []);

  const handleDrop = (files: File[]): void => {
    const [file] = files;
    if (file === undefined) {
      return;
    }

    cropAttemptRef.current += 1;
    const cropAttempt = cropAttemptRef.current;
    setIsCropFailed(false);
    setIsCropping(true);
    cropImageToSquare(file)
      .then((croppedFile) => {
        if (cropAttempt !== cropAttemptRef.current) {
          return;
        }
        replacePreview({ file: croppedFile, previewUrl: URL.createObjectURL(croppedFile) });
      })
      .catch(() => {
        if (cropAttempt !== cropAttemptRef.current) {
          return;
        }
        replacePreview(null);
        setIsCropFailed(true);
      })
      .finally(() => {
        if (cropAttempt === cropAttemptRef.current) {
          setIsCropping(false);
        }
      });
  };

  const handleClose = (): void => {
    cancel();
    resetUpload();
    resetPatch();
    cropAttemptRef.current += 1;
    replacePreview(null);
    setIsCropping(false);
    setIsCropFailed(false);
    onClose();
  };

  const saveAvatar = async (file: File): Promise<void> => {
    let uploadedFile: UploadedFile;
    try {
      uploadedFile = await upload(file);
    } catch {
      return;
    }

    patchMe(
      { avatarFileId: uploadedFile.id },
      {
        onSuccess: () => {
          showSuccessToast(t("avatar.saved"));
          handleClose();
        },
      },
    );
  };

  const handleSave = (): void => {
    if (croppedImage === null) {
      return;
    }
    void saveAvatar(croppedImage.file);
  };

  return (
    <DSModal
      isOpened={isOpened}
      onClose={handleClose}
      title={t("avatar.dialogTitle")}
      action={{
        label: t("avatar.save"),
        isLoading: isUploading || isSaving,
        isDisabled: croppedImage === null || isCropping,
        onClick: handleSave,
      }}
    >
      <DSStack gap={4}>
        {isCropFailed && <DSAlert color="danger">{t("avatar.cropFailed")}</DSAlert>}
        {croppedImage !== null && (
          <div className={styles.preview}>
            <DSAvatar name={currentUser.name} src={croppedImage.previewUrl} size="xl" />
          </div>
        )}
        <DSDropzone
          title={t("avatar.dropTitle")}
          description={t("avatar.dropDescription")}
          onDrop={handleDrop}
          acceptedTypes={[...AVATAR_CONTENT_TYPES]}
          maxSizeInBytes={MAX_FILE_SIZE_IN_BYTES}
          isMultiple={false}
          isLoading={isCropping}
        />
      </DSStack>
    </DSModal>
  );
};
