# -*- encoding: utf-8 -*-
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx


class partner_xlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)


partner_xlsx('report.res.partner.xlsx',
             'res.partner')
