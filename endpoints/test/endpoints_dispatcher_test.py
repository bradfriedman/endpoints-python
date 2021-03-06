# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Tests for endpoints.endpoints_dispatcher."""

import unittest

from protorpc import remote

import endpoints.api_config as api_config
import endpoints.apiserving as apiserving
import endpoints.endpoints_dispatcher as endpoints_dispatcher


@api_config.api('aservice', 'v1', hostname='aservice.appspot.com',
                description='A Service API')
class AService(remote.Service):

  @api_config.method(path='noop')
  def Noop(self, unused_request):
    return message_types.VoidMessage()


class EndpointsDispatcherBaseTest(unittest.TestCase):

  def setUp(self):
    self.dispatcher = endpoints_dispatcher.EndpointsDispatcherMiddleware(
      apiserving._ApiServer([AService]))


class EndpointsDispatcherGetExplorerUrlTest(EndpointsDispatcherBaseTest):

  def _check_explorer_url(self, server, port, base_url, expected):
    actual = self.dispatcher._get_explorer_redirect_url(
        server, port, base_url)
    self.assertEqual(actual, expected)

  def testGetExplorerUrl(self):
    self._check_explorer_url(
      'localhost', 8080, '_ah/api',
      'https://apis-explorer.appspot.com/apis-explorer/'
      '?base=http://localhost:8080/_ah/api')

  def testGetExplorerUrlExplicitHttpPort(self):
    self._check_explorer_url(
      'localhost', 80, '_ah/api',
      'https://apis-explorer.appspot.com/apis-explorer/'
      '?base=http://localhost/_ah/api')

  def testGetExplorerUrlExplicitHttpsPort(self):
    self._check_explorer_url(
          'testapp.appspot.com', 443, '_ah/api',
          'https://apis-explorer.appspot.com/apis-explorer/'
          '?base=https://testapp.appspot.com/_ah/api')
