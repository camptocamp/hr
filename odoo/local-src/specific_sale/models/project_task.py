# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    mrp_bom_ids = fields.One2many(
        'mrp.bom',
        'project_task_id',
        string='BOM',
    )
    bom_count = fields.Integer(
        compute='_compute_linked_bom',
        string='Count BOM',
    )

    def action_view_bom(self):
        action = self.env.ref('mrp.mrp_bom_form_action')
        result = action.read()[0]
        result['context'] = {'default_project_task_id': self.id}
        return result

    def _compute_linked_bom(self):
        BOM = self.env['mrp.bom']
        for task in self:
            task.bom_count = BOM.search_count([
                ('project_task_id', '=', task.id)])

    @api.model
    def create(self, vals):
        if self.env.context.get('_from_create_service_task'):
            vals = vals.copy()
            project_id = vals.get('project_id')
            product_id = self.env.context['_from_product_id']
            project = self.env['project.project'].browse(project_id)
            product = self.env['product.product'].browse(product_id)
            vals['name'] = '%s:%s' % (project.name, product.name)
        return super(ProjectTask, self).create(vals)
