from collections.abc import Mapping

from app.modules.notifications.domains.notification_email_texts.entity import NotificationEmailTexts
from app.modules.notifications.typing.enums.notification import NotificationKind, RunOutcome
from app.modules.notifications.typing.enums.report import ReportSource
from app.modules.users import UserLanguage

EMAIL_ON_BY_DEFAULT_KINDS = frozenset({NotificationKind.GAP_ASSIGNED, NotificationKind.FAILURE_ASSIGNED})
EMAIL_SUBJECT_TEMPLATE = "[{project_key}] {title}"
PROFILE_PATH = "/profile"
REPORT_SOURCE_PATHS: Mapping[ReportSource, str] = {
    ReportSource.RUN: "runs",
    ReportSource.PLAN: "plans",
    ReportSource.STORY: "stories",
}

NOTIFICATION_EMAIL_TEXTS: Mapping[UserLanguage, NotificationEmailTexts] = {
    UserLanguage.EN: NotificationEmailTexts(
        greeting="Hello {name},",
        project_line="Project: {project_name} ({project_key})",
        open_line="Open in Tessio: {url}",
        footer=(
            "You get this email because email is on for this kind of notification. "
            "Change it in your profile: {settings_url}"
        ),
        gap_assigned_title="Gap assigned to you on {story_key}",
        failure_assigned_title="Failure assigned to you on {story_key}",
        run_finished_titles={
            RunOutcome.PASSED: "Run passed on {story_key}",
            RunOutcome.FAILED: "Run failed on {story_key}",
            RunOutcome.ABORTED: "Run aborted on {story_key}",
        },
        suite_run_finished_titles={
            RunOutcome.PASSED: "Suite run passed: {suite_name}",
            RunOutcome.FAILED: "Suite run failed: {suite_name}",
            RunOutcome.ABORTED: "Suite run aborted: {suite_name}",
        },
        run_counts="{passed} passed · {failed} failed · {blocked} blocked",
        report_ready_title="Your report is ready: {source_label}",
    ),
    UserLanguage.FR: NotificationEmailTexts(
        greeting="Bonjour {name},",
        project_line="Projet : {project_name} ({project_key})",
        open_line="Ouvrir dans Tessio : {url}",
        footer=(
            "Vous recevez cet e-mail car les e-mails sont activés pour ce type de notification. "
            "Modifiez ce réglage dans votre profil : {settings_url}"
        ),
        gap_assigned_title="Écart qui vous est attribué sur {story_key}",
        failure_assigned_title="Échec qui vous est attribué sur {story_key}",
        run_finished_titles={
            RunOutcome.PASSED: "Exécution réussie sur {story_key}",
            RunOutcome.FAILED: "Exécution en échec sur {story_key}",
            RunOutcome.ABORTED: "Exécution interrompue sur {story_key}",
        },
        suite_run_finished_titles={
            RunOutcome.PASSED: "Exécution de suite réussie : {suite_name}",
            RunOutcome.FAILED: "Exécution de suite en échec : {suite_name}",
            RunOutcome.ABORTED: "Exécution de suite interrompue : {suite_name}",
        },
        run_counts="{passed} réussis · {failed} en échec · {blocked} bloqués",
        report_ready_title="Votre rapport est prêt : {source_label}",
    ),
    UserLanguage.VI: NotificationEmailTexts(
        greeting="Xin chào {name},",
        project_line="Dự án: {project_name} ({project_key})",
        open_line="Mở trong Tessio: {url}",
        footer=(
            "Bạn nhận được email này vì email đang bật cho loại thông báo này. "
            "Thay đổi trong hồ sơ của bạn: {settings_url}"
        ),
        gap_assigned_title="Khoảng trống được giao cho bạn ở {story_key}",
        failure_assigned_title="Lỗi được giao cho bạn ở {story_key}",
        run_finished_titles={
            RunOutcome.PASSED: "Lượt chạy đạt ở {story_key}",
            RunOutcome.FAILED: "Lượt chạy không đạt ở {story_key}",
            RunOutcome.ABORTED: "Lượt chạy bị hủy ở {story_key}",
        },
        suite_run_finished_titles={
            RunOutcome.PASSED: "Lượt chạy bộ kiểm thử đạt: {suite_name}",
            RunOutcome.FAILED: "Lượt chạy bộ kiểm thử không đạt: {suite_name}",
            RunOutcome.ABORTED: "Lượt chạy bộ kiểm thử bị hủy: {suite_name}",
        },
        run_counts="{passed} đạt · {failed} không đạt · {blocked} bị chặn",
        report_ready_title="Báo cáo của bạn đã sẵn sàng: {source_label}",
    ),
}
