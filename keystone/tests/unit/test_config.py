# Copyright 2013 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import uuid

from oslo_config import generator

import keystone.conf
from keystone import exception
from keystone.server import wsgi
from keystone.tests import unit


CONF = keystone.conf.CONF


class ConfigTestCase(unit.TestCase):

    def config_files(self):
        config_files = super(ConfigTestCase, self).config_files()

        # NOTE(lbragstad): This needs some investigation, but CONF.find_file()
        # apparently needs the sample configuration file in order to find the
        # paste file. This should really be replaced by just setting the
        # default configuration directory on the config object instead.
        sample_file = 'keystone.conf.sample'
        args = ['--namespace', 'keystone', '--output-file',
                unit.dirs.etc(sample_file)]
        generator.main(args=args)
        config_files.insert(0, unit.dirs.etc(sample_file))
        self.addCleanup(os.remove, unit.dirs.etc(sample_file))
        return config_files

    def test_default_paste_config_location_succeeds(self):
        paste_file_location = unit.dirs.etc(CONF.paste_deploy.config_file)
        self.assertEqual(paste_file_location, wsgi.find_paste_config())

    def test_invalid_paste_file_location_fails(self):
        self.config_fixture.config(
            group='paste_deploy', config_file=uuid.uuid4().hex
        )
        self.assertRaises(
            exception.ConfigFileNotFound, wsgi.find_paste_config
        )

    def test_config_default(self):
        self.assertIsNone(CONF.auth.password)
        self.assertIsNone(CONF.auth.token)

    def test_profiler_config_default(self):
        """Check config.set_config_defaults() has set [profiler]enabled."""
        self.assertEqual(False, CONF.profiler.enabled)


class DeprecatedTestCase(unit.TestCase):
    """Test using the original (deprecated) name for renamed options."""

    def config_files(self):
        config_files = super(DeprecatedTestCase, self).config_files()
        config_files.append(unit.dirs.tests_conf('deprecated.conf'))
        return config_files

    def test_sql(self):
        # Options in [sql] were moved to [database] in Icehouse for the change
        # to use oslo-incubator's db.sqlalchemy.sessions.

        self.assertEqual('sqlite://deprecated', CONF.database.connection)
        self.assertEqual(54321, CONF.database.idle_timeout)


class DeprecatedOverrideTestCase(unit.TestCase):
    """Test using the deprecated AND new name for renamed options."""

    def config_files(self):
        config_files = super(DeprecatedOverrideTestCase, self).config_files()
        config_files.append(unit.dirs.tests_conf('deprecated_override.conf'))
        return config_files

    def test_sql(self):
        # Options in [sql] were moved to [database] in Icehouse for the change
        # to use oslo-incubator's db.sqlalchemy.sessions.

        self.assertEqual('sqlite://new', CONF.database.connection)
        self.assertEqual(65432, CONF.database.idle_timeout)
