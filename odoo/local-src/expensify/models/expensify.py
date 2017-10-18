import base64
import json
import datetime

import requests
import yaml
from odoo import models, fields, api, exceptions, _


class Expensify(models.TransientModel):
    _name = 'expensify'

    name = fields.Char(
        default='Expensify',
        readonly=True
    )
    credentials_url = fields.Char(
        string='Credentials',
        default='https://www.expensify.com/tools/integrations/',
        readonly=True
    )
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        default=lambda self: self.get_employee(),
        required=True
    )
    expensify_api_id = fields.Char(
        string='partnerUserID',
        required=True
    )
    expensify_api_secret = fields.Char(
        string='partnerUserSecret',
        required=True
    )
    since_date = fields.Date(
        string='Since date',
        default=lambda self: self.get_since_date(),
        required=True
    )

    @api.model
    def get_employee(self):
        return self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)

    @api.model
    def get_since_date(self):
        return datetime.date.today() - datetime.timedelta(days=30)

    @api.onchange('employee_id')
    def set_expensify_credentials(self):
        for rec in self:
            if not rec.employee_id:
                continue
            rec.expensify_api_id = rec.employee_id.expensify_api_id
            rec.expensify_api_secret = rec.employee_id.expensify_api_secret

    @api.model
    def store_expensify_credentials(self, employee_id, api_id, api_secret):
        employee_id = employee_id.sudo()
        if api_id != employee_id.expensify_api_id:
            employee_id.expensify_api_id = api_id
        if api_secret != employee_id.expensify_api_secret:
            employee_id.expensify_api_secret = api_secret

    @api.multi
    def button_fetch(self):
        self.store_expensify_credentials(self.employee_id,
                                         self.expensify_api_id,
                                         self.expensify_api_secret)

        reports = self.fetch_reports(self.since_date)
        if not reports:
            raise exceptions.ValidationError(
                _("No reports found. Try setting an earlier date?"))

        expenses = [expense for report in reports for expense in
                    report.get('expenses', [])]
        if not expenses:
            raise exceptions.ValidationError(
                _("No expenses found. Try submitting them to a report?"))

        expensify_expenses = []
        for expense in expenses:
            # Extract expense date
            created = expense['created']
            date = created.strftime("%Y-%m-%d")

            # Discard expense if created before since_date
            if date < self.since_date:
                continue

            # Extract expense ID as String (too big for Integer type)
            expensify_id = str(expense['id'])

            # Discard expense if already imported
            if self.get_expense_id(expensify_id):
                continue

            # Extract category and get related Odoo product
            category = expense.get('category')
            product_id = self.get_product_id(category)

            # Extract Expense transaction
            merchant = expense['merchant']
            amount = expense['amount'] / 100.0
            currency = expense['currency']
            currency_id = self.get_currency_id(currency)

            if not currency_id:  # Currency not in Odoo, using converted amount
                converted_amount = expense['convertedAmount'] / 100.0
                converted_currency = expense['convertedCurrency']

                amount = converted_amount
                currency_id = self.get_currency_id(converted_currency)

            # Extract payment mode
            reimbursable = expense['reimbursable']
            payment_mode = "own_account" if reimbursable else "company_account"

            # Extract Expense details
            comment = expense.get('comment')
            tag = expense.get('tag')
            details = expense.get('details')

            # Extract Expense receipt
            receipt = expense.get('receipt', {})
            receipt_url = receipt.get('image')
            receipt_image = self.get_b64_from_url(receipt_url)

            # Build Expense default name
            name = merchant
            if comment:
                name += " (%s)" % comment

            # Build Expense description
            description = "Expensify id: %s\n" % expensify_id + \
                          "Image url: %s\n" % receipt_url + \
                          "Tag: %s\n" % tag + \
                          "Details: %s\n" % details

            expensify_expense = {
                'expensify_id': expensify_id,
                'date': date,
                'name': name,
                'amount': amount,
                'currency_id': currency_id,
                'receipt': receipt_image,
                'description': description,
                'payment_mode': payment_mode,
                'company_id': self.employee_id.company_id.id,
                'product_id': product_id,
            }

            expensify_expenses.append(expensify_expense)

        if not expensify_expenses:
            raise exceptions.ValidationError(
                _("All expenses already imported"))

        # Create and populate Expensify wizard
        expensify_wizard_id = self.env['expensify.wizard'].create({
            'employee_id': self.employee_id.id,
            'since_date': self.since_date,
            'expensify_expenses': [(0, 0, exp) for exp in expensify_expenses]
        })

        # Show Expensify wizard
        return {
            "name": "Import Expenses",
            "type": "ir.actions.act_window",
            "res_model": "expensify.wizard",
            "res_id": expensify_wizard_id.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }

    @api.model
    def get_expense_id(self, expensify_id):
        expense = self.env['hr.expense'].search([
            ('expensify_id', '=', expensify_id)
        ], limit=1)
        if not expense:
            return False
        return expense.id

    @api.model
    def get_product_id(self, category):
        product_id = self.env['product.product'].search([
            ('expensify_category_id', '=', category)
        ], limit=1)
        if not product_id:
            return False
        return product_id.id

    @api.model
    def get_currency_id(self, currency_name):
        currency = self.env['res.currency'].search([
            ('name', '=ilike', currency_name),  # Case insensitive
            '|',
            ('active', '=', True),
            ('active', '=', False)
        ], limit=1)
        if not currency:
            return False
        if not currency.active:
            currency.sudo().write({
                'active': True
            })
        return currency.id

    @api.model
    def get_b64_from_url(self, url):
        try:
            return base64.b64encode(requests.get(url).content)
        except:
            return False

    # EXPENSIFY API

    @api.model
    def _get_api_url(self):
        return "https://integrations.expensify.com/" \
               "Integration-Server/ExpensifyIntegrations"

    @api.model
    def _get_report_template(self, report_name):
        return """reports:
<#list reports as report>
  <#if report.reportName?contains("%s")>
    - id: ${report.reportID}
      name: ${report.reportName}
      status: ${report.status}
      state: ${report.state}
      submitted: ${report.submitted}
      approved: ${report.approved}
      expenses:
      <#list report.transactionList as expense>
        - id: ${expense.transactionID}
          details: ${expense.details}
          inserted: ${expense.inserted}
          tag: ${expense.tag}
          currency: ${expense.currency}
          convertedAmount: ${expense.convertedAmount}
          convertedCurrency: ${report.currency}
          convertedRate: ${expense.currencyConversionRate}
          category: ${expense.category}
          comment: ${expense.comment}
          reimbursable: ${expense.reimbursable?then(1,0)}
          billable: ${expense.billable?then(1,0)}
          taxAmount: ${expense.taxAmount}
          taxName: ${expense.taxName}
          taxRate: ${expense.taxRate}
          taxRateName: ${expense.taxRateName}
          taxCode: ${expense.taxCode}
          <#if expense.modifiedAmount?has_content>
          amount: ${expense.modifiedAmount}
          <#else>
          amount: ${expense.amount}
          </#if>
          <#if expense.modifiedCreated?has_content>
          created: ${expense.modifiedCreated}
          <#else>
          created: ${expense.created}
          </#if>
          <#if expense.modifiedMerchant?has_content>
          merchant: ${expense.modifiedMerchant}
          <#else>
          merchant: ${expense.merchant}
          </#if>
          <#if expense.receiptObject?has_content>
          receipt:
            image: ${expense.receiptObject.url!}
            thumbnail: ${expense.receiptObject.thumbnail!}
            smallthumbnail: ${expense.receiptObject.smallThumbnail!}
            state: ${expense.receiptObject.state!}
            receiptid: ${expense.receiptObject.receiptID!}
            formattedamount: ${expense.receiptObject.formattedAmount!}
          </#if>
    </#list>
    </#if>
</#list>""" % report_name

    @api.model
    def fetch_reports(self, start_date, report_name=""):
        """Requests all reports whose name contains `reportname` and
        where the report was created or updated after `start_date`.
        Returns a dict of reports, keyed on the report ID."""

        report_filename = self._generate_report(start_date, report_name)
        report = self._fetch_file(report_filename)
        return yaml.load(report)['reports']

    @api.model
    def _generate_report(self, start_date, report_name):
        """Requests all reports whose name contains `reportname` and
        where the report was created or updated after `start_date`,
        Returns a filename which should be fed to _fetch_file."""

        params = {
            "requestJobDescription": json.dumps({
                "type": "file",
                "credentials": {
                    "partnerUserID": self.expensify_api_id,
                    "partnerUserSecret": self.expensify_api_secret
                },
                "onReceive": {
                    "immediateResponse": ["returnRandomFileName"]
                },
                "inputSettings": {
                    "type": "combinedReportData",
                    # "reportState": "OPEN",
                    "filters": {
                        "startDate": start_date
                    }
                },
                "outputSettings": {
                    "fileExtension": "txt",
                    "fileBasename": "the_expensify_api_is_horrible"
                },
                "onFinish": [
                    {"actionName": "markAsExported",
                     "label": "Odoo"}
                ]
            }),
            "template": self._get_report_template(report_name)
        }

        response = requests.get(self._get_api_url(), params=params)
        if response.content.endswith(".txt"):
            return response.content
        else:
            raise exceptions.ValidationError(
                _("Error generating report: %s" % response.content))

    @api.model
    def _fetch_file(self, filename):
        """Given a `filename`, fetch it from Expensify."""
        params = {
            "requestJobDescription": json.dumps({
                "type": "download",
                "credentials": {
                    "partnerUserID": self.expensify_api_id,
                    "partnerUserSecret": self.expensify_api_secret,
                },
                "fileName": filename
            })
        }

        response = requests.get(self._get_api_url(), params=params)
        if response.status_code == 200:
            return response.content
        else:
            raise exceptions.ValidationError(
                _("Error fetching report: %s" % response.content))
