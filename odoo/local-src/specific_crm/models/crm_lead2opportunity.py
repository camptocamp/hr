# -*- coding: utf-8 -*-

from odoo import api, models


class CrmLead2OpportuniyPartner(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner"

    @api.multi
    def _convert_opportunity(self, vals):
        lead_ids = vals.get('lead_ids', [])
        new_leads = []
        for lead in lead_ids:
            original_lead = self.env['crm.lead'].browse(lead)
            new_lead = original_lead.copy()
            new_lead.write({
                'original_lead_id': original_lead.id,
            })
            new_leads.append(new_lead.id)
        vals['lead_ids'] = new_leads
        res = super(CrmLead2OpportuniyPartner, self)._convert_opportunity(vals)
        return res
