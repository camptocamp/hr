from odoo import models, fields, api


class PopUpMessage(models.TransientModel):
    _name = 'pop.up.message'

    name = fields.Char(
        string='title'
    )
    description = fields.Text(
        string='Description',
        required=True
    )

    @api.multi
    def action_ok(self):
        """
        call action_ok implemented on the active_model, to process with the
        execution
        :return: the return of the action_ok implemented on the active_model
        """
        self.ensure_one()
        active_model = self.env[self.env.context['active_model']]._name
        res_id = self.env.context['active_id']
        return self.env[active_model].browse(res_id)._action_ok()

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def show(self, args):
        """
        Shows a pop up message to the user, when calling this method from a
        model, a method called action_ok have to be implemented on the same
        model, to handle the ok case.
        :param args: a dict with two keys, name & description to be displayed
        on the pop up
        :return: pop up view
        """
        message = self.create(
            {'name': args['name'], 'description': args['description']}
        )

        return {
            'name': message.name,
            'type': 'ir.actions.act_window',
            'res_model': 'pop.up.message',
            'res_id': message.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
