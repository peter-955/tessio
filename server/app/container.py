from collections.abc import Mapping
from functools import cached_property

import httpx
from mcp.server.mcpserver import MCPServer

from app.config import Settings
from app.modules.ai_harness import GetAiHarnessUseCase
from app.modules.ai_harness.infrastructure import McpServerToolCatalog
from app.modules.api_tokens import (
    AuthenticateApiTokenUseCase,
    CreateApiTokenUseCase,
    ListApiTokensUseCase,
    RevokeApiTokenUseCase,
)
from app.modules.api_tokens.infrastructure import PostgresApiTokenRepository, PostgresApiTokenRevoker
from app.modules.audit import RecordAuditEventUseCase
from app.modules.audit.infrastructure import PostgresAuditEventRepository
from app.modules.auth import (
    AcceptInviteUseCase,
    ApiTokenRevoker,
    AuthenticateSessionUseCase,
    AvatarFileReader,
    ChangePasswordUseCase,
    ChangeWorkspaceRoleUseCase,
    ConfirmTwoFactorSetupUseCase,
    DeactivateUserUseCase,
    DeleteExpiredSessionsJobHandler,
    DeleteExpiredSessionsUseCase,
    GetAvatarLinkUseCase,
    GetWorkspaceUserUseCase,
    InviteUserUseCase,
    InviteWorkspaceUserUseCase,
    ListWorkspaceUsersUseCase,
    ReactivateUserUseCase,
    RegenerateRecoveryCodesUseCase,
    RequestPasswordResetUseCase,
    ResendInviteUseCase,
    ResetOwnTwoFactorUseCase,
    ResetPasswordUseCase,
    ResetUserTwoFactorUseCase,
    SignInWithPasswordUseCase,
    SignOutAllUseCase,
    SignOutUseCase,
    StartTwoFactorSetupUseCase,
    UpdateProfileUseCase,
    VerifyTwoFactorUseCase,
)
from app.modules.auth.infrastructure import (
    Argon2PasswordHasher,
    PostgresAvatarFileReader,
    PostgresOneTimeTokenRepository,
    PostgresRecoveryCodeRepository,
    PostgresUserSessionRepository,
    PwnedPasswordsChecker,
    PyotpTotpAuthenticator,
)
from app.modules.auth.ports.bearer_token_scope_gate import BearerTokenScopeGate
from app.modules.auth.ports.breached_password_checker import BreachedPasswordChecker
from app.modules.failures import (
    ApplyCaseResultUseCase,
    AssignFailureUseCase,
    ChangeFailureCauseUseCase,
    ChangeFailureStatusUseCase,
    CountActiveFailuresUseCase,
    CreateJiraIssueJobHandler,
    CreateJiraIssueUseCase,
    GetFailureUseCase,
    ListFailuresUseCase,
    PreviewJiraIssueUseCase,
    RefreshFailureJiraIssuesUseCase,
    RequestJiraIssueUseCase,
)
from app.modules.failures.infrastructure import (
    PostgresCaseResultReader,
    PostgresFailureAssigneeDirectory,
    PostgresFailureEventRepository,
    PostgresFailureRepository,
    PostgresJiraBugSourceReader,
)
from app.modules.files import (
    CompleteUploadUseCase,
    CreateAvatarUploadUseCase,
    CreateDownloadLinkUseCase,
    CreateUploadUseCase,
    DeleteOrphanFilesJobHandler,
    DeleteOrphanFilesUseCase,
)
from app.modules.files.infrastructure import PostgresProjectFileTypesReader, PostgresStoredFileRepository
from app.modules.gaps import (
    AnswerGapUseCase,
    GetGapUseCase,
    GetMyGapsUseCase,
    GetOpenGapsUseCase,
    ListGapInboxUseCase,
    ListGapsUseCase,
    OpenGapChecker,
    RaiseGapsUseCase,
    ReassignGapUseCase,
    ReopenGapUseCase,
    register_gap_tools,
)
from app.modules.gaps.infrastructure import PostgresGapAssigneeDirectory, PostgresGapRepository, PostgresGapTargetReader
from app.modules.health import CheckReadinessUseCase
from app.modules.health.infrastructure import PostgresReadinessProbe, RedisReadinessProbe
from app.modules.insights import (
    SNAPSHOT_CRON_PATTERN,
    SNAPSHOT_SCHEDULER_ID,
    DailySnapshotJobHandler,
    GetDashboardUseCase,
    GetLabelCoverageUseCase,
    GetMyWorkUseCase,
    GetTokenUsageUseCase,
    GetTraceabilityUseCase,
    GetTrendsUseCase,
    LatestResultCriterionImpactCalculator,
    ListCaseLatestResultsUseCase,
    ListFailingCasesUseCase,
    ListFlakyCasesUseCase,
    ListSprintCoverageUseCase,
    ListStoryProgressUseCase,
    SnapshotDailyStatsUseCase,
)
from app.modules.insights.infrastructure import (
    PostgresActivityReader,
    PostgresCoverageReader,
    PostgresDailyStatsCalculator,
    PostgresDailyStatsRepository,
    PostgresQualityReader,
    PostgresStoryScopeReader,
    PostgresTokenUsageReader,
)
from app.modules.integrations import (
    ChatChannelLiveEventHandler,
    ChatMessageDelivery,
    CreateChatChannelUseCase,
    CreateWebhookUseCase,
    DeleteChatChannelUseCase,
    DeleteOldWebhookDeliveriesJobHandler,
    DeleteOldWebhookDeliveriesUseCase,
    DeleteWebhookUseCase,
    DeliverChatMessageJobHandler,
    DeliverChatMessageUseCase,
    DeliverWebhookJobHandler,
    DeliverWebhookUseCase,
    ListChatChannelsUseCase,
    ListWebhookDeliveriesUseCase,
    ListWebhooksUseCase,
    RedeliverWebhookUseCase,
    RequestChatDeliveriesUseCase,
    RequestWebhookDeliveriesUseCase,
    SendChatChannelTestUseCase,
    UpdateChatChannelUseCase,
    UpdateWebhookUseCase,
)
from app.modules.integrations.infrastructure import (
    HttpxChatWebhookSender,
    HttpxWebhookSender,
    PostgresChatChannelRepository,
    PostgresChatEventReader,
    PostgresWebhookDeliveryRepository,
    PostgresWebhookRepository,
    QueuedChatDeliveryRequester,
    QueuedWebhookDeliveryRequester,
)
from app.modules.integrations.ports.chat_webhook_sender import ChatWebhookSender
from app.modules.integrations.ports.webhook_sender import WebhookSender
from app.modules.jira import (
    CheckJiraWriteAccessUseCase,
    FindJiraWriteAccessUseCase,
    GetJiraConnectionUseCase,
    GetProjectJiraWriteAccessUseCase,
    JiraClient,
    JiraResultCommentRequester,
    ListJiraBoardsUseCase,
    ListJiraProjectsUseCase,
    LoadJiraCredentialsUseCase,
    RefreshJiraWriteAccessUseCase,
    SaveJiraConnectionUseCase,
)
from app.modules.jira.infrastructure import (
    HttpxJiraClient,
    PostgresJiraConnectionChecker,
    PostgresJiraConnectionRepository,
    PostgresLinkedProjectReader,
    QueuedJiraResultCommentRequester,
)
from app.modules.labels import CreateLabelUseCase, DeleteLabelUseCase, ListLabelsUseCase, UpdateLabelUseCase
from app.modules.labels.infrastructure import PostgresLabelRepository, PostgresTestCaseLabelRepository
from app.modules.live_events import StreamLiveEventsUseCase
from app.modules.live_events.typing.constants.live_events import PROJECT_ACCESS_REFRESH_INTERVAL
from app.modules.notifications import (
    CountUnreadNotificationsUseCase,
    ListNotificationPreferencesUseCase,
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
    SendNotificationEmailJobHandler,
    SendNotificationEmailUseCase,
    SendNotificationUseCase,
    UpdateNotificationPreferencesUseCase,
)
from app.modules.notifications.infrastructure import (
    PostgresNotificationEmailRecipientReader,
    PostgresNotificationPreferenceRepository,
    PostgresNotificationRepository,
    PostgresRecipientDirectory,
    QueuedNotificationEmailRequester,
)
from app.modules.plans import (
    ClosePlanUseCase,
    CreatePlanUseCase,
    GetPlanUseCase,
    ListPlansUseCase,
    SetPlanItemsUseCase,
    SignOffPlanUseCase,
    UpdatePlanUseCase,
)
from app.modules.plans.infrastructure import (
    PostgresPlanItemRepository,
    PostgresPlanReferenceReader,
    PostgresPlanViewReader,
    PostgresTestPlanRepository,
)
from app.modules.plugin import (
    CheckPluginVersionUseCase,
    GetPluginArchiveUseCase,
    GetPluginMarketplaceUseCase,
    PluginBundle,
)
from app.modules.plugin.infrastructure import DirectoryPluginBundleLoader
from app.modules.projects import (
    ArchiveProjectUseCase,
    CreateProjectUseCase,
    GetProjectUseCase,
    GetUserAccessUseCase,
    JiraConnectionChecker,
    ListMemberCandidatesUseCase,
    ListProjectMembersUseCase,
    ListProjectsUseCase,
    RemoveProjectMemberUseCase,
    SetProjectMemberUseCase,
    UnarchiveProjectUseCase,
    UpdateProjectUseCase,
)
from app.modules.projects.infrastructure import (
    PostgresMemberDirectory,
    PostgresProjectAccessResolver,
    PostgresProjectMemberRepository,
    PostgresProjectRepository,
)
from app.modules.projects.ports.environment_checker import EnvironmentChecker
from app.modules.reports import (
    ExportReportJobHandler,
    ExportReportUseCase,
    PdfRenderer,
    ReportDocumentLoader,
    ReportFileWriter,
    RequestReportExportUseCase,
)
from app.modules.reports.infrastructure import (
    PostgresReportRequesterReader,
    S3ReportFileWriter,
    WeasyPrintPdfRenderer,
)
from app.modules.run_logs import GetRunLogUseCase, UploadRunLogUseCase
from app.modules.run_logs.infrastructure import PostgresRunLogRepository
from app.modules.runs import (
    AbortStaleRunsJobHandler,
    AbortStaleRunsUseCase,
    CaseResultRecordedHandler,
    CreateManualRunUseCase,
    CreateScreenshotUploadUseCase,
    CriterionImpactCalculator,
    FinishManualRunUseCase,
    FinishRunUseCase,
    FlakyRecomputeRequester,
    GetFailedCasesUseCase,
    GetRunUseCase,
    ImportJunitRunUseCase,
    JiraCommentSourceReader,
    ListRunsUseCase,
    PostJiraResultCommentJobHandler,
    PostJiraResultCommentUseCase,
    RecordCaseResultUseCase,
    RecordManualCaseResultUseCase,
    RerunFailedCasesUseCase,
    RunStartGate,
    ScreenshotVerifier,
    StartRunUseCase,
    register_run_tools,
)
from app.modules.runs.infrastructure import (
    PostgresCaseResultHistoryReader,
    PostgresCaseResultRepository,
    PostgresEnvironmentUsageChecker,
    PostgresImportCaseReader,
    PostgresJiraCommentSourceReader,
    PostgresRunCaseRepository,
    PostgresRunFileRepository,
    PostgresRunGapReader,
    PostgresRunningRunChecker,
    PostgresRunRepository,
    PostgresRunStoryReader,
    PostgresRunTargetReader,
    PostgresRunViewReader,
    QueuedFlakyRecomputeRequester,
)
from app.modules.shared_steps import (
    CreateSharedStepUseCase,
    GetSharedStepUseCase,
    ListSharedStepsUseCase,
    ListSharedStepUsageUseCase,
    UpdateSharedStepUseCase,
)
from app.modules.shared_steps.infrastructure import PostgresSharedStepRepository, PostgresSharedStepUsageReader
from app.modules.stories import (
    ActiveFailureCounter,
    ChangeTestStatusUseCase,
    CreateWrittenStoryUseCase,
    CriteriaChangedHandler,
    DeleteWrittenStoryUseCase,
    GetSprintUseCase,
    GetStoryUseCase,
    GetSyncStatusUseCase,
    JiraIssueStatusRefresher,
    ListSprintsUseCase,
    ListStoriesUseCase,
    MarkStoryInTestUseCase,
    RequestJiraSyncUseCase,
    RunningRunChecker,
    SyncJiraProjectJobHandler,
    SyncJiraProjectUseCase,
    UpdateWrittenStoryUseCase,
)
from app.modules.stories.infrastructure import (
    PostgresAcceptanceCriterionRepository,
    PostgresProjectSyncStateRepository,
    PostgresSprintRepository,
    PostgresStoryKeyCounterRepository,
    PostgresStoryRepository,
    PostgresStoryUsageChecker,
    PostgresSyncTargetReader,
)
from app.modules.story_context import (
    GetStoryContextUseCase,
    GetTestFileUseCase,
    ResolveDataUseCase,
    register_story_context_tools,
)
from app.modules.story_context.infrastructure import (
    PostgresRunFileRecorder,
    PostgresRunScopeReader,
    PostgresStoryContextReader,
)
from app.modules.suites import (
    AddSuiteCasesByFilterUseCase,
    ArchiveSuiteUseCase,
    CreateSuiteUseCase,
    GetSuiteContextUseCase,
    GetSuiteUseCase,
    ListSuitesUseCase,
    SetSuiteCasesUseCase,
    UpdateSuiteUseCase,
    register_suite_tools,
)
from app.modules.suites.infrastructure import (
    PostgresSuiteCaseRepository,
    PostgresSuiteRunScopeReader,
    PostgresSuiteViewReader,
    PostgresTestSuiteRepository,
)
from app.modules.test_cases import (
    AddReviewCommentUseCase,
    AttachTestFileUseCase,
    CaseStepExpander,
    ChangeTestCaseStatusUseCase,
    CheckDraftCasesUseCase,
    CommitTestCaseImportUseCase,
    CreateDraftCasesUseCase,
    CreateTestCaseUseCase,
    FlagCasesForReviewUseCase,
    GetTestCaseUseCase,
    ListQuarantineEventsUseCase,
    ListReviewCommentsUseCase,
    ListTestCasesUseCase,
    ListTestCaseVersionsUseCase,
    ListTestFileVersionsUseCase,
    MarkTestCaseReviewedUseCase,
    PreviewTestCaseImportUseCase,
    QuarantineTestCaseUseCase,
    RecomputeFlakyJobHandler,
    RecomputeFlakyUseCase,
    ReleaseTestCaseQuarantineUseCase,
    ResolveReviewCommentUseCase,
    SetTestCaseLabelsUseCase,
    SweepFlakyJobHandler,
    SweepFlakyUseCase,
    UpdateTestCaseUseCase,
    register_test_case_tools,
)
from app.modules.test_cases.infrastructure import (
    PostgresCriterionReader,
    PostgresDataKeyReader,
    PostgresQuarantineEventRepository,
    PostgresReviewCommentRepository,
    PostgresReviewPolicyReader,
    PostgresStoryReader,
    PostgresTestCaseCounterRepository,
    PostgresTestCaseQualityRepository,
    PostgresTestCaseRepository,
    PostgresTestCaseVersionRepository,
    PostgresTestFileRepository,
    PostgresTestFileVersionRepository,
)
from app.modules.test_data import (
    ArchiveEnvironmentUseCase,
    CommitImportUseCase,
    CreateDataItemUseCase,
    CreateEnvironmentUseCase,
    DeleteDataItemUseCase,
    DeleteEnvironmentUseCase,
    EnvironmentUsageChecker,
    ImportFileReader,
    ListDataItemsUseCase,
    ListEffectiveDataItemsUseCase,
    ListEnvironmentsUseCase,
    PreviewImportUseCase,
    RevealSecretUseCase,
    SecretValueReader,
    SetTestDataUseCase,
    UnarchiveEnvironmentUseCase,
    UpdateDataItemUseCase,
    UpdateEnvironmentUseCase,
    register_test_data_tools,
)
from app.modules.test_data.infrastructure import (
    PostgresDataItemRepository,
    PostgresDataKeyDescriptionRepository,
    PostgresEnvironmentChecker,
    PostgresEnvironmentRepository,
    StorageImportFileReader,
)
from app.modules.users.infrastructure import PostgresUserRepository
from app.shared.crypto import AesGcmSecretCipher, parse_key_ring
from app.shared.events import (
    LiveEventHandler,
    LiveEventHub,
    LiveEventListener,
    LiveEventPublisher,
    RedisLiveEventHub,
    RedisLiveEventPublisher,
)
from app.shared.mailer import Mailer, QueuedMailer, SendEmailJobHandler, SmtpMailer
from app.shared.permissions import ProjectAccessResolver
from app.shared.postgres import Database
from app.shared.queue import BullmqJobQueue, BullmqJobWorker, JobHandler, JobQueue, JobSchedule, build_job_workers
from app.shared.rate_limit import RateLimiter, RedisRateLimiter
from app.shared.storage import ObjectStorage, S3ObjectStorage, build_s3_client
from app.shared.typing.enums import JobName, QueueName


