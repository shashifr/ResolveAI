import logging
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

# Thread-safe context variable to store correlation IDs
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        c_id = correlation_id_ctx.get()
        if c_id:
            log_record["correlation_id"] = c_id

def setup_structured_logging():
    # Console Stream Handler
    stream_handler = logging.StreamHandler()
    
    # Standard JSON Formatter replacing custom dict formatting
    formatter = CustomJsonFormatter(
        "%(asctime)s %(levelname)s %(message)s %(module)s %(lineno)d",
        rename_fields={"asctime": "timestamp", "levelname": "level"}
    )
    stream_handler.setFormatter(formatter)
    
    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [stream_handler]
    
    # Redirect and intercept Uvicorn and FastAPI loggers
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = [stream_handler]
        logger.propagate = False
