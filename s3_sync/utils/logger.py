import logging

logger = logging.getLogger(__name__)


def log_error(success: bool, error: Exception, errors: list):
    if not success:
        errors.append(error)


def has_error(errors: list):
    return len(errors) > 0
