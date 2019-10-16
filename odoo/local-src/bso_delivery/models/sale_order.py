# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_project_id = fields.One2many(
        string='Delivey Project',
        comodel_name='delivery.project',
        inverse_name='sale_order_id'
    )

    @api.multi
    def create_project_delivery(self):
        self.ensure_one()
        delivery_project = self.delivery_project_id.create({
            'name': '{} {}'.format(self.name, self.partner_id.name),
            'sale_order_id': self.id,
            'jira_key': self.name,
            'kickoff_date': datetime.now(),
            'date_signed': self.commitment_date
        })
        self.update({'delivery_project_id': [(6, 0, [delivery_project.id])]})
        return {
            "type": "ir.actions.act_window",
            "res_model": "delivery.project",
            "views": [[False, "form"]],
            "res_id": self.delivery_project_id.id,
        }
