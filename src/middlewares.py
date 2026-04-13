# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；本文件若含中文，均为补充释义而非替换原文。
import logging

logger = logging.getLogger(__name__)


# What's missing and why:
# - These functions are not integrated into FastAPI middleware system
# - No automatic request/response logging or timing
# - No error handling or request tracing
# - Functions exist for future use when middleware integration is needed
#
# In production, these would be used via FastAPI middleware decorators
# or integrated into a proper BaseHTTPMiddleware class for automatic
# request logging, performance monitoring, and error tracking.


def log_request(method: str, path: str) -> None:
    """Simple request logging for Week 1."""
    logger.info(f"{method} {path}")


def log_error(error: str, method: str, path: str) -> None:
    """Simple error logging for Week 1."""
    logger.error(f"Error in {method} {path}: {error}")
