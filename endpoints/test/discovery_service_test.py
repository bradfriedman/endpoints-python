# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for discovery_service."""

import os
import unittest

import endpoints.api_config as api_config
import endpoints.api_config_manager as api_config_manager
import endpoints.apiserving as apiserving
import endpoints.discovery_service as discovery_service

from protorpc import message_types
from protorpc import remote


@api_config.api('aservice', 'v3', hostname='aservice.appspot.com',
                description='A Service API')
class AService(remote.Service):

  @api_config.method(path='noop')
  def Noop(self, unused_request):
    return message_types.VoidMessage()


class DiscoveryServiceTest(unittest.TestCase):

  class FakeRequest(object):

    def __init__(self, server=None, port=None, url_scheme=None, api=None,
                 version=None):
      self.server = server
      self.port = port
      self.url_scheme = url_scheme
      self.body_json = {'api': api, 'version': version}

  def setUp(self):
    """Make ApiConfigManager with a few helpful fakes."""
    self.backend = self._create_wsgi_application()
    self.config_manager = api_config_manager.ApiConfigManager()
    self.discovery = discovery_service.DiscoveryService(
        self.config_manager, self.backend)

  def _create_wsgi_application(self):
    return apiserving._ApiServer([AService], registry_path='/my_registry')

  def _check_api_config(self, expected_base_url, server, port, url_scheme, api,
                        version, local=True):
    request = DiscoveryServiceTest.FakeRequest(
        server=server, port=port, url_scheme=url_scheme, api=api,
        version=version)
    config_dict = self._generate_api_config(request, local=local)

    # Check bns entry
    adapter = config_dict.get('adapter')
    self.assertIsNotNone(adapter)
    self.assertEqual(expected_base_url, adapter.get('bns'))

    # Check root
    self.assertEqual(expected_base_url, config_dict.get('root'))

  def _generate_api_config(self, request, local=True):
    return self.discovery._generate_api_config_with_root(request, local=local)


class ProdDiscoveryServiceTest(DiscoveryServiceTest):

  def testGenerateApiConfigWithRoot(self):
    server = 'test.appspot.com'
    port = '12345'
    url_scheme = 'https'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}:{2}/_ah/api'.format(url_scheme, server, port)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigWithRootLocalhost(self):
    server = 'localhost'
    port = '12345'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}:{2}/_ah/api'.format(url_scheme, server, port)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigLocalhostDefaultHttpPort(self):
    server = 'localhost'
    port = '80'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigWithRootDefaultHttpsPort(self):
    server = 'test.appspot.com'
    port = '443'
    url_scheme = 'https'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)


ENV_VARIABLE_KEY = 'SERVER_SOFTWARE'
class DevServerDiscoveryServiceTest(DiscoveryServiceTest):

  def setUp(self):
    super(DevServerDiscoveryServiceTest, self).setUp()
    self.original_env_value = os.environ.get(ENV_VARIABLE_KEY)
    self._set_env_value_for_remote_env()

  def tearDown(self):
    self._restore_env_value()

  def _set_env_value_for_remote_env(self):
    os.environ[ENV_VARIABLE_KEY] = 'Development/2.0.0'

  def _restore_env_value(self):
    if self.original_env_value is None:
      del os.environ[ENV_VARIABLE_KEY]
    else:
      os.environ[ENV_VARIABLE_KEY] = self.original_env_value

  def testGenerateApiConfigWithRootDefaultHttpPortRemoteGeneration(self):
    server = 'test.appspot.com'
    port = '80'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version, local=False)

  def testGenerateApiConfigWithRootDefaultHttpPort(self):
    server = 'test.appspot.com'
    port = '443'
    url_scheme = 'https'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}/_ah/api'.format(url_scheme, server)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version)

  def testGenerateApiConfigWithRootRemoteGeneration(self):
    server = 'test.appspot.com'
    port = '12345'
    url_scheme = 'http'
    api = 'aservice'
    version = 'v3'
    expected_base_url = '{0}://{1}:{2}/_ah/api'.format(url_scheme, server, port)

    self._check_api_config(expected_base_url, server, port, url_scheme, api,
                           version, local=False)

if __name__ == '__main__':
  unittest.main()
