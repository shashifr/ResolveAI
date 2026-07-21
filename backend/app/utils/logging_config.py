import logging
import json
from contextvars import ContextVar

# Thread-safe context variable to store correlation IDs
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        
        # Inject correlation ID if available in context
        c_id = correlation_id_ctx.get()
        if c_id:
            log_record["correlation_id"] = c_id
            
        # Capture stack traces if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_structured_logging():
    # Console Stream Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(JSONFormatter())
    
    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [stream_handler]
    
    # Redirect and intercept Uvicorn and FastAPI loggers
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = [stream_handler]
        logger.propagate = False
