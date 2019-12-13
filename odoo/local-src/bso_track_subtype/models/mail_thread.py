# -*- coding: utf-8 -*-


from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def write(self, vals):
        if self._context.get('tracking_disable') or self._context.get(
                'mail_notrack'):
            return super(MailThread, self).write(vals)
        tracked_fields = self._get_new_tracked_fields()
        if tracked_fields:
            initial_values = {rec.id: {key: getattr(rec, key) for key in
                                       tracked_fields} for rec in self}
        res = super(MailThread, self).write(vals)
        for rec in self:
            if tracked_fields:
                rec_init_vals = initial_values.get(rec.id, {})
                rec.auto_notify_partners(rec_init_vals)
        return res

    def _get_new_tracked_fields(self):
        return self.env['mail.message.subtype'].search([
            ('res_model', '=', self._name),
            ('field_id', '!=', False),
        ]).mapped('field_id.name')

    @api.model
    def create(self, vals):
        if self._context.get('tracking_disable') or self._context.get(
                'mail_notrack'):
            return super(MailThread, self).create(vals)
        tracked_fields = self._get_new_tracked_fields()
        if tracked_fields:
            initial_values = {key: False for key in tracked_fields}
        rec = super(MailThread, self).create(vals)
        if tracked_fields:
            rec.auto_notify_partners(initial_values)
        return rec

    def auto_notify_partners(self, init_values):
        for key, init_val in init_values.iteritems():
            trigger_value = getattr(self, key)
            if init_val == trigger_value:
                continue
            subtype_id = self.env['mail.message.subtype'].search([
                ('res_model', '=', self._name),
                ('field_id.name', '=', key),
                ('trigger_value', '=', '%s' % trigger_value),
            ])
            if not subtype_id:
                continue
            partners = self.env['res.partner']
            if subtype_id.notify_existing_followers:
                partners |= self.message_partner_ids
            if subtype_id.partner_ids:
                partners |= subtype_id.partner_ids
            old_value = init_values.get(key, '') or ''
            self.message_post(
                subtype_id=subtype_id.id,
                body=self.get_message_body(key, trigger_value, old_value),
                subject=subtype_id.description,
                partner_ids=partners.ids)
        return

    def get_message_body(self, key, val, old_value):
        self.ensure_one()
        arrow = '<span>&#8594;</span>' if old_value else ''
        field_name = self.fields_get(key, 'string')[key]['string']
        return '<ul><li> %s: %s %s %s </li></ul>' % (
            field_name, old_value, arrow, val)