class Container:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def is_session_cookie_secure(self) -> bool:
        return self._settings.security.is_session_cookie_secure

    @property
    def allowed_origins(self) -> set[str]:
        return {self._settings.client.client_url}

    @cached_property
    def http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=5)

    @cached_property
    def breached_password_checker(self) -> BreachedPasswordChecker:
        return PwnedPasswordsChecker(self.http_client)

    @cached_property
    def database(self) -> Database:
        return Database(self._settings.database.database_url)

    @cached_property
    def job_queue(self) -> JobQueue:
        return BullmqJobQueue(self._settings.queue.redis_url)

    @cached_property
    def mailer(self) -> Mailer:
        return QueuedMailer(self.job_queue)

    @cached_property
    def smtp_mailer(self) -> Mailer:
        mail = self._settings.mail
        return SmtpMailer(
            mail.smtp_host,
            mail.smtp_port,
            mail.mail_sender,
            mail.smtp_username or None,
            None if mail.smtp_password is None else mail.smtp_password.get_secret_value() or None,
            mail.smtp_security,
        )

    @cached_property
    def secret_cipher(self) -> AesGcmSecretCipher:
        security = self._settings.security
        key_ring = parse_key_ring(
            security.encryption_key.get_secret_value(),
            security.encryption_key_id,
            None if security.previous_encryption_keys is None else security.previous_encryption_keys.get_secret_value(),
        )
        return AesGcmSecretCipher(key_ring, security.encryption_key_id)

    @cached_property
    def object_storage(self) -> ObjectStorage:
        storage = self._settings.storage
        access_key_id = None if storage.s3_access_key_id is None else storage.s3_access_key_id.get_secret_value()
        secret_access_key = (
            None if storage.s3_secret_access_key is None else storage.s3_secret_access_key.get_secret_value()
        )
        client = build_s3_client(storage.s3_endpoint_url, storage.s3_region, access_key_id, secret_access_key)
        signing_client = build_s3_client(
            storage.s3_public_endpoint_url or storage.s3_endpoint_url,
            storage.s3_region,
            access_key_id,
            secret_access_key,
        )
        return S3ObjectStorage(client, signing_client, storage.s3_bucket)

    @cached_property
    def live_event_publisher(self) -> LiveEventPublisher:
        return RedisLiveEventPublisher(self._settings.queue.redis_url)

    @cached_property
    def rate_limiter(self) -> RateLimiter:
        return RedisRateLimiter(self._settings.queue.redis_url)

    @cached_property
    def live_event_hub(self) -> LiveEventHub:
        return RedisLiveEventHub(self._settings.queue.redis_url)

    @cached_property
    def password_hasher(self) -> Argon2PasswordHasher:
        return Argon2PasswordHasher()

    @cached_property
    def totp_authenticator(self) -> PyotpTotpAuthenticator:
        return PyotpTotpAuthenticator()

    @cached_property
    def user_repository(self) -> PostgresUserRepository:
        return PostgresUserRepository(self.database)

    @cached_property
    def user_session_repository(self) -> PostgresUserSessionRepository:
        return PostgresUserSessionRepository(self.database)

    @cached_property
    def recovery_code_repository(self) -> PostgresRecoveryCodeRepository:
        return PostgresRecoveryCodeRepository(self.database)

    @cached_property
    def one_time_token_repository(self) -> PostgresOneTimeTokenRepository:
        return PostgresOneTimeTokenRepository(self.database)

    @cached_property
    def invite_user(self) -> InviteUserUseCase:
        return InviteUserUseCase(
            self.database,
            self.user_repository,
            self.one_time_token_repository,
            self.mailer,
            self._settings.client.client_url,
        )

    @cached_property
    def accept_invite(self) -> AcceptInviteUseCase:
        return AcceptInviteUseCase(
            self.database,
            self.user_repository,
            self.one_time_token_repository,
            self.user_session_repository,
            self.password_hasher,
            self.breached_password_checker,
        )

    @cached_property
    def request_password_reset(self) -> RequestPasswordResetUseCase:
        return RequestPasswordResetUseCase(
            self.database,
            self.user_repository,
            self.one_time_token_repository,
            self.rate_limiter,
            self.mailer,
            self._settings.client.client_url,
        )

    @cached_property
    def reset_password(self) -> ResetPasswordUseCase:
        return ResetPasswordUseCase(
            self.database,
            self.user_repository,
            self.one_time_token_repository,
            self.user_session_repository,
            self.password_hasher,
            self.breached_password_checker,
        )

    @cached_property
    def sign_in_with_password(self) -> SignInWithPasswordUseCase:
        return SignInWithPasswordUseCase(
            self.database, self.user_repository, self.user_session_repository, self.password_hasher
        )

    @cached_property
    def start_two_factor_setup(self) -> StartTwoFactorSetupUseCase:
        return StartTwoFactorSetupUseCase(
            self.database, self.user_repository, self.totp_authenticator, self.secret_cipher
        )

    @cached_property
    def confirm_two_factor_setup(self) -> ConfirmTwoFactorSetupUseCase:
        return ConfirmTwoFactorSetupUseCase(
            self.database,
            self.user_repository,
            self.user_session_repository,
            self.recovery_code_repository,
            self.totp_authenticator,
            self.secret_cipher,
        )

    @cached_property
    def verify_two_factor(self) -> VerifyTwoFactorUseCase:
        return VerifyTwoFactorUseCase(
            self.database,
            self.user_repository,
            self.user_session_repository,
            self.recovery_code_repository,
            self.totp_authenticator,
            self.secret_cipher,
        )

    @cached_property
    def authenticate_session(self) -> AuthenticateSessionUseCase:
        return AuthenticateSessionUseCase(self.database, self.user_repository, self.user_session_repository)

    @cached_property
    def sign_out(self) -> SignOutUseCase:
        return SignOutUseCase(self.database, self.user_session_repository)

    @cached_property
    def api_token_revoker(self) -> ApiTokenRevoker:
        return PostgresApiTokenRevoker(self.database)

    @cached_property
    def avatar_file_reader(self) -> AvatarFileReader:
        return PostgresAvatarFileReader(self.database)

    @cached_property
    def list_workspace_users(self) -> ListWorkspaceUsersUseCase:
        return ListWorkspaceUsersUseCase(self.database, self.user_repository)

    @cached_property
    def get_workspace_user(self) -> GetWorkspaceUserUseCase:
        return GetWorkspaceUserUseCase(self.database, self.user_repository)

    @cached_property
    def invite_workspace_user(self) -> InviteWorkspaceUserUseCase:
        return InviteWorkspaceUserUseCase(self.invite_user)

    @cached_property
    def resend_invite(self) -> ResendInviteUseCase:
        return ResendInviteUseCase(
            self.database,
            self.user_repository,
            self.one_time_token_repository,
            self.mailer,
            self._settings.client.client_url,
        )

    @cached_property
    def deactivate_user(self) -> DeactivateUserUseCase:
        return DeactivateUserUseCase(
            self.database,
            self.user_repository,
            self.user_session_repository,
            self.one_time_token_repository,
            self.api_token_revoker,
        )

    @cached_property
    def reactivate_user(self) -> ReactivateUserUseCase:
        return ReactivateUserUseCase(
            self.database,
            self.user_repository,
            self.one_time_token_repository,
            self.mailer,
            self._settings.client.client_url,
        )

    @cached_property
    def reset_user_two_factor(self) -> ResetUserTwoFactorUseCase:
        return ResetUserTwoFactorUseCase(
            self.database, self.user_repository, self.user_session_repository, self.recovery_code_repository
        )

    @cached_property
    def change_workspace_role(self) -> ChangeWorkspaceRoleUseCase:
        return ChangeWorkspaceRoleUseCase(self.database, self.user_repository)

    @cached_property
    def get_avatar_link(self) -> GetAvatarLinkUseCase:
        return GetAvatarLinkUseCase(self.database, self.user_repository, self.avatar_file_reader, self.object_storage)

    @cached_property
    def update_profile(self) -> UpdateProfileUseCase:
        return UpdateProfileUseCase(self.database, self.user_repository, self.avatar_file_reader)

    @cached_property
    def change_password(self) -> ChangePasswordUseCase:
        return ChangePasswordUseCase(
            self.database,
            self.user_repository,
            self.user_session_repository,
            self.password_hasher,
            self.breached_password_checker,
        )

    @cached_property
    def regenerate_recovery_codes(self) -> RegenerateRecoveryCodesUseCase:
        return RegenerateRecoveryCodesUseCase(self.database, self.recovery_code_repository, self.password_hasher)

    @cached_property
    def reset_own_two_factor(self) -> ResetOwnTwoFactorUseCase:
        return ResetOwnTwoFactorUseCase(
            self.database,
            self.user_repository,
            self.user_session_repository,
            self.recovery_code_repository,
            self.password_hasher,
        )

    @cached_property
    def sign_out_all(self) -> SignOutAllUseCase:
        return SignOutAllUseCase(self.database, self.user_session_repository)

    @cached_property
    def delete_expired_sessions(self) -> DeleteExpiredSessionsUseCase:
        return DeleteExpiredSessionsUseCase(self.database, self.user_session_repository)

    @cached_property
    def project_repository(self) -> PostgresProjectRepository:
        return PostgresProjectRepository(self.database)

    @cached_property
    def project_member_repository(self) -> PostgresProjectMemberRepository:
        return PostgresProjectMemberRepository(self.database)

    @cached_property
    def member_directory(self) -> PostgresMemberDirectory:
        return PostgresMemberDirectory(self.database)

    @cached_property
    def project_access_resolver(self) -> ProjectAccessResolver:
        return PostgresProjectAccessResolver(self.database)

    @cached_property
    def jira_connection_checker(self) -> JiraConnectionChecker:
        return PostgresJiraConnectionChecker(self.database)

    @cached_property
    def list_projects(self) -> ListProjectsUseCase:
        return ListProjectsUseCase(self.database, self.project_repository, self.project_member_repository)

    @cached_property
    def create_project(self) -> CreateProjectUseCase:
        return CreateProjectUseCase(
            self.database, self.project_repository, self.project_member_repository, self.jira_connection_checker
        )

    @cached_property
    def get_project(self) -> GetProjectUseCase:
        return GetProjectUseCase(self.database, self.project_access_resolver, self.project_repository)

    @cached_property
    def update_project(self) -> UpdateProjectUseCase:
        return UpdateProjectUseCase(
            self.database, self.project_access_resolver, self.project_repository, self.environment_checker
        )

    @cached_property
    def archive_project(self) -> ArchiveProjectUseCase:
        return ArchiveProjectUseCase(self.database, self.project_access_resolver, self.project_repository)

    @cached_property
    def unarchive_project(self) -> UnarchiveProjectUseCase:
        return UnarchiveProjectUseCase(self.database, self.project_access_resolver, self.project_repository)

    @cached_property
    def list_project_members(self) -> ListProjectMembersUseCase:
        return ListProjectMembersUseCase(self.database, self.project_access_resolver, self.member_directory)

    @cached_property
    def set_project_member(self) -> SetProjectMemberUseCase:
        return SetProjectMemberUseCase(
            self.database,
            self.project_access_resolver,
            self.project_repository,
            self.project_member_repository,
            self.user_repository,
            self.live_event_publisher,
        )

    @cached_property
    def remove_project_member(self) -> RemoveProjectMemberUseCase:
        return RemoveProjectMemberUseCase(
            self.database,
            self.project_access_resolver,
            self.project_repository,
            self.project_member_repository,
            self.live_event_publisher,
        )

    @cached_property
    def list_member_candidates(self) -> ListMemberCandidatesUseCase:
        return ListMemberCandidatesUseCase(self.database, self.project_access_resolver, self.member_directory)

    @cached_property
    def get_user_access(self) -> GetUserAccessUseCase:
        return GetUserAccessUseCase(
            self.database, self.user_repository, self.project_repository, self.project_member_repository
        )

    @cached_property
    def audit_event_repository(self) -> PostgresAuditEventRepository:
        return PostgresAuditEventRepository(self.database)

    @cached_property
    def record_audit_event(self) -> RecordAuditEventUseCase:
        return RecordAuditEventUseCase(self.database, self.audit_event_repository)

    @cached_property
    def stored_file_repository(self) -> PostgresStoredFileRepository:
        return PostgresStoredFileRepository(self.database)

    @cached_property
    def project_file_types_reader(self) -> PostgresProjectFileTypesReader:
        return PostgresProjectFileTypesReader(self.database)

    @cached_property
    def create_upload(self) -> CreateUploadUseCase:
        return CreateUploadUseCase(
            self.database,
            self.project_access_resolver,
            self.stored_file_repository,
            self.project_file_types_reader,
            self.object_storage,
        )

    @cached_property
    def complete_upload(self) -> CompleteUploadUseCase:
        return CompleteUploadUseCase(
            self.database, self.project_access_resolver, self.stored_file_repository, self.object_storage
        )

    @cached_property
    def create_download_link(self) -> CreateDownloadLinkUseCase:
        return CreateDownloadLinkUseCase(
            self.database, self.project_access_resolver, self.stored_file_repository, self.object_storage
        )

    @cached_property
    def create_avatar_upload(self) -> CreateAvatarUploadUseCase:
        return CreateAvatarUploadUseCase(self.database, self.stored_file_repository, self.object_storage)

    @cached_property
    def delete_orphan_files(self) -> DeleteOrphanFilesUseCase:
        return DeleteOrphanFilesUseCase(self.database, self.stored_file_repository, self.object_storage)

    @cached_property
    def api_token_repository(self) -> PostgresApiTokenRepository:
        return PostgresApiTokenRepository(self.database)

    @cached_property
    def create_api_token(self) -> CreateApiTokenUseCase:
        return CreateApiTokenUseCase(
            self.database,
            self.project_access_resolver,
            self.project_repository,
            self.project_member_repository,
            self.api_token_repository,
        )

    @cached_property
    def list_api_tokens(self) -> ListApiTokensUseCase:
        return ListApiTokensUseCase(self.database, self.api_token_repository)

    @cached_property
    def revoke_api_token(self) -> RevokeApiTokenUseCase:
        return RevokeApiTokenUseCase(self.database, self.api_token_repository)

    @cached_property
    def authenticate_api_token(self) -> AuthenticateApiTokenUseCase:
        return AuthenticateApiTokenUseCase(
            self.database,
            self.api_token_repository,
            self.user_repository,
            self.project_access_resolver,
            self.check_plugin_version,
        )

    @cached_property
    def bearer_token_scope_gate(self) -> BearerTokenScopeGate:
        return self.authenticate_api_token

    @cached_property
    def plugin_bundle(self) -> PluginBundle:
        return DirectoryPluginBundleLoader(self._settings.plugin.plugin_dir).load()

    @cached_property
    def check_plugin_version(self) -> CheckPluginVersionUseCase:
        return CheckPluginVersionUseCase(self.plugin_bundle.version)

    @cached_property
    def get_plugin_marketplace(self) -> GetPluginMarketplaceUseCase:
        return GetPluginMarketplaceUseCase(self.plugin_bundle, self._settings.client.client_url)

    @cached_property
    def get_plugin_archive(self) -> GetPluginArchiveUseCase:
        return GetPluginArchiveUseCase(self.plugin_bundle)

    @cached_property
    def get_ai_harness(self) -> GetAiHarnessUseCase:
        return GetAiHarnessUseCase(
            self.plugin_bundle,
            McpServerToolCatalog(self.mcp_server),
            self._settings.release.server_version,
            self._settings.release.build_commit,
            self._settings.client.client_url,
        )

    @cached_property
    def jira_client(self) -> JiraClient:
        return HttpxJiraClient(self.http_client)

    @cached_property
    def jira_connection_repository(self) -> PostgresJiraConnectionRepository:
        return PostgresJiraConnectionRepository(self.database)

    @cached_property
    def linked_project_reader(self) -> PostgresLinkedProjectReader:
        return PostgresLinkedProjectReader(self.database)

    @cached_property
    def get_jira_connection(self) -> GetJiraConnectionUseCase:
        return GetJiraConnectionUseCase(self.database, self.jira_connection_repository)

    @cached_property
    def save_jira_connection(self) -> SaveJiraConnectionUseCase:
        return SaveJiraConnectionUseCase(
            self.database,
            self.jira_connection_repository,
            self.jira_client,
            self.secret_cipher,
            self.check_jira_write_access,
        )

    @cached_property
    def check_jira_write_access(self) -> CheckJiraWriteAccessUseCase:
        return CheckJiraWriteAccessUseCase(self.database, self.linked_project_reader, self.jira_client)

    @cached_property
    def refresh_jira_write_access(self) -> RefreshJiraWriteAccessUseCase:
        return RefreshJiraWriteAccessUseCase(
            self.database, self.jira_connection_repository, self.secret_cipher, self.check_jira_write_access
        )

    @cached_property
    def find_jira_write_access(self) -> FindJiraWriteAccessUseCase:
        return FindJiraWriteAccessUseCase(self.database, self.jira_connection_repository)

    @cached_property
    def get_project_jira_write_access(self) -> GetProjectJiraWriteAccessUseCase:
        return GetProjectJiraWriteAccessUseCase(
            self.database, self.project_access_resolver, self.linked_project_reader, self.jira_connection_repository
        )

    @cached_property
    def jira_result_comment_requester(self) -> JiraResultCommentRequester:
        return QueuedJiraResultCommentRequester(self.database, self.job_queue)

    @cached_property
    def jira_comment_source_reader(self) -> JiraCommentSourceReader:
        return PostgresJiraCommentSourceReader(self.database)

    @cached_property
    def post_jira_result_comment(self) -> PostJiraResultCommentUseCase:
        return PostJiraResultCommentUseCase(
            self.database,
            self.jira_comment_source_reader,
            self.load_jira_credentials,
            self.jira_client,
            self._settings.client.client_url,
        )

    @cached_property
    def jira_bug_source_reader(self) -> PostgresJiraBugSourceReader:
        return PostgresJiraBugSourceReader(self.database)

    @cached_property
    def request_jira_issue(self) -> RequestJiraIssueUseCase:
        return RequestJiraIssueUseCase(
            self.database,
            self.project_access_resolver,
            self.failure_repository,
            self.jira_bug_source_reader,
            self.find_jira_write_access,
            self.job_queue,
            self.live_event_publisher,
        )

    @cached_property
    def preview_jira_issue(self) -> PreviewJiraIssueUseCase:
        return PreviewJiraIssueUseCase(
            self.database,
            self.project_access_resolver,
            self.failure_repository,
            self.jira_bug_source_reader,
            self.case_result_reader,
            self.secret_value_reader,
            self._settings.client.client_url,
        )

    @cached_property
    def create_jira_issue(self) -> CreateJiraIssueUseCase:
        return CreateJiraIssueUseCase(
            self.database,
            self.failure_repository,
            self.failure_event_repository,
            self.jira_bug_source_reader,
            self.case_result_reader,
            self.secret_value_reader,
            self.load_jira_credentials,
            self.jira_client,
            self.stored_file_repository,
            self.object_storage,
            self.live_event_publisher,
            self._settings.client.client_url,
        )

    @cached_property
    def jira_issue_status_refresher(self) -> JiraIssueStatusRefresher:
        return self.refresh_failure_jira_issues

    @cached_property
    def refresh_failure_jira_issues(self) -> RefreshFailureJiraIssuesUseCase:
        return RefreshFailureJiraIssuesUseCase(
            self.database, self.failure_repository, self.jira_client, self.live_event_publisher
        )

    @cached_property
    def list_jira_projects(self) -> ListJiraProjectsUseCase:
        return ListJiraProjectsUseCase(
            self.database,
            self.jira_connection_repository,
            self.secret_cipher,
            self.jira_client,
            self.linked_project_reader,
        )

    @cached_property
    def list_jira_boards(self) -> ListJiraBoardsUseCase:
        return ListJiraBoardsUseCase(
            self.database,
            self.jira_connection_repository,
            self.secret_cipher,
            self.jira_client,
            self.linked_project_reader,
            self.project_access_resolver,
        )

    @cached_property
    def load_jira_credentials(self) -> LoadJiraCredentialsUseCase:
        return LoadJiraCredentialsUseCase(self.database, self.jira_connection_repository, self.secret_cipher)

    @cached_property
    def environment_repository(self) -> PostgresEnvironmentRepository:
        return PostgresEnvironmentRepository(self.database)

    @cached_property
    def data_item_repository(self) -> PostgresDataItemRepository:
        return PostgresDataItemRepository(self.database)

    @cached_property
    def data_key_description_repository(self) -> PostgresDataKeyDescriptionRepository:
        return PostgresDataKeyDescriptionRepository(self.database)

    @cached_property
    def environment_checker(self) -> EnvironmentChecker:
        return PostgresEnvironmentChecker(self.database)

    @cached_property
    def environment_usage_checker(self) -> EnvironmentUsageChecker:
        return PostgresEnvironmentUsageChecker(self.database)

    @cached_property
    def import_file_reader(self) -> ImportFileReader:
        return StorageImportFileReader(self.database, self.object_storage)

    @cached_property
    def secret_value_reader(self) -> SecretValueReader:
        return SecretValueReader(self.database, self.data_item_repository, self.secret_cipher)

    @cached_property
    def list_environments(self) -> ListEnvironmentsUseCase:
        return ListEnvironmentsUseCase(self.database, self.project_access_resolver, self.environment_repository)

    @cached_property
    def create_environment(self) -> CreateEnvironmentUseCase:
        return CreateEnvironmentUseCase(self.database, self.project_access_resolver, self.environment_repository)

    @cached_property
    def update_environment(self) -> UpdateEnvironmentUseCase:
        return UpdateEnvironmentUseCase(self.database, self.project_access_resolver, self.environment_repository)

    @cached_property
    def archive_environment(self) -> ArchiveEnvironmentUseCase:
        return ArchiveEnvironmentUseCase(self.database, self.project_access_resolver, self.environment_repository)

    @cached_property
    def unarchive_environment(self) -> UnarchiveEnvironmentUseCase:
        return UnarchiveEnvironmentUseCase(self.database, self.project_access_resolver, self.environment_repository)

    @cached_property
    def delete_environment(self) -> DeleteEnvironmentUseCase:
        return DeleteEnvironmentUseCase(
            self.database, self.project_access_resolver, self.environment_repository, self.environment_usage_checker
        )

    @cached_property
    def list_data_items(self) -> ListDataItemsUseCase:
        return ListDataItemsUseCase(self.database, self.project_access_resolver, self.data_item_repository)

    @cached_property
    def list_effective_data_items(self) -> ListEffectiveDataItemsUseCase:
        return ListEffectiveDataItemsUseCase(
            self.database, self.project_access_resolver, self.environment_repository, self.data_item_repository
        )

    @cached_property
    def create_data_item(self) -> CreateDataItemUseCase:
        return CreateDataItemUseCase(
            self.database,
            self.project_access_resolver,
            self.environment_repository,
            self.data_item_repository,
            self.data_key_description_repository,
            self.secret_cipher,
        )

    @cached_property
    def update_data_item(self) -> UpdateDataItemUseCase:
        return UpdateDataItemUseCase(
            self.database,
            self.project_access_resolver,
            self.data_item_repository,
            self.data_key_description_repository,
            self.secret_cipher,
        )

    @cached_property
    def delete_data_item(self) -> DeleteDataItemUseCase:
        return DeleteDataItemUseCase(
            self.database,
            self.project_access_resolver,
            self.data_item_repository,
            self.data_key_description_repository,
        )

    @cached_property
    def set_test_data(self) -> SetTestDataUseCase:
        return SetTestDataUseCase(
            self.database,
            self.project_access_resolver,
            self.environment_repository,
            self.data_item_repository,
            self.secret_cipher,
        )

    @cached_property
    def reveal_secret(self) -> RevealSecretUseCase:
        return RevealSecretUseCase(
            self.database,
            self.project_access_resolver,
            self.data_item_repository,
            self.secret_cipher,
            self.record_audit_event,
        )

    @cached_property
    def preview_import(self) -> PreviewImportUseCase:
        return PreviewImportUseCase(
            self.database,
            self.project_access_resolver,
            self.environment_repository,
            self.data_item_repository,
            self.import_file_reader,
            self.secret_cipher,
        )

    @cached_property
    def commit_import(self) -> CommitImportUseCase:
        return CommitImportUseCase(
            self.database,
            self.project_access_resolver,
            self.environment_repository,
            self.data_item_repository,
            self.data_key_description_repository,
            self.import_file_reader,
            self.secret_cipher,
        )

    @cached_property
    def sprint_repository(self) -> PostgresSprintRepository:
        return PostgresSprintRepository(self.database)

    @cached_property
    def story_repository(self) -> PostgresStoryRepository:
        return PostgresStoryRepository(self.database)

    @cached_property
    def acceptance_criterion_repository(self) -> PostgresAcceptanceCriterionRepository:
        return PostgresAcceptanceCriterionRepository(self.database)

    @cached_property
    def project_sync_state_repository(self) -> PostgresProjectSyncStateRepository:
        return PostgresProjectSyncStateRepository(self.database)

    @cached_property
    def sync_target_reader(self) -> PostgresSyncTargetReader:
        return PostgresSyncTargetReader(self.database)

    @cached_property
    def criteria_changed_handler(self) -> CriteriaChangedHandler:
        return self.flag_cases_for_review

    @cached_property
    def active_failure_counter(self) -> ActiveFailureCounter:
        return self.count_active_failures

    @cached_property
    def running_run_checker(self) -> RunningRunChecker:
        return PostgresRunningRunChecker(self.database)

    @cached_property
    def list_sprints(self) -> ListSprintsUseCase:
        return ListSprintsUseCase(self.database, self.project_access_resolver, self.sprint_repository)

    @cached_property
    def get_sprint(self) -> GetSprintUseCase:
        return GetSprintUseCase(self.database, self.project_access_resolver, self.sprint_repository)

    @cached_property
    def list_stories(self) -> ListStoriesUseCase:
        return ListStoriesUseCase(self.database, self.project_access_resolver, self.story_repository)

    @cached_property
    def get_story(self) -> GetStoryUseCase:
        return GetStoryUseCase(
            self.database,
            self.project_access_resolver,
            self.story_repository,
            self.sprint_repository,
            self.acceptance_criterion_repository,
        )

    @cached_property
    def get_sync_status(self) -> GetSyncStatusUseCase:
        return GetSyncStatusUseCase(self.database, self.project_access_resolver, self.project_sync_state_repository)

    @cached_property
    def request_jira_sync(self) -> RequestJiraSyncUseCase:
        return RequestJiraSyncUseCase(
            self.database,
            self.project_access_resolver,
            self.project_sync_state_repository,
            self.jira_connection_checker,
            self.sync_target_reader,
            self.job_queue,
            self.live_event_publisher,
        )

    @cached_property
    def story_key_counter_repository(self) -> PostgresStoryKeyCounterRepository:
        return PostgresStoryKeyCounterRepository(self.database)

    @cached_property
    def story_usage_checker(self) -> PostgresStoryUsageChecker:
        return PostgresStoryUsageChecker(self.database)

    @cached_property
    def create_written_story(self) -> CreateWrittenStoryUseCase:
        return CreateWrittenStoryUseCase(
            self.database,
            self.project_access_resolver,
            self.sync_target_reader,
            self.story_repository,
            self.acceptance_criterion_repository,
            self.story_key_counter_repository,
            self.live_event_publisher,
        )

    @cached_property
    def update_written_story(self) -> UpdateWrittenStoryUseCase:
        return UpdateWrittenStoryUseCase(
            self.database,
            self.project_access_resolver,
            self.story_repository,
            self.acceptance_criterion_repository,
            self.criteria_changed_handler,
            self.live_event_publisher,
        )

    @cached_property
    def delete_written_story(self) -> DeleteWrittenStoryUseCase:
        return DeleteWrittenStoryUseCase(
            self.database,
            self.project_access_resolver,
            self.story_repository,
            self.acceptance_criterion_repository,
            self.story_usage_checker,
            self.live_event_publisher,
        )

    @cached_property
    def sync_jira_project(self) -> SyncJiraProjectUseCase:
        return SyncJiraProjectUseCase(
            self.database,
            self.sync_target_reader,
            self.project_sync_state_repository,
            self.sprint_repository,
            self.story_repository,
            self.acceptance_criterion_repository,
            self.load_jira_credentials,
            self.jira_client,
            self.criteria_changed_handler,
            self.live_event_publisher,
            self.refresh_jira_write_access,
            self.jira_issue_status_refresher,
        )

    @cached_property
    def change_test_status(self) -> ChangeTestStatusUseCase:
        return ChangeTestStatusUseCase(
            self.database,
            self.project_access_resolver,
            self.story_repository,
            self.sprint_repository,
            self.acceptance_criterion_repository,
            self.active_failure_counter,
            self.running_run_checker,
            self.live_event_publisher,
            self.jira_result_comment_requester,
        )

    @cached_property
    def mark_story_in_test(self) -> MarkStoryInTestUseCase:
        return MarkStoryInTestUseCase(self.database, self.story_repository)

    @cached_property
    def test_case_repository(self) -> PostgresTestCaseRepository:
        return PostgresTestCaseRepository(self.database)

    @cached_property
    def test_case_counter_repository(self) -> PostgresTestCaseCounterRepository:
        return PostgresTestCaseCounterRepository(self.database)

    @cached_property
    def test_case_version_repository(self) -> PostgresTestCaseVersionRepository:
        return PostgresTestCaseVersionRepository(self.database)

    @cached_property
    def test_file_repository(self) -> PostgresTestFileRepository:
        return PostgresTestFileRepository(self.database)

    @cached_property
    def test_file_version_repository(self) -> PostgresTestFileVersionRepository:
        return PostgresTestFileVersionRepository(self.database)

    @cached_property
    def case_story_reader(self) -> PostgresStoryReader:
        return PostgresStoryReader(self.database)

    @cached_property
    def case_criterion_reader(self) -> PostgresCriterionReader:
        return PostgresCriterionReader(self.database)

    @cached_property
    def data_key_reader(self) -> PostgresDataKeyReader:
        return PostgresDataKeyReader(self.database)

    @cached_property
    def label_repository(self) -> PostgresLabelRepository:
        return PostgresLabelRepository(self.database)

    @cached_property
    def test_case_label_repository(self) -> PostgresTestCaseLabelRepository:
        return PostgresTestCaseLabelRepository(self.database)

    @cached_property
    def shared_step_repository(self) -> PostgresSharedStepRepository:
        return PostgresSharedStepRepository(self.database)

    @cached_property
    def shared_step_usage_reader(self) -> PostgresSharedStepUsageReader:
        return PostgresSharedStepUsageReader(self.database)

    @cached_property
    def case_step_expander(self) -> CaseStepExpander:
        return CaseStepExpander(self.shared_step_repository)

    @cached_property
    def list_shared_steps(self) -> ListSharedStepsUseCase:
        return ListSharedStepsUseCase(
            self.database, self.project_access_resolver, self.shared_step_repository, self.shared_step_usage_reader
        )

    @cached_property
    def create_shared_step(self) -> CreateSharedStepUseCase:
        return CreateSharedStepUseCase(
            self.database, self.project_access_resolver, self.shared_step_repository, self.live_event_publisher
        )

    @cached_property
    def get_shared_step(self) -> GetSharedStepUseCase:
        return GetSharedStepUseCase(
            self.database, self.project_access_resolver, self.shared_step_repository, self.shared_step_usage_reader
        )

    @cached_property
    def update_shared_step(self) -> UpdateSharedStepUseCase:
        return UpdateSharedStepUseCase(
            self.database,
            self.project_access_resolver,
            self.shared_step_repository,
            self.shared_step_usage_reader,
            self.live_event_publisher,
        )

    @cached_property
    def list_shared_step_usage(self) -> ListSharedStepUsageUseCase:
        return ListSharedStepUsageUseCase(
            self.database, self.project_access_resolver, self.shared_step_repository, self.shared_step_usage_reader
        )

    @cached_property
    def list_labels(self) -> ListLabelsUseCase:
        return ListLabelsUseCase(self.database, self.project_access_resolver, self.label_repository)

    @cached_property
    def create_label(self) -> CreateLabelUseCase:
        return CreateLabelUseCase(
            self.database, self.project_access_resolver, self.label_repository, self.live_event_publisher
        )

    @cached_property
    def update_label(self) -> UpdateLabelUseCase:
        return UpdateLabelUseCase(
            self.database, self.project_access_resolver, self.label_repository, self.live_event_publisher
        )

    @cached_property
    def delete_label(self) -> DeleteLabelUseCase:
        return DeleteLabelUseCase(
            self.database, self.project_access_resolver, self.label_repository, self.live_event_publisher
        )

    @cached_property
    def set_test_case_labels(self) -> SetTestCaseLabelsUseCase:
        return SetTestCaseLabelsUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.label_repository,
            self.test_case_label_repository,
            self.live_event_publisher,
        )

    @cached_property
    def list_test_cases(self) -> ListTestCasesUseCase:
        return ListTestCasesUseCase(
            self.database, self.project_access_resolver, self.test_case_repository, self.test_case_label_repository
        )

    @cached_property
    def get_test_case(self) -> GetTestCaseUseCase:
        return GetTestCaseUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
        )

    @cached_property
    def create_test_case(self) -> CreateTestCaseUseCase:
        return CreateTestCaseUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
            self.test_case_counter_repository,
            self.live_event_publisher,
            self.shared_step_repository,
            self.secret_value_reader,
        )

    @cached_property
    def update_test_case(self) -> UpdateTestCaseUseCase:
        return UpdateTestCaseUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
            self.live_event_publisher,
            self.shared_step_repository,
            self.secret_value_reader,
        )

    @cached_property
    def list_test_case_versions(self) -> ListTestCaseVersionsUseCase:
        return ListTestCaseVersionsUseCase(
            self.database, self.project_access_resolver, self.test_case_repository, self.test_case_version_repository
        )

    @cached_property
    def change_test_case_status(self) -> ChangeTestCaseStatusUseCase:
        return ChangeTestCaseStatusUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
            self.live_event_publisher,
            self.review_comment_repository,
            self.review_policy_reader,
        )

    @cached_property
    def mark_test_case_reviewed(self) -> MarkTestCaseReviewedUseCase:
        return MarkTestCaseReviewedUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
            self.live_event_publisher,
            self.review_policy_reader,
        )

    @cached_property
    def review_comment_repository(self) -> PostgresReviewCommentRepository:
        return PostgresReviewCommentRepository(self.database)

    @cached_property
    def review_policy_reader(self) -> PostgresReviewPolicyReader:
        return PostgresReviewPolicyReader(self.database)

    @cached_property
    def list_review_comments(self) -> ListReviewCommentsUseCase:
        return ListReviewCommentsUseCase(
            self.database, self.project_access_resolver, self.test_case_repository, self.review_comment_repository
        )

    @cached_property
    def add_review_comment(self) -> AddReviewCommentUseCase:
        return AddReviewCommentUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_version_repository,
            self.review_comment_repository,
            self.live_event_publisher,
        )

    @cached_property
    def resolve_review_comment(self) -> ResolveReviewCommentUseCase:
        return ResolveReviewCommentUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.review_comment_repository,
            self.live_event_publisher,
        )

    @cached_property
    def attach_test_file(self) -> AttachTestFileUseCase:
        return AttachTestFileUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
            self.test_file_version_repository,
            self.stored_file_repository,
            self.live_event_publisher,
        )

    @cached_property
    def list_test_file_versions(self) -> ListTestFileVersionsUseCase:
        return ListTestFileVersionsUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_file_repository,
            self.test_file_version_repository,
        )

    @cached_property
    def preview_test_case_import(self) -> PreviewTestCaseImportUseCase:
        return PreviewTestCaseImportUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.import_file_reader,
        )

    @cached_property
    def commit_test_case_import(self) -> CommitTestCaseImportUseCase:
        return CommitTestCaseImportUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.import_file_reader,
            self.test_case_counter_repository,
            self.live_event_publisher,
        )

    @cached_property
    def check_draft_cases(self) -> CheckDraftCasesUseCase:
        return CheckDraftCasesUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.case_story_reader,
            self.case_criterion_reader,
        )

    @cached_property
    def create_draft_cases(self) -> CreateDraftCasesUseCase:
        return CreateDraftCasesUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.test_case_counter_repository,
            self.live_event_publisher,
        )

    @cached_property
    def flag_cases_for_review(self) -> FlagCasesForReviewUseCase:
        return FlagCasesForReviewUseCase(self.database, self.test_case_repository)

    @cached_property
    def gap_repository(self) -> PostgresGapRepository:
        return PostgresGapRepository(self.database)

    @cached_property
    def gap_target_reader(self) -> PostgresGapTargetReader:
        return PostgresGapTargetReader(self.database)

    @cached_property
    def gap_assignee_directory(self) -> PostgresGapAssigneeDirectory:
        return PostgresGapAssigneeDirectory(self.database)

    @cached_property
    def raise_gaps(self) -> RaiseGapsUseCase:
        return RaiseGapsUseCase(
            self.database,
            self.project_access_resolver,
            self.gap_repository,
            self.gap_target_reader,
            self.gap_assignee_directory,
            self.send_notification,
            self.live_event_publisher,
        )

    @cached_property
    def list_gaps(self) -> ListGapsUseCase:
        return ListGapsUseCase(self.database, self.project_access_resolver, self.gap_repository, self.gap_target_reader)

    @cached_property
    def get_open_gaps(self) -> GetOpenGapsUseCase:
        return GetOpenGapsUseCase(
            self.database, self.project_access_resolver, self.gap_repository, self.gap_target_reader
        )

    @cached_property
    def get_gap(self) -> GetGapUseCase:
        return GetGapUseCase(self.database, self.project_access_resolver, self.gap_repository)

    @cached_property
    def list_gap_inbox(self) -> ListGapInboxUseCase:
        return ListGapInboxUseCase(self.database, self.project_access_resolver, self.gap_repository)

    @cached_property
    def answer_gap(self) -> AnswerGapUseCase:
        return AnswerGapUseCase(
            self.database, self.project_access_resolver, self.gap_repository, self.live_event_publisher
        )

    @cached_property
    def reopen_gap(self) -> ReopenGapUseCase:
        return ReopenGapUseCase(
            self.database,
            self.project_access_resolver,
            self.gap_repository,
            self.gap_assignee_directory,
            self.send_notification,
            self.live_event_publisher,
        )

    @cached_property
    def reassign_gap(self) -> ReassignGapUseCase:
        return ReassignGapUseCase(
            self.database,
            self.project_access_resolver,
            self.gap_repository,
            self.gap_assignee_directory,
            self.send_notification,
            self.live_event_publisher,
        )

    @cached_property
    def get_my_gaps(self) -> GetMyGapsUseCase:
        return GetMyGapsUseCase(
            self.database,
            self.project_access_resolver,
            self.gap_repository,
            self.gap_target_reader,
            self.gap_assignee_directory,
            self._settings.client.client_url,
        )

    @cached_property
    def open_gap_checker(self) -> OpenGapChecker:
        return OpenGapChecker(self.database, self.gap_repository)

    @cached_property
    def notification_repository(self) -> PostgresNotificationRepository:
        return PostgresNotificationRepository(self.database)

    @cached_property
    def recipient_directory(self) -> PostgresRecipientDirectory:
        return PostgresRecipientDirectory(self.database)

    @cached_property
    def send_notification(self) -> SendNotificationUseCase:
        return SendNotificationUseCase(
            self.database,
            self.notification_repository,
            self.recipient_directory,
            self.live_event_publisher,
            self.notification_preference_repository,
            self.notification_email_requester,
        )

    @cached_property
    def notification_preference_repository(self) -> PostgresNotificationPreferenceRepository:
        return PostgresNotificationPreferenceRepository(self.database)

    @cached_property
    def notification_email_requester(self) -> QueuedNotificationEmailRequester:
        return QueuedNotificationEmailRequester(self.job_queue)

    @cached_property
    def notification_email_recipient_reader(self) -> PostgresNotificationEmailRecipientReader:
        return PostgresNotificationEmailRecipientReader(self.database)

    @cached_property
    def send_notification_email(self) -> SendNotificationEmailUseCase:
        return SendNotificationEmailUseCase(
            self.database,
            self.notification_email_recipient_reader,
            self.notification_preference_repository,
            self.smtp_mailer,
            self._settings.client.client_url,
        )

    @cached_property
    def list_notification_preferences(self) -> ListNotificationPreferencesUseCase:
        return ListNotificationPreferencesUseCase(self.database, self.notification_preference_repository)

    @cached_property
    def update_notification_preferences(self) -> UpdateNotificationPreferencesUseCase:
        return UpdateNotificationPreferencesUseCase(self.database, self.notification_preference_repository)

    @cached_property
    def chat_channel_repository(self) -> PostgresChatChannelRepository:
        return PostgresChatChannelRepository(self.database)

    @cached_property
    def chat_event_reader(self) -> PostgresChatEventReader:
        return PostgresChatEventReader(self.database)

    @cached_property
    def chat_webhook_sender(self) -> ChatWebhookSender:
        return HttpxChatWebhookSender(self.http_client)

    @cached_property
    def chat_delivery_requester(self) -> QueuedChatDeliveryRequester:
        return QueuedChatDeliveryRequester(self.job_queue)

    @cached_property
    def chat_message_delivery(self) -> ChatMessageDelivery:
        return ChatMessageDelivery(
            self.database,
            self.chat_channel_repository,
            self.secret_cipher,
            self.chat_webhook_sender,
            self.live_event_publisher,
        )

    @cached_property
    def list_chat_channels(self) -> ListChatChannelsUseCase:
        return ListChatChannelsUseCase(self.database, self.project_access_resolver, self.chat_channel_repository)

    @cached_property
    def create_chat_channel(self) -> CreateChatChannelUseCase:
        return CreateChatChannelUseCase(
            self.database,
            self.project_access_resolver,
            self.chat_channel_repository,
            self.secret_cipher,
            self.live_event_publisher,
        )

    @cached_property
    def update_chat_channel(self) -> UpdateChatChannelUseCase:
        return UpdateChatChannelUseCase(
            self.database,
            self.project_access_resolver,
            self.chat_channel_repository,
            self.secret_cipher,
            self.live_event_publisher,
        )

    @cached_property
    def delete_chat_channel(self) -> DeleteChatChannelUseCase:
        return DeleteChatChannelUseCase(
            self.database, self.project_access_resolver, self.chat_channel_repository, self.live_event_publisher
        )

    @cached_property
    def send_chat_channel_test(self) -> SendChatChannelTestUseCase:
        return SendChatChannelTestUseCase(
            self.database,
            self.project_access_resolver,
            self.chat_channel_repository,
            self.chat_event_reader,
            self.chat_message_delivery,
            self._settings.client.client_url,
        )

    @cached_property
    def request_chat_deliveries(self) -> RequestChatDeliveriesUseCase:
        return RequestChatDeliveriesUseCase(self.database, self.chat_channel_repository, self.chat_delivery_requester)

    @cached_property
    def deliver_chat_message(self) -> DeliverChatMessageUseCase:
        return DeliverChatMessageUseCase(
            self.database,
            self.chat_channel_repository,
            self.chat_event_reader,
            self.chat_message_delivery,
            self._settings.client.client_url,
        )

    @cached_property
    def list_notifications(self) -> ListNotificationsUseCase:
        return ListNotificationsUseCase(self.database, self.project_access_resolver, self.notification_repository)

    @cached_property
    def count_unread_notifications(self) -> CountUnreadNotificationsUseCase:
        return CountUnreadNotificationsUseCase(
            self.database, self.project_access_resolver, self.notification_repository
        )

    @cached_property
    def mark_notification_read(self) -> MarkNotificationReadUseCase:
        return MarkNotificationReadUseCase(self.database, self.notification_repository)

    @cached_property
    def mark_all_notifications_read(self) -> MarkAllNotificationsReadUseCase:
        return MarkAllNotificationsReadUseCase(self.database, self.notification_repository)

    @cached_property
    def run_repository(self) -> PostgresRunRepository:
        return PostgresRunRepository(self.database)

    @cached_property
    def run_case_repository(self) -> PostgresRunCaseRepository:
        return PostgresRunCaseRepository(self.database)

    @cached_property
    def case_result_repository(self) -> PostgresCaseResultRepository:
        return PostgresCaseResultRepository(self.database)

    @cached_property
    def run_file_repository(self) -> PostgresRunFileRepository:
        return PostgresRunFileRepository(self.database)

    @cached_property
    def run_target_reader(self) -> PostgresRunTargetReader:
        return PostgresRunTargetReader(self.database)

    @cached_property
    def run_view_reader(self) -> PostgresRunViewReader:
        return PostgresRunViewReader(self.database)

    @cached_property
    def run_story_reader(self) -> PostgresRunStoryReader:
        return PostgresRunStoryReader(self.database)

    @cached_property
    def case_result_recorded_handler(self) -> CaseResultRecordedHandler:
        return self.apply_case_result

    @cached_property
    def criterion_impact_calculator(self) -> CriterionImpactCalculator:
        return LatestResultCriterionImpactCalculator(self.database, self.coverage_reader)

    @cached_property
    def run_start_gate(self) -> RunStartGate:
        return RunStartGate(
            self.open_gap_checker,
            self.run_repository,
            self.run_case_repository,
            self.run_target_reader,
            self.mark_story_in_test,
            self.suite_run_scope_reader,
            self.run_gap_reader,
            self.case_step_expander,
        )

    @cached_property
    def run_gap_reader(self) -> PostgresRunGapReader:
        return PostgresRunGapReader(self.database)

    @cached_property
    def suite_run_scope_reader(self) -> PostgresSuiteRunScopeReader:
        return PostgresSuiteRunScopeReader(self.database)

    @cached_property
    def test_suite_repository(self) -> PostgresTestSuiteRepository:
        return PostgresTestSuiteRepository(self.database)

    @cached_property
    def suite_case_repository(self) -> PostgresSuiteCaseRepository:
        return PostgresSuiteCaseRepository(self.database)

    @cached_property
    def suite_view_reader(self) -> PostgresSuiteViewReader:
        return PostgresSuiteViewReader(self.database)

    @cached_property
    def list_suites(self) -> ListSuitesUseCase:
        return ListSuitesUseCase(self.database, self.project_access_resolver, self.suite_view_reader)

    @cached_property
    def get_suite(self) -> GetSuiteUseCase:
        return GetSuiteUseCase(
            self.database, self.project_access_resolver, self.test_suite_repository, self.suite_view_reader
        )

    @cached_property
    def create_suite(self) -> CreateSuiteUseCase:
        return CreateSuiteUseCase(
            self.database, self.project_access_resolver, self.test_suite_repository, self.live_event_publisher
        )

    @cached_property
    def update_suite(self) -> UpdateSuiteUseCase:
        return UpdateSuiteUseCase(
            self.database,
            self.project_access_resolver,
            self.test_suite_repository,
            self.suite_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def archive_suite(self) -> ArchiveSuiteUseCase:
        return ArchiveSuiteUseCase(
            self.database,
            self.project_access_resolver,
            self.test_suite_repository,
            self.suite_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def set_suite_cases(self) -> SetSuiteCasesUseCase:
        return SetSuiteCasesUseCase(
            self.database,
            self.project_access_resolver,
            self.test_suite_repository,
            self.suite_case_repository,
            self.suite_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def add_suite_cases_by_filter(self) -> AddSuiteCasesByFilterUseCase:
        return AddSuiteCasesByFilterUseCase(
            self.database,
            self.project_access_resolver,
            self.test_suite_repository,
            self.suite_case_repository,
            self.suite_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def get_suite_context(self) -> GetSuiteContextUseCase:
        return GetSuiteContextUseCase(
            self.database,
            self.project_access_resolver,
            self.suite_run_scope_reader,
            self.test_suite_repository,
            self.story_context_reader,
        )

    @cached_property
    def test_plan_repository(self) -> PostgresTestPlanRepository:
        return PostgresTestPlanRepository(self.database)

    @cached_property
    def plan_item_repository(self) -> PostgresPlanItemRepository:
        return PostgresPlanItemRepository(self.database)

    @cached_property
    def plan_view_reader(self) -> PostgresPlanViewReader:
        return PostgresPlanViewReader(self.database)

    @cached_property
    def plan_reference_reader(self) -> PostgresPlanReferenceReader:
        return PostgresPlanReferenceReader(self.database)

    @cached_property
    def list_plans(self) -> ListPlansUseCase:
        return ListPlansUseCase(self.database, self.project_access_resolver, self.plan_view_reader)

    @cached_property
    def get_plan(self) -> GetPlanUseCase:
        return GetPlanUseCase(
            self.database, self.project_access_resolver, self.test_plan_repository, self.plan_view_reader
        )

    @cached_property
    def create_plan(self) -> CreatePlanUseCase:
        return CreatePlanUseCase(
            self.database,
            self.project_access_resolver,
            self.test_plan_repository,
            self.plan_reference_reader,
            self.plan_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def update_plan(self) -> UpdatePlanUseCase:
        return UpdatePlanUseCase(
            self.database,
            self.project_access_resolver,
            self.test_plan_repository,
            self.plan_reference_reader,
            self.plan_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def set_plan_items(self) -> SetPlanItemsUseCase:
        return SetPlanItemsUseCase(
            self.database,
            self.project_access_resolver,
            self.test_plan_repository,
            self.plan_item_repository,
            self.plan_reference_reader,
            self.plan_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def sign_off_plan(self) -> SignOffPlanUseCase:
        return SignOffPlanUseCase(
            self.database,
            self.project_access_resolver,
            self.test_plan_repository,
            self.plan_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def close_plan(self) -> ClosePlanUseCase:
        return ClosePlanUseCase(
            self.database,
            self.project_access_resolver,
            self.test_plan_repository,
            self.plan_view_reader,
            self.live_event_publisher,
        )

    @cached_property
    def screenshot_verifier(self) -> ScreenshotVerifier:
        return ScreenshotVerifier(self.case_result_repository, self.stored_file_repository, self.object_storage)

    @cached_property
    def start_run(self) -> StartRunUseCase:
        return StartRunUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.run_target_reader,
            self.run_start_gate,
            self.live_event_publisher,
        )

    @cached_property
    def record_case_result(self) -> RecordCaseResultUseCase:
        return RecordCaseResultUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.stored_file_repository,
            self.secret_value_reader,
            self.case_result_recorded_handler,
            self.flaky_recompute_requester,
            self.live_event_publisher,
        )

    @cached_property
    def finish_run(self) -> FinishRunUseCase:
        return FinishRunUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.run_story_reader,
            self.screenshot_verifier,
            self.criterion_impact_calculator,
            self.secret_value_reader,
            self.send_notification,
            self.live_event_publisher,
            self.jira_result_comment_requester,
        )

    @cached_property
    def get_failed_cases(self) -> GetFailedCasesUseCase:
        return GetFailedCasesUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.run_target_reader,
            self.run_story_reader,
        )

    @cached_property
    def create_screenshot_upload(self) -> CreateScreenshotUploadUseCase:
        return CreateScreenshotUploadUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.case_result_repository,
            self.object_storage,
        )

    @cached_property
    def list_runs(self) -> ListRunsUseCase:
        return ListRunsUseCase(
            self.database, self.project_access_resolver, self.run_target_reader, self.run_view_reader
        )

    @cached_property
    def get_run(self) -> GetRunUseCase:
        return GetRunUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.run_view_reader,
            self.data_item_repository,
        )

    @cached_property
    def create_manual_run(self) -> CreateManualRunUseCase:
        return CreateManualRunUseCase(
            self.database, self.project_access_resolver, self.run_start_gate, self.live_event_publisher
        )

    @cached_property
    def record_manual_case_result(self) -> RecordManualCaseResultUseCase:
        return RecordManualCaseResultUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.test_case_version_repository,
            self.stored_file_repository,
            self.secret_value_reader,
            self.case_result_recorded_handler,
            self.flaky_recompute_requester,
            self.live_event_publisher,
        )

    @cached_property
    def finish_manual_run(self) -> FinishManualRunUseCase:
        return FinishManualRunUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.screenshot_verifier,
            self.criterion_impact_calculator,
            self.secret_value_reader,
            self.run_story_reader,
            self.send_notification,
            self.live_event_publisher,
            self.jira_result_comment_requester,
        )

    @cached_property
    def rerun_failed_cases(self) -> RerunFailedCasesUseCase:
        return RerunFailedCasesUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.run_start_gate,
            self.live_event_publisher,
        )

    @cached_property
    def import_case_reader(self) -> PostgresImportCaseReader:
        return PostgresImportCaseReader(self.database)

    @cached_property
    def import_junit_run(self) -> ImportJunitRunUseCase:
        return ImportJunitRunUseCase(
            self.database,
            self.project_access_resolver,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.run_target_reader,
            self.run_start_gate,
            self.import_case_reader,
            self.criterion_impact_calculator,
            self.secret_value_reader,
            self.run_story_reader,
            self.case_result_recorded_handler,
            self.flaky_recompute_requester,
            self.send_notification,
            self.live_event_publisher,
            self.jira_result_comment_requester,
        )

    @cached_property
    def abort_stale_runs(self) -> AbortStaleRunsUseCase:
        return AbortStaleRunsUseCase(
            self.database,
            self.run_repository,
            self.run_case_repository,
            self.case_result_repository,
            self.screenshot_verifier,
            self.criterion_impact_calculator,
            self.run_story_reader,
            self.send_notification,
            self.live_event_publisher,
        )

    @cached_property
    def failure_repository(self) -> PostgresFailureRepository:
        return PostgresFailureRepository(self.database)

    @cached_property
    def failure_event_repository(self) -> PostgresFailureEventRepository:
        return PostgresFailureEventRepository(self.database)

    @cached_property
    def failure_assignee_directory(self) -> PostgresFailureAssigneeDirectory:
        return PostgresFailureAssigneeDirectory(self.database)

    @cached_property
    def case_result_reader(self) -> PostgresCaseResultReader:
        return PostgresCaseResultReader(self.database)

    @cached_property
    def apply_case_result(self) -> ApplyCaseResultUseCase:
        return ApplyCaseResultUseCase(self.database, self.failure_repository, self.failure_event_repository)

    @cached_property
    def count_active_failures(self) -> CountActiveFailuresUseCase:
        return CountActiveFailuresUseCase(self.database, self.failure_repository)

    @cached_property
    def list_failures(self) -> ListFailuresUseCase:
        return ListFailuresUseCase(self.database, self.project_access_resolver, self.failure_repository)

    @cached_property
    def get_failure(self) -> GetFailureUseCase:
        return GetFailureUseCase(
            self.database,
            self.project_access_resolver,
            self.failure_repository,
            self.failure_event_repository,
            self.case_result_reader,
        )

    @cached_property
    def change_failure_status(self) -> ChangeFailureStatusUseCase:
        return ChangeFailureStatusUseCase(
            self.database,
            self.project_access_resolver,
            self.failure_repository,
            self.failure_event_repository,
            self.live_event_publisher,
        )

    @cached_property
    def assign_failure(self) -> AssignFailureUseCase:
        return AssignFailureUseCase(
            self.database,
            self.project_access_resolver,
            self.failure_repository,
            self.failure_event_repository,
            self.failure_assignee_directory,
            self.send_notification,
            self.live_event_publisher,
        )

    @cached_property
    def change_failure_cause(self) -> ChangeFailureCauseUseCase:
        return ChangeFailureCauseUseCase(
            self.database,
            self.project_access_resolver,
            self.failure_repository,
            self.failure_event_repository,
            self.live_event_publisher,
        )

    @cached_property
    def story_context_reader(self) -> PostgresStoryContextReader:
        return PostgresStoryContextReader(self.database, self.case_step_expander)

    @cached_property
    def story_context_run_reader(self) -> PostgresRunScopeReader:
        return PostgresRunScopeReader(self.database)

    @cached_property
    def run_file_recorder(self) -> PostgresRunFileRecorder:
        return PostgresRunFileRecorder(self.database)

    @cached_property
    def get_story_context(self) -> GetStoryContextUseCase:
        return GetStoryContextUseCase(self.database, self.project_access_resolver, self.story_context_reader)

    @cached_property
    def resolve_data(self) -> ResolveDataUseCase:
        return ResolveDataUseCase(
            self.database,
            self.project_access_resolver,
            self.story_context_run_reader,
            self.story_context_reader,
            self.secret_value_reader,
            self.record_audit_event,
        )

    @cached_property
    def get_test_file(self) -> GetTestFileUseCase:
        return GetTestFileUseCase(
            self.database,
            self.project_access_resolver,
            self.story_context_run_reader,
            self.run_file_recorder,
            self.object_storage,
        )

    @cached_property
    def story_scope_reader(self) -> PostgresStoryScopeReader:
        return PostgresStoryScopeReader(self.database)

    @cached_property
    def coverage_reader(self) -> PostgresCoverageReader:
        return PostgresCoverageReader(self.database)

    @cached_property
    def activity_reader(self) -> PostgresActivityReader:
        return PostgresActivityReader(self.database)

    @cached_property
    def get_traceability(self) -> GetTraceabilityUseCase:
        return GetTraceabilityUseCase(
            self.database, self.project_access_resolver, self.story_scope_reader, self.coverage_reader
        )

    @cached_property
    def list_story_progress(self) -> ListStoryProgressUseCase:
        return ListStoryProgressUseCase(
            self.database,
            self.project_access_resolver,
            self.story_scope_reader,
            self.coverage_reader,
            self.activity_reader,
        )

    @cached_property
    def list_case_latest_results(self) -> ListCaseLatestResultsUseCase:
        return ListCaseLatestResultsUseCase(
            self.database, self.project_access_resolver, self.story_scope_reader, self.coverage_reader
        )

    @cached_property
    def get_dashboard(self) -> GetDashboardUseCase:
        return GetDashboardUseCase(
            self.database,
            self.project_access_resolver,
            self.story_scope_reader,
            self.coverage_reader,
            self.activity_reader,
        )

    @cached_property
    def get_my_work(self) -> GetMyWorkUseCase:
        return GetMyWorkUseCase(
            self.database,
            self.project_access_resolver,
            self.story_scope_reader,
            self.coverage_reader,
            self.activity_reader,
        )

    @cached_property
    def daily_stats_repository(self) -> PostgresDailyStatsRepository:
        return PostgresDailyStatsRepository(self.database)

    @cached_property
    def daily_stats_calculator(self) -> PostgresDailyStatsCalculator:
        return PostgresDailyStatsCalculator(self.database)

    @cached_property
    def quality_reader(self) -> PostgresQualityReader:
        return PostgresQualityReader(self.database)

    @cached_property
    def token_usage_reader(self) -> PostgresTokenUsageReader:
        return PostgresTokenUsageReader(self.database)

    @cached_property
    def get_insight_trends(self) -> GetTrendsUseCase:
        return GetTrendsUseCase(
            self.database,
            self.project_access_resolver,
            self.daily_stats_repository,
            self.daily_stats_calculator,
            self.story_scope_reader,
        )

    @cached_property
    def get_label_coverage(self) -> GetLabelCoverageUseCase:
        return GetLabelCoverageUseCase(self.database, self.project_access_resolver, self.quality_reader)

    @cached_property
    def list_failing_cases(self) -> ListFailingCasesUseCase:
        return ListFailingCasesUseCase(self.database, self.project_access_resolver, self.quality_reader)

    @cached_property
    def list_flaky_cases(self) -> ListFlakyCasesUseCase:
        return ListFlakyCasesUseCase(self.database, self.project_access_resolver, self.quality_reader)

    @cached_property
    def get_token_usage(self) -> GetTokenUsageUseCase:
        return GetTokenUsageUseCase(self.database, self.project_access_resolver, self.token_usage_reader)

    @cached_property
    def list_sprint_coverage(self) -> ListSprintCoverageUseCase:
        return ListSprintCoverageUseCase(
            self.database, self.project_access_resolver, self.story_scope_reader, self.coverage_reader
        )

    @cached_property
    def snapshot_daily_stats(self) -> SnapshotDailyStatsUseCase:
        return SnapshotDailyStatsUseCase(
            self.database, self.daily_stats_calculator, self.daily_stats_repository, self.live_event_publisher
        )

    @cached_property
    def report_document_loader(self) -> ReportDocumentLoader:
        return ReportDocumentLoader(self.get_run, self.get_plan, self.get_traceability, self.list_runs)

    @cached_property
    def report_requester_reader(self) -> PostgresReportRequesterReader:
        return PostgresReportRequesterReader(self.database)

    @cached_property
    def report_file_writer(self) -> ReportFileWriter:
        storage = self._settings.storage
        access_key_id = None if storage.s3_access_key_id is None else storage.s3_access_key_id.get_secret_value()
        secret_access_key = (
            None if storage.s3_secret_access_key is None else storage.s3_secret_access_key.get_secret_value()
        )
        client = build_s3_client(storage.s3_endpoint_url, storage.s3_region, access_key_id, secret_access_key)
        return S3ReportFileWriter(client, storage.s3_bucket)

    @cached_property
    def pdf_renderer(self) -> PdfRenderer:
        return WeasyPrintPdfRenderer()

    @cached_property
    def request_report_export(self) -> RequestReportExportUseCase:
        return RequestReportExportUseCase(
            self.database,
            self.project_access_resolver,
            self.report_document_loader,
            self.stored_file_repository,
            self.job_queue,
        )

    @cached_property
    def export_report(self) -> ExportReportUseCase:
        return ExportReportUseCase(
            self.database,
            self.stored_file_repository,
            self.report_requester_reader,
            self.report_document_loader,
            self.secret_value_reader,
            self.pdf_renderer,
            self.report_file_writer,
            self.send_notification,
            self.live_event_publisher,
        )

    @cached_property
    def webhook_repository(self) -> PostgresWebhookRepository:
        return PostgresWebhookRepository(self.database)

    @cached_property
    def webhook_delivery_repository(self) -> PostgresWebhookDeliveryRepository:
        return PostgresWebhookDeliveryRepository(self.database)

    @cached_property
    def webhook_sender(self) -> WebhookSender:
        return HttpxWebhookSender(self.http_client)

    @cached_property
    def webhook_delivery_requester(self) -> QueuedWebhookDeliveryRequester:
        return QueuedWebhookDeliveryRequester(self.job_queue)

    @cached_property
    def list_webhooks(self) -> ListWebhooksUseCase:
        return ListWebhooksUseCase(
            self.database,
            self.project_access_resolver,
            self.webhook_repository,
            self.webhook_delivery_repository,
            self.secret_cipher,
        )

    @cached_property
    def create_webhook(self) -> CreateWebhookUseCase:
        return CreateWebhookUseCase(
            self.database,
            self.project_access_resolver,
            self.webhook_repository,
            self.secret_cipher,
            self.live_event_publisher,
        )

    @cached_property
    def update_webhook(self) -> UpdateWebhookUseCase:
        return UpdateWebhookUseCase(
            self.database,
            self.project_access_resolver,
            self.webhook_repository,
            self.webhook_delivery_repository,
            self.secret_cipher,
            self.live_event_publisher,
        )

    @cached_property
    def delete_webhook(self) -> DeleteWebhookUseCase:
        return DeleteWebhookUseCase(
            self.database, self.project_access_resolver, self.webhook_repository, self.live_event_publisher
        )

    @cached_property
    def list_webhook_deliveries(self) -> ListWebhookDeliveriesUseCase:
        return ListWebhookDeliveriesUseCase(
            self.database, self.project_access_resolver, self.webhook_repository, self.webhook_delivery_repository
        )

    @cached_property
    def redeliver_webhook(self) -> RedeliverWebhookUseCase:
        return RedeliverWebhookUseCase(
            self.database,
            self.project_access_resolver,
            self.webhook_repository,
            self.webhook_delivery_repository,
            self.webhook_delivery_requester,
            self.live_event_publisher,
        )

    @cached_property
    def request_webhook_deliveries(self) -> RequestWebhookDeliveriesUseCase:
        return RequestWebhookDeliveriesUseCase(
            self.database,
            self.project_repository,
            self.webhook_repository,
            self.webhook_delivery_repository,
            self.webhook_delivery_requester,
            self.live_event_publisher,
        )

    @cached_property
    def deliver_webhook(self) -> DeliverWebhookUseCase:
        return DeliverWebhookUseCase(
            self.database,
            self.webhook_repository,
            self.webhook_delivery_repository,
            self.webhook_sender,
            self.secret_cipher,
            self.live_event_publisher,
        )

    @cached_property
    def delete_old_webhook_deliveries(self) -> DeleteOldWebhookDeliveriesUseCase:
        return DeleteOldWebhookDeliveriesUseCase(self.database, self.webhook_delivery_repository)

    @cached_property
    def stream_live_events(self) -> StreamLiveEventsUseCase:
        return StreamLiveEventsUseCase(
            self.database, self.live_event_hub, self.project_access_resolver, PROJECT_ACCESS_REFRESH_INTERVAL
        )

    @cached_property
    def check_readiness(self) -> CheckReadinessUseCase:
        return CheckReadinessUseCase(
            {
                "postgres": PostgresReadinessProbe(self.database),
                "redis": RedisReadinessProbe(self._settings.queue.redis_url),
            }
        )

    @cached_property
    def job_handlers(self) -> Mapping[QueueName, Mapping[JobName, JobHandler]]:
        return {
            QueueName.EMAIL: {
                JobName.SEND_EMAIL: SendEmailJobHandler(self.smtp_mailer),
                JobName.NOTIFICATION_EMAIL: SendNotificationEmailJobHandler(self.send_notification_email),
            },
            QueueName.INTEGRATIONS: {
                JobName.CHAT_DELIVER: DeliverChatMessageJobHandler(self.deliver_chat_message),
                JobName.WEBHOOK_DELIVER: DeliverWebhookJobHandler(self.deliver_webhook),
            },
            QueueName.JIRA: {
                JobName.JIRA_SYNC_PROJECT: SyncJiraProjectJobHandler(self.sync_jira_project),
                JobName.JIRA_CREATE_ISSUE: CreateJiraIssueJobHandler(self.create_jira_issue),
                JobName.JIRA_POST_COMMENT: PostJiraResultCommentJobHandler(self.post_jira_result_comment),
            },
            QueueName.MAINTENANCE: {
                JobName.FILES_DELETE_ORPHANS: DeleteOrphanFilesJobHandler(self.delete_orphan_files),
                JobName.SESSIONS_DELETE_EXPIRED: DeleteExpiredSessionsJobHandler(self.delete_expired_sessions),
                JobName.RUNS_ABORT_STALE: AbortStaleRunsJobHandler(self.abort_stale_runs),
                JobName.TEST_CASES_RECOMPUTE_FLAKY: RecomputeFlakyJobHandler(self.recompute_flaky),
                JobName.TEST_CASES_SWEEP_FLAKY: SweepFlakyJobHandler(self.sweep_flaky),
                JobName.WEBHOOK_DELETE_OLD_DELIVERIES: DeleteOldWebhookDeliveriesJobHandler(
                    self.delete_old_webhook_deliveries
                ),
                JobName.INSIGHTS_DAILY_SNAPSHOT: DailySnapshotJobHandler(self.snapshot_daily_stats),
            },
            QueueName.REPORTS: {JobName.REPORT_EXPORT: ExportReportJobHandler(self.export_report)},
        }

    @cached_property
    def job_schedules(self) -> tuple[JobSchedule, ...]:
        return (
            JobSchedule(
                scheduler_id=SNAPSHOT_SCHEDULER_ID,
                queue_name=QueueName.MAINTENANCE,
                job_name=JobName.INSIGHTS_DAILY_SNAPSHOT,
                cron_pattern=SNAPSHOT_CRON_PATTERN,
            ),
            JobSchedule(
                scheduler_id="files.delete_orphans",
                queue_name=QueueName.MAINTENANCE,
                job_name=JobName.FILES_DELETE_ORPHANS,
                cron_pattern="0 3 * * *",
            ),
            JobSchedule(
                scheduler_id="sessions.delete_expired",
                queue_name=QueueName.MAINTENANCE,
                job_name=JobName.SESSIONS_DELETE_EXPIRED,
                cron_pattern="30 3 * * *",
            ),
            JobSchedule(
                scheduler_id="runs.abort_stale",
                queue_name=QueueName.MAINTENANCE,
                job_name=JobName.RUNS_ABORT_STALE,
                cron_pattern="*/15 * * * *",
            ),
            JobSchedule(
                scheduler_id="test_cases.sweep_flaky",
                queue_name=QueueName.MAINTENANCE,
                job_name=JobName.TEST_CASES_SWEEP_FLAKY,
                cron_pattern="45 3 * * *",
            ),
            JobSchedule(
                scheduler_id="webhook.delete_old_deliveries",
                queue_name=QueueName.MAINTENANCE,
                job_name=JobName.WEBHOOK_DELETE_OLD_DELIVERIES,
                cron_pattern="15 4 * * *",
            ),
        )

    @cached_property
    def test_case_quality_repository(self) -> PostgresTestCaseQualityRepository:
        return PostgresTestCaseQualityRepository(self.database)

    @cached_property
    def quarantine_event_repository(self) -> PostgresQuarantineEventRepository:
        return PostgresQuarantineEventRepository(self.database)

    @cached_property
    def case_result_history_reader(self) -> PostgresCaseResultHistoryReader:
        return PostgresCaseResultHistoryReader(self.database)

    @cached_property
    def flaky_recompute_requester(self) -> FlakyRecomputeRequester:
        return QueuedFlakyRecomputeRequester(self.job_queue)

    @cached_property
    def recompute_flaky(self) -> RecomputeFlakyUseCase:
        return RecomputeFlakyUseCase(
            self.database,
            self.test_case_quality_repository,
            self.case_result_history_reader,
            self.quarantine_event_repository,
            self.live_event_publisher,
        )

    @cached_property
    def sweep_flaky(self) -> SweepFlakyUseCase:
        return SweepFlakyUseCase(self.database, self.test_case_quality_repository, self.recompute_flaky)

    @cached_property
    def quarantine_test_case(self) -> QuarantineTestCaseUseCase:
        return QuarantineTestCaseUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_quality_repository,
            self.quarantine_event_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
            self.live_event_publisher,
        )

    @cached_property
    def release_test_case_quarantine(self) -> ReleaseTestCaseQuarantineUseCase:
        return ReleaseTestCaseQuarantineUseCase(
            self.database,
            self.project_access_resolver,
            self.test_case_repository,
            self.test_case_quality_repository,
            self.quarantine_event_repository,
            self.test_case_version_repository,
            self.test_file_repository,
            self.case_story_reader,
            self.case_criterion_reader,
            self.data_key_reader,
            self.test_case_label_repository,
            self.live_event_publisher,
        )

    @cached_property
    def list_quarantine_events(self) -> ListQuarantineEventsUseCase:
        return ListQuarantineEventsUseCase(
            self.database, self.project_access_resolver, self.test_case_repository, self.quarantine_event_repository
        )

    @cached_property
    def job_workers(self) -> list[BullmqJobWorker]:
        return build_job_workers(self._settings.queue.redis_url, self.job_handlers)

    @cached_property
    def live_event_handlers(self) -> tuple[LiveEventHandler, ...]:
        return (ChatChannelLiveEventHandler(self.request_chat_deliveries), self.request_webhook_deliveries)

    @cached_property
    def live_event_listener(self) -> LiveEventListener:
        return LiveEventListener(self.live_event_hub, self.live_event_handlers)

    @cached_property
    def run_log_repository(self) -> PostgresRunLogRepository:
        return PostgresRunLogRepository(self.database)

    @cached_property
    def upload_run_log(self) -> UploadRunLogUseCase:
        return UploadRunLogUseCase(
            self.database,
            self.run_repository,
            self.run_case_repository,
            self.run_log_repository,
            self.secret_value_reader,
            self.live_event_publisher,
        )

    @cached_property
    def get_run_log(self) -> GetRunLogUseCase:
        return GetRunLogUseCase(
            self.database, self.project_access_resolver, self.run_repository, self.run_log_repository
        )

    @cached_property
    def mcp_server(self) -> MCPServer:
        server = MCPServer("tessio")
        register_run_tools(
            server,
            self.authenticate_api_token,
            self.start_run,
            self.record_case_result,
            self.finish_run,
            self.get_failed_cases,
        )
        register_gap_tools(
            server,
            self.authenticate_api_token,
            self.raise_gaps,
            self.get_open_gaps,
            self.get_my_gaps,
            self.answer_gap,
            self.reassign_gap,
        )
        register_test_data_tools(server, self.authenticate_api_token, self.set_test_data)
        register_test_case_tools(server, self.authenticate_api_token, self.check_draft_cases, self.create_draft_cases)
        register_story_context_tools(
            server, self.authenticate_api_token, self.get_story_context, self.resolve_data, self.get_test_file
        )
        register_suite_tools(server, self.authenticate_api_token, self.get_suite_context)
        return server

    async def close(self) -> None:
        await self.http_client.aclose()
        await self.job_queue.close()
        await self.live_event_hub.close()
        await self.live_event_publisher.close()
        await self.rate_limiter.close()
        await self.database.close()
