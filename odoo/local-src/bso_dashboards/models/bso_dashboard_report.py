# -*- coding: utf-8 -*-
import json

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class BSODashboardReport(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, graph):
        graph_type = json.loads(graph.graph).get('settings', {}).get(
            'graph_type')
        if not graph_type:
            return
        data = json.loads(graph.graph).get('data', [])
        if not data:
            return
        sheet = workbook.add_worksheet('Sheet 1')
        bold = workbook.add_format({'bold': True})
        x_axis_label = self.get_axis_label(graph.groupby_id,
                                           graph.groupby_interval)
        y_axis_label = self.get_axis_label(graph.measure_id,
                                           graph.measure_consolidate_id)
        sheet.write(0, 0, graph.name)
        sheet.write(1, 0, x_axis_label, bold)
        sheet.write(1, 1, y_axis_label, bold)
        if graph_type == 'bar' or graph_type == 'line':
            data = data[0].get('values', [])
        for counter, line in enumerate(data):
            values = line.values()
            sheet.write(counter + 1, 0, values[1], bold)  # key
            sheet.write(counter + 1, 1, values[0], bold)  # value

    def get_axis_label(self, column, column_type):
        if not column_type:
            return column.name
        return "%s %s" % (column.name, column_type.name)


BSODashboardReport('report.bso.dashboard.report',
                   'bso.dashboard.graph')
