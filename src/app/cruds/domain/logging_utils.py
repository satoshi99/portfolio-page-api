import logging
from logging import LogRecord


class NoPasswordLogFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        message = record.getMessage()
        return "password" not in message
