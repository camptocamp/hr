# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProjectZone(models.Model):
    _name = 'project.zone'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)


class ProjectProcess(models.Model):
    _name = 'project.process'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)


class ProjectMarket(models.Model):
    _name = 'project.market'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
