"use client";

import {
  DSButton,
  DSCard,
  DSCheckbox,
  DSErrorState,
  DSGroup,
  DSSkeleton,
  DSStack,
  DSTable,
  DSText,
} from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type FormEvent, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePatchNotificationPreferences } from "../../hooks/mutations/use-patch-notification-preferences";
import { useGetNotificationPreferences } from "../../hooks/queries/use-get-notification-preferences";
import { NOTIFICATION_PREFERENCE_KIND_KEYS } from "../../typing/constants/notification-preference.constant";
import type { NotificationPreferenceChannel } from "../../typing/types/notification-preference-channel.type";
import type {
  NotificationPreference,
  NotificationPreferenceKind,
} from "../../typing/types/notification-preference.type";
import {
  buildNotificationPreferenceChanges,
  setNotificationPreference,
} from "../../utils/notification-preference-changes.util";
import styles from "./notification-preferences-card.module.scss";

export const NotificationPreferencesCard: FC = () => {
  const { t } = useTranslation("notificationPreferences");
  const { email } = useCurrentUser();
  const { showSuccessToast } = useShowToast();
  const { data, isPending, isError, isFetching, refetch } = useGetNotificationPreferences();
  const [syncedPreferences, setSyncedPreferences] = useState(data);
  const [draft, setDraft] = useState<NotificationPreference[]>(data ?? []);
  const { mutate: savePreferences, isPending: isSaving } = usePatchNotificationPreferences({
    onSuccess: () => {
      showSuccessToast(t("card.saved"));
    },
  });

  if (data !== syncedPreferences) {
    setSyncedPreferences(data);
    setDraft(data ?? []);
  }

  const changes = data === undefined ? [] : buildNotificationPreferenceChanges(data, draft);

  const handleChange = (
    kind: NotificationPreferenceKind,
    channel: NotificationPreferenceChannel,
    isOn: boolean,
  ): void => {
    setDraft((current) => {
      return setNotificationPreference(current, kind, channel, isOn);
    });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (changes.length > 0) {
      savePreferences({ preferences: changes });
    }
  };

  const renderRow = (preference: NotificationPreference): ReactNode => {
    const kindKey = NOTIFICATION_PREFERENCE_KIND_KEYS[preference.kind];
    const kindTitle = t(`kinds.${kindKey}.title`);

    return (
      <tr key={preference.kind}>
        <th scope="row" className={styles.kindCell}>
          <div className={styles.kindText}>
            <DSText size="sm" weight="medium" component="span">
              {kindTitle}
            </DSText>
            <DSText size="sm" color="muted" component="span">
              {t(`kinds.${kindKey}.description`)}
            </DSText>
          </div>
        </th>
        <td className={styles.channelCell}>
          <div className={styles.checkbox}>
            <DSCheckbox
              label={
                <span className={styles.visuallyHidden}>
                  {t("card.inAppFor", { kind: kindTitle })}
                </span>
              }
              isChecked={preference.inApp}
              isDisabled={isSaving}
              onChange={(isOn) => {
                handleChange(preference.kind, "inApp", isOn);
              }}
            />
          </div>
        </td>
        <td className={styles.channelCell}>
          <div className={styles.checkbox}>
            <DSCheckbox
              label={
                <span className={styles.visuallyHidden}>
                  {t("card.emailFor", { kind: kindTitle })}
                </span>
              }
              isChecked={preference.email}
              isDisabled={isSaving}
              onChange={(isOn) => {
                handleChange(preference.kind, "email", isOn);
              }}
            />
          </div>
        </td>
      </tr>
    );
  };

  const renderContent = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true" aria-label={t("card.loading")}>
          <DSSkeleton lineCount={5} />
        </div>
      );
    }

    if (isError) {
      return (
        <DSErrorState
          title={t("card.loadError")}
          retryLabel={t("card.retry")}
          isRetrying={isFetching}
          titleOrder={3}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    return (
      <form onSubmit={handleSubmit} noValidate>
        <DSStack gap={4}>
          <DSTable label={t("card.tableLabel")}>
            <caption className={styles.visuallyHidden}>{t("card.tableLabel")}</caption>
            <thead>
              <tr>
                <th scope="col">{t("card.notification")}</th>
                <th scope="col" className={styles.channelCell}>
                  {t("card.inApp")}
                </th>
                <th scope="col" className={styles.channelCell}>
                  {t("card.email")}
                </th>
              </tr>
            </thead>
            <tbody>{draft.map(renderRow)}</tbody>
          </DSTable>
          <DSText size="sm" color="muted">
            {t("card.inAppOffNote")}
          </DSText>
          <DSGroup justify="end">
            <DSButton
              type="primary"
              nativeType="submit"
              icon="check"
              isDisabled={changes.length === 0}
              isLoading={isSaving}
            >
              {t("card.save")}
            </DSButton>
          </DSGroup>
        </DSStack>
      </form>
    );
  };

  return (
    <DSCard title={t("card.title")}>
      <DSStack gap={4}>
        <DSText size="sm" color="muted">
          {t("card.description", { email })}
        </DSText>
        {renderContent()}
      </DSStack>
    </DSCard>
  );
};
