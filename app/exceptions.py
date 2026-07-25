class ApplicationError(Exception):
    default_message = "Application error"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(ApplicationError):
    pass


class AuthenticationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class RequestValidationError(ApplicationError):
    pass


class UnsupportedMediaTypeError(ApplicationError):
    pass


class PayloadTooLargeError(ApplicationError):
    pass


class InfrastructureError(ApplicationError):
    pass


class ProjectNotFoundError(NotFoundError):
    default_message = "Project not found"


class TaskNotFoundError(NotFoundError):
    default_message = "Task not found in this project"


class UserNotFoundError(NotFoundError):
    default_message = "User not found"


class ProjectMemberNotFoundError(NotFoundError):
    default_message = "Project member not found"


class TaskImageNotFoundError(NotFoundError):
    default_message = "Task image not found"


class InvalidCredentialsError(AuthenticationError):
    default_message = "Invalid username or password"


class TokenValidationError(AuthenticationError):
    default_message = "Could not validate credentials"


class ProjectOwnerRequiredError(AuthorizationError):
    default_message = "Only the project owner can perform this action"


class ProjectMembershipRequiredError(AuthorizationError):
    default_message = "Only project members can access this resource"


class TaskImageDeleteForbiddenError(AuthorizationError):
    default_message = "You cannot delete this image"


class UsernameAlreadyExistsError(ConflictError):
    default_message = "This user already exists"


class ProjectMemberAlreadyExistsError(ConflictError):
    default_message = "User is already a project member"


class ProjectOwnerRemovalError(RequestValidationError):
    default_message = "The project owner cannot be removed"


class EmptyImageError(RequestValidationError):
    default_message = "Image is empty"


class UnsupportedImageTypeError(UnsupportedMediaTypeError):
    default_message = "Only JPEG, PNG, and WebP images are allowed"


class ImageTooLargeError(PayloadTooLargeError):
    default_message = "Image cannot exceed 5 MB"


class RepositoryError(InfrastructureError):
    resource_name = "resource"

    def __init__(self, operation: str):
        super().__init__(f"Could not {operation} {self.resource_name}")


class UserRepositoryError(RepositoryError):
    resource_name = "user data"


class ProjectRepositoryError(RepositoryError):
    resource_name = "project data"


class ProjectMemberRepositoryError(RepositoryError):
    resource_name = "project membership data"


class TaskRepositoryError(RepositoryError):
    resource_name = "task data"


class TaskImageRepositoryError(RepositoryError):
    resource_name = "task image data"


class TaskCommentNotFoundError(NotFoundError):
    default_message = "Task comment not found"


class NotificationNotFoundError(NotFoundError):
    default_message = "Notification not found"


class TaskCommentDeleteForbiddenError(AuthorizationError):
    default_message = "You cannot delete this comment"


class TaskCommentRepositoryError(RepositoryError):
    resource_name = "task comment data"


class NotificationRepositoryError(RepositoryError):
    resource_name = "notification data"
