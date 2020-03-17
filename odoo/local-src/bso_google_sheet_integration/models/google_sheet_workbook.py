from odoo import models, fields, api


class GoogleSheetWorkbook(models.Model):
    _name = 'google.sheet.workbook'
    _order = 'name'

    name = fields.Char(
        string='Workbook Name',
        readonly=True
    )
    workbook_ref = fields.Char(
        string='Workbook ID',
        required=True
    )
    src = fields.Char(
        string='Workbook URL',
        compute='compute_src',
        store=True
    )
    server_action_id = fields.Many2one(
        string='Server Action',
        comodel_name='ir.actions.server',
        required=True
    )
    iframe = fields.Html(
        string='Embedded Workbook',
        compute='_compute_iframe',
        sanitize=False,
        strip_style=False,
        store=True
    )
    group_ids = fields.Many2many(
        string='Groups',
        comodel_name='res.groups'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.depends('workbook_ref')
    def compute_src(self):
        for rec in self:
            rec.src = 'https://docs.google.com/spreadsheets/d/%s' % \
                      rec.workbook_ref

    @api.multi
    def refresh_action(self):
        for rec in self:
            rec.server_action_id.with_context(
                {'active_model': self._name, 'active_id': rec.id}).run()

    @api.depends('src')
    def _compute_iframe(self):
        for rec in self:
            template = self.env.ref(
                'bso_google_sheet_integration.workbook_iframe'
            )
            rec.iframe = template.render({'url': rec.src})
