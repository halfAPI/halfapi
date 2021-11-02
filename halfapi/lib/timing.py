"""
Timing module

Helpers to gathers stats on requests timing

class HTimingClient
"""
import logging

from timing_asgi import TimingClient

from ..logging import logger

class HTimingClient(TimingClient):
    """ Used to redefine TimingClient.timing
    """
    def timing(self, metric_name, timing, tags):
        tags_d = dict(map(lambda elt: elt.split(':'), tags))

        logger.debug('[TIME:%s][%s] %s %s - %sms',
            tags_d['time'], metric_name,
            tags_d['http_method'], tags_d['http_status'],
            round(timing*1000, 2))
