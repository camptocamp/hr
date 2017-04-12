# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _create_service_task(self):
        _super = super(ProcurementOrder,
                       self.with_context(_from_create_service_task=True,
                                         _from_product_id=self.product_id.id))
        return _super._create_service_task()
