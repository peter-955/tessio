import { useMemo } from "react";
import { toast } from "sonner";

interface Result {
  showSuccessToast: (title: string, description?: string) => void;
  showErrorToast: (title: string, description?: string) => void;
  showInfoToast: (title: string, description?: string) => void;
  showWarningToast: (title: string, description?: string) => void;
}

export const useShowToast = (): Result => {
  return useMemo((): Result => {
    return {
      showSuccessToast: (title, description): void => {
        toast.success(title, { description });
      },
      showErrorToast: (title, description): void => {
        toast.error(title, { description });
      },
      showInfoToast: (title, description): void => {
        toast.info(title, { description });
      },
      showWarningToast: (title, description): void => {
        toast.warning(title, { description });
      },
    };
  }, []);
};
