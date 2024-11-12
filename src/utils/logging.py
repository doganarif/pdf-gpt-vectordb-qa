import logging
import logging.config
import json
from datetime import datetime
from typing import Dict, Any
import os


def setup_logging(
        level: str = "INFO",
        log_file: str = "app.log",
        json_format: bool = True
) -> None:
    """Setup application logging"""

    class JSONFormatter(logging.Formatter):
        """JSON log formatter"""

        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }

            if hasattr(record, 'team_id'):
                log_data["team_id"] = record.team_id

            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)

            return json.dumps(log_data)

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Configure logging
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json" if json_format else "standard",
                "level": level
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"logs/{log_file}",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json" if json_format else "standard",
                "level": level
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": level,
                "propagate": True
            }
        }
    }

    logging.config.dictConfig(config)


def log_with_context(
        logger: logging.Logger,
        level: str,
        message: str,
        team_id: str = None,
        extra: Dict[str, Any] = None
) -> None:
    """Log with additional context"""
    log_data = extra or {}
    if team_id:
        log_data["team_id"] = team_id

    logger.log(
        getattr(logging, level.upper()),
        message,
        extra=log_data
    )


# Initialize logging
setup_logging()