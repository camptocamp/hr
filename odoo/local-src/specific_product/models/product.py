# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
from openerp.osv import fields as ofields

import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # link_type = fields.Selection([('a', 'a'),
    #                               ('b', 'b'),
    #                               ('c', 'c')])
    # rts = fields.Float()
    # sla = fields.Float()
    # mrc = fields.Float()
    # nrc = fields.Float()
    # variant_name = fields.Char()
    # display_name = fields.Char(compute='compute_display_name')

    # @api.depends('name', 'variant_name')
    # def compute_display_name(self):
    #     for product in self:
    #         display_name = product.name
    #         if product.variant_name:
    #             display_name += " %s" % product.variant_name
    #         product.display_name = display_name

    # @api.multi
    # def name_get(self):
    #     res = super(ProductProduct, self).name_get()
    #     res2 = []
    #     for p_id, name in res:
    #         product = self.browse(p_id)
    #         if product.variant_name:
    #             name += " %s" % product.variant_name
    #         res2.append((p_id, name))

    #     return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # pop_src = fields.Many2one(comodel_name='res.partner')
    # pop_dst = fields.Many2one(comodel_name='res.partner')
    # supplier_id = fields.Many2one(comodel_name='res.partner',
    #                               domain=[('supplier', '=', True)])
    mrc = fields.Float()
    nrc = fields.Float()
    is_epl = fields.Boolean(default=False)

    def _price_get(self, cr, uid, products, ptype='list_price', context=None):
        if context is None:
            context = {}
        res = super(ProductTemplate, self)._price_get(
            cr, uid, products, ptype=ptype, context=context)
        for product in products:
            if product.is_epl:
                price = (
                    product.nrc + (product.mrc * context.get('duration', 0))
                )
                res[product.id] = price
        return res
