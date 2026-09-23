try:
    from .logger import get_secure_logger
except ImportError:
    from securelogger.logger import get_secure_logger
