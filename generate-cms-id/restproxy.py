# Copyright 2015 Alcatel-Lucent USA Inc.
# All Rights Reserved.

import base64
import httplib
import json
import socket
import time
import logging
import ssl

LOG = logging.getLogger(__name__)
MAX_RETRIES = 5
MAX_RETRIES_503 = 5


class RESTProxyBaseException(Exception):
    message = "An unknown exception occurred."

    def __init__(self, **kwargs):
        try:
            super(RESTProxyBaseException, self).__init__(self.message % kwargs)
            self.msg = self.message % kwargs
        except Exception:
            if self.use_fatal_exceptions():
                raise
            else:
                super(RESTProxyBaseException, self).__init__(self.message)

    def __unicode__(self):
        return unicode(self.msg)

    def use_fatal_exceptions(self):
        return False


class RESTProxyError(RESTProxyBaseException):
    def __init__(self, message, error_code=None):
        self.code = 0
        if error_code:
            self.code = error_code

        if message is None:
            message = "None"

        if self.code == 409:
            self.message = message
        else:
            self.message = "Error in REST call to VSD: %s" % message
        super(RESTProxyError, self).__init__()


class RESTProxyServer(object):
    def __init__(self, server, base_uri, serverssl,
                 serverauth, auth_resource,
                 organization, servertimeout=30):
        try:
            server_ip, port = server.split(":")
        except ValueError:
            server_ip = server
            port = None
        self.server = server_ip
        self.port = int(port) if port else None
        self.base_uri = base_uri
        self.serverssl = serverssl
        self.serverauth = serverauth
        self.auth_resource = auth_resource
        self.organization = organization
        self.timeout = servertimeout
        self.retry = 0
        self.retry_503 = 0
        self.auth = None
        self.success_codes = range(200, 207)

    def _rest_call(self, action, resource, data, extra_headers=None):
        if self.retry >= MAX_RETRIES:
            LOG.error('RESTProxy: Max retries exceeded')
            # Get ready for the next set of operation
            self.retry = 0
            return 0, None, None, None
        uri = self.base_uri + resource
        body = json.dumps(data)
        headers = {}
        headers['Content-type'] = 'application/json'
        headers['X-Nuage-Organization'] = self.organization
        if self.auth:
            headers['Authorization'] = self.auth
        conn = None
        if extra_headers:
            headers.update(extra_headers)

        LOG.debug('Request uri: %s', uri)
        LOG.debug('Request headers: %s', headers)
        LOG.debug('Request body: %s', body)

        if self.serverssl:
            conn = httplib.HTTPSConnection(
                self.server, self.port, timeout=self.timeout, context=ssl._create_unverified_context())
            if conn is None:
                LOG.error('RESTProxy: Could not establish HTTPS '
                          'connection')
                return 0, None, None, None
        else:
            conn = httplib.HTTPConnection(
                self.server, self.port, timeout=self.timeout)
            if conn is None:
                LOG.error('RESTProxy: Could not establish HTTP '
                          'connection')
                return 0, None, None, None

        try:
            conn.request(action, uri, body, headers)
            response = conn.getresponse()
            respstr = response.read()
            respdata = respstr
            LOG.debug('Response status is %(st)s and reason is %(res)s',
                      {'st': response.status,
                       'res': response.reason})
            LOG.debug('Response data is %s', respstr)
            if response.status in self.success_codes:
                try:
                    respdata = json.loads(respstr)
                except ValueError:
                    # response was not JSON, ignore the exception
                    pass
            ret = (response.status, response.reason, respstr, respdata)
        except (socket.timeout, socket.error) as e:
            LOG.error('ServerProxy: %(action)s failure, %(e)r', locals())
            # retry
            self.retry += 1
            return self._rest_call(action, resource, data, extra_headers)
        conn.close()
        if response.status == 503:
            if self.retry_503 < MAX_RETRIES_503:
                time.sleep(1)
                self.retry_503 += 1
                LOG.debug('VSD unavailable. Retrying')
                return self._rest_call(action, resource, data,
                                       extra_headers=extra_headers)
            else:
                LOG.debug('After 5 retries VSD is unavailable. Bailing out')
        self.retry = 0
        self.retry_503 = 0
        return ret

    def generate_nuage_auth(self):
        data = ''
        encoded_auth = base64.encodestring(self.serverauth).strip()
        self.auth = 'Basic ' + encoded_auth
        resp = self._rest_call('GET', self.auth_resource, data)
        if resp[0] in self.success_codes and resp[3][0]['APIKey']:
            respkey = resp[3][0]['APIKey']
        else:
            if resp[0] == 0:
                assert 0, 'Could not establish conn with REST server. Abort'
            else:
                assert 0, 'Could not authenticate to REST server. Abort'
        uname = self.serverauth.split(':')[0]
        new_uname_pass = uname + ':' + respkey
        auth = 'Basic ' + base64.encodestring(new_uname_pass).strip()
        self.auth = auth

    def rest_call(self, action, resource, data, extra_headers=None):
        response = self._rest_call(action, resource, data,
                                   extra_headers=extra_headers)
        '''
        If at all authentication expires with VSD, re-authenticate.
        '''
        if response[0] == 401 and response[1] == 'Unauthorized':
            self.generate_nuage_auth()
            return self._rest_call(action, resource, data,
                                   extra_headers=extra_headers)
        return response
