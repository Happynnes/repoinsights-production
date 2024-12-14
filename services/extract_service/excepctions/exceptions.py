class GitHubUserException(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


class RateLimitExceededError(Exception):
    pass


class NoMoreTokensError(Exception):
    pass


class EmptyQueueError(Exception):
    pass


class ExtractError(Exception):
    pass


class LoadError(Exception):
    pass


class MainProjectError(Exception):
    pass


class ExtractDataResulstsError(Exception):
    pass


class GitHubError(Exception):
    pass


class LimitExceededError(Exception):
    pass


class RateLimitExceededErrorPrivate(Exception):
    pass


class InternalGitHubError(Exception):
    pass


class QueueNotExistError(Exception):
    pass


class TokensFileError(Exception):
    pass
