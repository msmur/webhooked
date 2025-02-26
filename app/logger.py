import logging
import json

from app.config import IS_DEVELOPMENT


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_message = {
            "name": record.name,
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_message)


class PrettyJsonFormatter(JsonFormatter):
    def format(self, record):
        log_message = json.loads(super().format(record))  # Get the JSON and parse it
        return json.dumps(log_message, indent=4)  # Pretty print with indentation


logger = logging.getLogger("webhooked")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = PrettyJsonFormatter() if IS_DEVELOPMENT else JsonFormatter()
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
