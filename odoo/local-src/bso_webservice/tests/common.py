# -*- coding: utf-8 -*-
# © 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import odoo.tests.common as common


class BaseTestCase(common.SavepointCase):
    """ Base class for Tests with the ESB backend """

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls.ws = cls.env['bso.ws']
        cls.setup_records()

    @classmethod
    def setup_records(cls):
        pass
