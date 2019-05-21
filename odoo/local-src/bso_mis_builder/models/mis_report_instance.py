# from datetime import datetime
import re

from odoo import api, models, fields


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    forecast_report_id = fields.Many2one(
        string='Forecast Report',
        comodel_name='forecast.report',
    )

    @api.multi
    def compute(self):
        self.ensure_one()
        if not self.forecast_report_id:
            return super(MisReportInstance, self).compute()
        self.forecast_report_id.refresh()
        kpi_matrix_dict = super(MisReportInstance, self).compute()
        return self.add_query_drilldown_args(kpi_matrix_dict)

    def add_query_drilldown_args(self, kpi_matrix_dict):
        for row in kpi_matrix_dict.get('body', []):
            for cell in row.get('cells', []):
                # n_telco_r = q_n_telco_r.total
                if not re.match(
                        r"(?P<type>[a-z_]+)"
                        r"\s\=\s"
                        r"(?P<query_name>[a-z_]+)"
                        r"\."
                        r"(?P<query_field>[a-z]+)", cell['val_c']):
                    break
            else:
                query = self.report_id.query_ids.filtered(
                    lambda q: q.name == 'q_%s' % row['row_id'])
                row['drilldown_arg'] = {
                    'row_model_name': query.row_model_id.model,
                    'type': row['row_id'],
                }
        return kpi_matrix_dict

    @api.multi
    def drilldown(self, arg):
        self.ensure_one()
        res = super(MisReportInstance, self).drilldown(arg)
        if not res:
            row_model_name = arg.get('row_model_name')
            line_type = arg.get('type')
            if line_type and row_model_name:
                domain = [('company_id', '=', self.company_id.id),
                          ('report_id', '=', self.forecast_report_id.id),
                          ('type', '=', line_type)]
                return {
                    'name': 'Details',
                    'domain': domain,
                    'type': 'ir.actions.act_window',
                    'res_model': row_model_name,
                    'views': [[False, 'list'], [False, 'form']],
                    'view_type': 'list',
                    'view_mode': 'list',
                    "context": {'report_id': self.forecast_report_id.id,
                                'type': line_type},
                    'target': 'current',
                }
        return res


class MisReportInstancePeriod(models.Model):
    _inherit = "mis.report.instance.period"

    @api.multi
    def _get_additional_query_filter(self, query):
        self.ensure_one()
        if not self.report_instance_id.forecast_report_id:
            return []
        domain = [('company_id', '=', self.report_instance_id.company_id.id),
                  ('report_id', '=',
                   self.report_instance_id.forecast_report_id.id)]
        return domain
