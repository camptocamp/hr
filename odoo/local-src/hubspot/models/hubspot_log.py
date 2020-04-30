# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

logger = logging.getLogger(__name__)


class HubspotLog(models.Model):
    _rec_name = "lead_id"
    _name = "hubspot.log"

    lead_id = fields.Many2one(
        string="Lead",
        comodel_name="crm.lead"
    )
    params = fields.Text(
        string="Parameters"
    )
    error_message = fields.Char(
        string="Error Message"
    )
    function_name = fields.Char(
        string="Function Name"
    )
    hubspot_contact_id = fields.Char(
        string='Hubspot Contact ID',
    )
    hubspot_deal_id = fields.Char(
        string='Hubspot Deal ID',
    )
