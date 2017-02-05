import logging
from logging.handlers import SysLogHandler

LOG_PREFIX = 'get_reading'


def ptt_logger():
    locallog = logging.getLogger()
    locallog.setLevel(logging.INFO)

    syslog = SysLogHandler(address=('logs2.papertrailapp.com', 55691))
    formatter = logging.Formatter('%(asctime)s weather %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

    syslog.setFormatter(formatter)
    locallog.addHandler(syslog)
    return locallog


logger = ptt_logger()


def log(msg, error=False, debug=False):
    global logger, LOG_PREFIX
    s = '{} - {}'.format(LOG_PREFIX, msg)
    if error:
        logger.error(s)
    elif debug:
        logger.debug(s)
    else:
        logger.info(s)
