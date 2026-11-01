from collections.abc import Mapping
from functools import cached_property

import httpx
from mcp.server.mcpserver import MCPServer

from app.config import Settings
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
from app.modules.auth.ports.breached_password_checker import BreachedPasswordChecker
from app.modules.failures import (
    ApplyCaseResultUseCase,
    AssignFailureUseCase,
    ChangeFailureStatusUseCase,
    CountActiveFailuresUseCase,
    GetFailureUseCase,
    ListFailuresUseCase,
)
from app.modules.failures.infrastructure import (
    PostgresCaseResultReader,
    PostgresFailureAssigneeDirectory,
    PostgresFailureEventRepository,
    PostgresFailureRepository,
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
    GetDashboardUseCase,
    GetMyWorkUseCase,
    GetTraceabilityUseCase,
    LatestResultCriterionImpactCalculator,
    ListCaseLatestResultsUseCase,
    ListStoryProgressUseCase,
)
from app.modules.insights.infrastructure import PostgresActivityReader, PostgresCoverageReader, PostgresStoryScopeReader
from app.modules.jira import (
    GetJiraConnectionUseCase,
    JiraClient,
    ListJiraBoardsUseCase,
    ListJiraProjectsUseCase,
    LoadJiraCredentialsUseCase,
    SaveJiraConnectionUseCase,
)
from app.modules.jira.infrastructure import (
    HttpxJiraClient,
    PostgresJiraConnectionChecker,
    PostgresJiraConnectionRepository,
    PostgresLinkedProjectReader,
)
from app.modules.live_events import StreamLiveEventsUseCase
from app.modules.live_events.typing.constants.live_events import PROJECT_ACCESS_REFRESH_INTERVAL
from app.modules.notifications import (
    CountUnreadNotificationsUseCase,
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
    SendNotificationUseCase,
)
from app.modules.notifications.infrastructure import PostgresNotificationRepository, PostgresRecipientDirectory
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
from app.modules.runs import (
    AbortStaleRunsJobHandler,
    AbortStaleRunsUseCase,
    CaseResultRecordedHandler,
    CreateManualRunUseCase,
    CreateScreenshotUploadUseCase,
    CriterionImpactCalculator,
    FinishManualRunUseCase,
    FinishRunUseCase,
    GetFailedCasesUseCase,
    GetRunUseCase,
    ListRunsUseCase,
    RecordCaseResultUseCase,
    RecordManualCaseResultUseCase,
    RerunFailedCasesUseCase,
    RunStartGate,
    ScreenshotVerifier,
    StartRunUseCase,
    register_run_tools,
)
from app.modules.runs.infrastructure import (
    PostgresCaseResultRepository,
    PostgresEnvironmentUsageChecker,
    PostgresRunCaseRepository,
    PostgresRunFileRepository,
    PostgresRunningRunChecker,
    PostgresRunRepository,
    PostgresRunStoryReader,
    PostgresRunTargetReader,
    PostgresRunViewReader,
)
from app.modules.stories import (
    ActiveFailureCounter,
    ChangeTestStatusUseCase,
    CriteriaChangedHandler,
    GetSprintUseCase,
    GetStoryUseCase,
    GetSyncStatusUseCase,
    ListSprintsUseCase,
    ListStoriesUseCase,
    MarkStoryInTestUseCase,
    RequestJiraSyncUseCase,
    RunningRunChecker,
    SyncJiraProjectJobHandler,
    SyncJiraProjectUseCase,
)
from app.modules.stories.infrastructure import (
    PostgresAcceptanceCriterionRepository,
    PostgresProjectSyncStateRepository,
    PostgresSprintRepository,
    PostgresStoryRepository,
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
from app.modules.test_cases import (
    AttachTestFileUseCase,
    ChangeTestCaseStatusUseCase,
    CommitTestCaseImportUseCase,
    CreateTestCaseUseCase,
    FlagCasesForReviewUseCase,
    GetTestCaseUseCase,
    ListTestCasesUseCase,
    ListTestCaseVersionsUseCase,
    ListTestFileVersionsUseCase,
    MarkTestCaseReviewedUseCase,
    PreviewTestCaseImportUseCase,
    UpdateTestCaseUseCase,
)
from app.modules.test_cases.infrastructure import (
    PostgresCriterionReader,
    PostgresDataKeyReader,
    PostgresStoryReader,
    PostgresTestCaseCounterRepository,
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
    UnarchiveEnvironmentUseCase,
    UpdateDataItemUseCase,
    UpdateEnvironmentUseCase,
)
from app.modules.test_data.infrastructure import (
    PostgresDataItemRepository,
    PostgresEnvironmentChecker,
    PostgresEnvironmentRepository,
    StorageImportFileReader,
)
from app.modules.users.infrastructure import PostgresUserRepository
from app.shared.crypto import AesGcmSecretCipher, parse_key_ring
from app.shared.events import LiveEventHub, LiveEventPublisher, RedisLiveEventHub, RedisLiveEventPublisher
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
            self.database, self.api_token_repository, self.user_repository, self.project_access_resolver
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
            self.database, self.jira_connection_repository, self.jira_client, self.secret_cipher
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
            self.secret_cipher,
        )

    @cached_property
    def update_data_item(self) -> UpdateDataItemUseCase:
        return UpdateDataItemUseCase(
            self.database, self.project_access_resolver, self.data_item_repository, self.secret_cipher
        )

    @cached_property
    def delete_data_item(self) -> DeleteDataItemUseCase:
        return DeleteDataItemUseCase(self.database, self.project_access_resolver, self.data_item_repository)

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
            self.job_queue,
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
    def list_test_cases(self) -> ListTestCasesUseCase:
        return ListTestCasesUseCase(self.database, self.project_access_resolver, self.test_case_repository)

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
            self.test_case_counter_repository,
            self.live_event_publisher,
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
            self.live_event_publisher,
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
            self.live_event_publisher,
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
            self.database, self.notification_repository, self.recipient_directory, self.live_event_publisher
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
            self.run_target_reader,
            self.screenshot_verifier,
            self.criterion_impact_calculator,
            self.secret_value_reader,
            self.send_notification,
            self.live_event_publisher,
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
    def story_context_reader(self) -> PostgresStoryContextReader:
        return PostgresStoryContextReader(self.database)

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
            QueueName.EMAIL: {JobName.SEND_EMAIL: SendEmailJobHandler(self.smtp_mailer)},
            QueueName.JIRA: {JobName.JIRA_SYNC_PROJECT: SyncJiraProjectJobHandler(self.sync_jira_project)},
            QueueName.MAINTENANCE: {
                JobName.FILES_DELETE_ORPHANS: DeleteOrphanFilesJobHandler(self.delete_orphan_files),
                JobName.SESSIONS_DELETE_EXPIRED: DeleteExpiredSessionsJobHandler(self.delete_expired_sessions),
                JobName.RUNS_ABORT_STALE: AbortStaleRunsJobHandler(self.abort_stale_runs),
            },
        }

    @cached_property
    def job_schedules(self) -> tuple[JobSchedule, ...]:
        return (
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
        )

    @cached_property
    def job_workers(self) -> list[BullmqJobWorker]:
        return build_job_workers(self._settings.queue.redis_url, self.job_handlers)

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
        register_gap_tools(server, self.authenticate_api_token, self.raise_gaps, self.get_open_gaps)
        register_story_context_tools(
            server, self.authenticate_api_token, self.get_story_context, self.resolve_data, self.get_test_file
        )
        return server

    async def close(self) -> None:
        await self.http_client.aclose()
        await self.job_queue.close()
        await self.live_event_hub.close()
        await self.live_event_publisher.close()
        await self.rate_limiter.close()
        await self.database.close()
