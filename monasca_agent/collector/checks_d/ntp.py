# (C) Copyright 2015,2016 Hewlett Packard Enterprise Development LP

import ntplib

from monasca_agent.collector.checks import AgentCheck

DEFAULT_NTP_VERSION = 3
DEFAULT_TIMEOUT = 1  # in seconds
DEFAULT_HOST = "pool.ntp.org"
DEFAULT_PORT = "ntp"


class NtpCheck(AgentCheck):
    """Uses ntplib to grab a metric for the ntp offset
    """

    def check(self, instance):
        dimensions = self._set_dimensions(None, instance)
        req_args = {
            'host': instance.get('host', DEFAULT_HOST),
            'port': instance.get('port', DEFAULT_PORT),
            'version': int(instance.get('version', DEFAULT_NTP_VERSION)),
            'timeout': float(instance.get('timeout', DEFAULT_TIMEOUT)),
        }
        dimensions['ntp_server'] = req_args['host']
        try:
            ntp_stats = ntplib.NTPClient().request(**req_args)
        except ntplib.NTPException as err:
            self.log.error("Could not connect to NTP Server: %s" % err)
            self.gauge('ntp.connection_status', 1, dimensions=dimensions)
        else:
            ntp_offset = ntp_stats.offset

            # Use the ntp server's timestamp for the time of the result in
            # case the agent host's clock is messed up.
            ntp_ts = ntp_stats.recv_time
            self.gauge('ntp.offset', ntp_offset, timestamp=ntp_ts, dimensions=dimensions)
            self.gauge('ntp.connection_status', 0, timestamp=ntp_ts, dimensions=dimensions)
