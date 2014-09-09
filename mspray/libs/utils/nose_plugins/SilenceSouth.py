from nose.plugins import Plugin  # noqa

import logging


class SilenceSouth(Plugin):
    south_logging_level = logging.ERROR

    def configure(self, options, conf):
        super(SilenceSouth, self).configure(options, conf)
        logger = logging.getLogger('django.db.backends.schema')
        logger.setLevel(self.south_logging_level)
