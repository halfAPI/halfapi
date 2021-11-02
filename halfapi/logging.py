import logging


def config_logging(level=logging.INFO):

    # When run by 'uvicorn ...', a root handler is already
    # configured and the basicConfig below does nothing.
    # To get the desired formatting:
    logging.getLogger().handlers.clear()

    # 'uvicorn --log-config' is broken so we configure in the app.
    #   https://github.com/encode/uvicorn/issues/511
    logging.basicConfig(
        # match gunicorn format
        format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
        level=level)

        # When run by 'gunicorn -k uvicorn.workers.UvicornWorker ...',
    # These loggers are already configured and propogating.
    # So we have double logging with a root logger.
    # (And setting propagate = False hurts the other usage.)
    logging.getLogger('uvicorn.asgi').handlers.clear()
    logging.getLogger('uvicorn.access').handlers.clear()
    logging.getLogger('uvicorn.error').handlers.clear()
    logging.getLogger('uvicorn.asgi').propagate = True
    logging.getLogger('uvicorn.access').propagate = True
    logging.getLogger('uvicorn.error').propagate = True

config_logging()
logger = logging.getLogger()
