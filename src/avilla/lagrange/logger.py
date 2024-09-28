# We won't use install_loguru() for it can break default performance.
import inspect
import logging

from lagrange.utils.log import log, _Logger  # noqa
from loguru import logger


class LagrangeLoguruHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _config(level: str | int):
    logging.basicConfig(
        handlers=[LagrangeLoguruHandler()],
        level=level
    )
    logger.configure(extra={'lagrange_log_level': level})


log.set_level = _config
log.set_level(logging.INFO)

_Logger.get_logger = lambda self: logger.patch(lambda r: r.update(name=self.context))  # pyright: ignore
