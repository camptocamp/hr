.. :changelog:

.. Template:

.. 0.0.1 (2016-05-09)
.. ++++++++++++++++++

.. **Features and Improvements**

.. **Bugfixes**

.. **Build**

.. **Documentation**

Release History
---------------

Latest (Unreleased)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1130: install sale_contract_tax_subscription

**Bugfixes**

* BSIBSO-1132: update odoo and enterprise to latest

**Build**

* BSIBSO-1134: use wkhtml2pdf 0.12.5

**Documentation**


10.20.0 (2019-01-24)
++++++++++++++++++++

**Features and Improvements**

* BSIBSO-1127: Add oca/currency repository
* BSIBSO-1127: Add from oca/currency the module currency_monthly_rate
* BSIBSO-1127: Update oca account_multicurrency_revaluation to add rate_type
  like that the currency revaluation is doing by days or with monthly average rate
* Dealsheet improvements by Gapard Coudurier (PR #286)
* BSIBSO-1116: a batch of improvements in account_financial_report_qweb

**Bugfixes**

* BSIBSO-1129: fix the computation of qty_delivered on sales line in the case
  where the sale order has a contract (in that case, we want to force this to
  the qty invoiced for MRC products)
* BSIBSO-1129: make sure we don't create multiple sale subscriptions for the
  same sale order.

**Build**

* BSIBSO-1111: Migrate project to docker image 3.1
* BSIBSO-1118: Apply patches for ODOO-SA-2018-11-28


10.19.0 (2018-12-20)
++++++++++++++++++++

**Features and Improvements**

* BSIBSO-1125: Add from oca/web module web_sheet_full_width
* BSIBSO-1125: Modification of the purchase_id domain in the supplier invoice
  to have only purchase orders in the currency of the invoice
* BSIBSO-1122: Add new field in purchase order `Continue after end`
* BSIBSO-1121: Active field in 'purchase.order', filter into view
* BSIBSO-1117: have a customer dependent numbering for analytic accounts
* bso_backbone: change the visibility of some fields in the views
* bso_custom_doc: update
* bso_report_saleorder: custom Sale Order Report for Website quote
* BSIBSO-1120: Recurring supplier invoices, add "yearly" option
* bso_restrict_attachments_visibility installation

**Build**

* BSIBSO-1114: Change test admin password


10.18.1 (2018-12-11)
++++++++++++++++++++

**Bugfixes**

* fix bso_backbone (pr#269)
* access right issue when creating a refund


10.18.0 (2018-11-29)
++++++++++++++++++++

**Features and Improvements**
* BSIBSO-1079: generate recurring invoices 10d in advance (delay can be
  adjusted in the cron parameters)

* BSIBSO-1107: Change the delivery date of a picking
* BSIBSO-1103 Connector-exchange: add flag on res.users to filter for Odoo events
* BSIBSO-1103 Connector-exchange: add parameter to search with a max horizon
* BSIBSO-1106: Recurring supplier invoices
* install bso_custom_doc

**Bugfixes**
* BSIBSO-1092: fix invoicing of sales with MRC

* BSIBSO-1108: Replace record rule for multicompany on stock.picking.type to 1=1

**Build**

* BS-233: Remove submodule odoo-prototype
* BSIBSO-1105: update OCA repos
    - account-closing
    - account-financial-reporting
* BSIBSO-1105: Install OCA repos from account-analytic
    - analytic_tag_dimension
    - analytic_tag_dimension_purchase_warning
    - analytic_tag_dimension_sale_warning

* BSIBSO-1103 Update OCA/connector repository


10.17.1 (2018-10-30)
++++++++++++++++++++

**Bugfixes**

* BSIBSO-1102: Force the drop of specific_crm.assets_backend view after its move to bso_telephony module


10.17.0 (2018-10-25)
++++++++++++++++++++

**Features and Improvements**

* BSIBSO-1093: Install module bso_telephony
* BSIBSO-1093: Replace Dial button by a phone icon
* purchase order: add a cron to recompute the received qty each day
* update bso_backbone: cympa sychronization
* BSIBSO-1097: Install mass_editing

**Bugfixes**
* purchase order invoicing: fix the received quantity computation

**Build**

* Applying security advisory 2018-08-07
* remove DJ and compilations


10.16.0 (2018-09-03)
++++++++++++++++++++

**Features and Improvements**

* BSO Dashboards update (PR 242)
* disable automatic addition of partner & lead as follower on crm.lead and
  res.partner
* mailchimp integration update
* BSIBSO-1090: Add ACL for Manager on account.payment.mode

**Bugfixes**

* BSIBSO-1078_fix: reverting last minute change that was breaking the thing


10.15.0 (2018-08-23)
++++++++++++++++++++

**Features and Improvements**

* BSIBSO-1087: add a boolean field to pilot lead generation from a partner. If
  the field is unset, the lead is deleted.
* BSIBSO-1086: fix "can't set the sale pricelist to GBP"

**Bugfixes**

* BIZ-2141 - don't update opportunities when partner is updated, only leads
* fix the way a unique index is generated for lead emails.
  CAUTION: no index is generated until duplicates are cleaned. Once this is
  done, restart odoo to get the unicity enforced in the future.


10.14.1 (2018-08-15)
++++++++++++++++++++

**Bugfixes**

* BSIBSO-1072: Fix invoice update wizard not updating analytic account
* biz-2139: Set name of lead only at creation of customer


10.14.0 (2018-08-13)
++++++++++++++++++++

**Features and Improvements**

* BSIBSO-1075: Move menu Lead under Marketing section
* BSIBSO-1083: Reclaim `Dial` button on `phone` widget
* BSIBSO-1076: no create/update of customer in opportunity form
* BSIBSO-1078: change the propagation of client_order_ref

**Bugfixes**

* BIZ-2106: Fix "editing a partner kill relations with opportunities"


10.13.1 (2018-08-09)
++++++++++++++++++++

**Bugfixes**

* Remove self.ensure_one in method write in bso_mailchimp


10.13.0 (2018-08-09)
++++++++++++++++++++

**Features and Improvements**
  * Improvements in Mailchimps webhook

**Bugfixes**
 * Fix in Dashboard, Backbone, Mailchimp
     PR #225 #226 #228 #229

**Build**

**Documentation**


10.12.0 (2018-08-03)
++++++++++++++++++++

**Features and Improvements**

  * Add custom mailchimp addon
    * #224 BSO Mailchimp
  * Add custom dashboard addon
    * #223 BSO Dashboards
  * integrate bso_dealsheet and bso_bundle minor change
    * #217 BSO backbone bundle dealsheet update


**Bugfixes**

* BIZ-2081: Fix new lead creation by displaying `currency_id` on the form
* integrtate bso expensify fix
  * #215 Expensify fix

**Build**

**Documentation**


10.11.0 (2018-07-23)
++++++++++++++++++++

**Bugfixes**

* BSIBSO-1081: fix regression from Odoo restricting the kind of products you
  can use for sale subscriptions


10.10.0 (2018-07-17)
++++++++++++++++++++

**Bugfixes**

* BSIBSO-1074: Fix invoice NRC manual before 1st delivery
* BSIBSO-1073 Fix multicurrency flow in `crm.lead

**Build**

* BSIBSO-1069: Sync project and update image version.


10.9.0 (2018-07-13)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1066: Add a menu 'sources' under sales
* BSIBSO-1061: Install account_invoice_update_wizard
* BSIBSO-1067: Implement multicurrency in `crm.lead`
* BSIBSO-1070: Restyle stuff implemented in =BSIBSO-1067=
* BSIBSO-1068: Add telephony asterisk connector



10.8.1 (2018-07-04)
+++++++++++++++++++

**Bugfixes**

* fix issue with xml_ids from l10n_lu module


10.8.0 (2018-06-29)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1060: install `l10n_fr_certification`
* BSIBSO-1059: On invoice print out display "Ref. Source" on a separate line as it can contain multiple references after invoice merge.
* BSIBSO-1065: On invoice print out display add start and end dates on invoice lines.
* BSIBSO-1064: Disable creation of customers on leads.
* BSIBSO-1063: Remove buttons on leads.
* BSIBSO-1062: Add Old ref field to analytic account.
* install `connector_exchange` module

**Bugfixes**

* BSIBSO-1060: fix for the template for customer invoice as it couldn't find
  element by xpath after core upgrade

**Build**

* BSIBSO-1060: in short, updated odoo to get the fix for `l10n_fr_certification`
* upgrading this broke l10n_lu_reports from enterprise(it is auto-installed module)
* dropped useless pending merge for enterprise with git -am patches as they
  were long time implemented
* updated enterprise submodule
* add `connector-exchange` repo

**Documentation**


10.7.0 (2018-06-15)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1055: Add `Existing customers` filter to `crm.lead` search view
* BSIBSO-1056: Use data from SO when create subscription.
* install bso_expenses_holidays_filtering
* install bso_hr_holidays_report
* bso_backbone: log all changes
* BSIBSO-1058: fix several fields not getting propagated during invoice merge
* install `base_export_manager`

**Bugfixes**

* BSIBSO-1054: Enforce default `type` value to `crm.lead` records through custom action
* BSIBSO-1057: Fix error when click on 'generate invoice' from subscription

**Build**

* Reduce docker image size by removing unused .po files
* Upgrade docker-compose to 1.17.1
* add `mailchimp3` python lib in requirements

**Documentation**


10.6.0 (2018-05-18)
+++++++++++++++++++

**Features and Improvements**

* install bso_employee_notebook_visibility
* update bso_backbone_bundle_dealsheet


10.5.0 (2018-05-03)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1052 Added propagation of origin to the invoice lines
* Uninstall sale_line_cost_control and sale_margin

**Bugfixes**

* Manually generated invoices from SO: end date on invoice line must be the
  day before the reference date


10.4.1 (2018-04-11)
+++++++++++++++++++

**Bugfixes**

* preserve price and description when sourcing from a dealsheet


10.4.0 (2018-04-09)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1050: Remove Bank account section on customer invoice
* BSIBSO-1033: Set date and invoice_date to the same date as the cron generating
  the invoices for subscriptions is ran
* BSIBSO-1043 Use mailtrap as outgoing mail server if env not prod or integration
* BSIBSO-1035: create crm.industry and it's sub models, add new fields to leads
  customers now create one lead id they don't have one
* BSIBSO-1036: Add new module specific_mailchimp with models:
  * crm.mailchimp.campaign
  * crm.mailchimp.mailing
  * crm.mailchimp.mailing.stats
  * create.campaign.wizard to create campaigns from leads
* BSIBSO-1049: install CFONB bank statement import
* BSIBSO-1048: propagate PO analytic account on SO in intercompany flow.
* BSIBSO-1047: manage subscriptions to customer invoices
* Revamp of product bundle by Gaspard

**Bugfixes**

* BSIBSO-1038: Set field "Start date of next invoice period" required to avoid
  stacktraces when generating invoices for manually created subscriptions

**Build**

* BSIBSO-1043 Do not setup LDAP if env not prod or integration


10.3.7 (2018-03-07)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1032: Change the way analytic accounts / projects are numbered
  the name of the analytic account must be generated as follows AARRR/BBBBCC/DDDDD
* BSIBSO-1031: move the Procure button from Sale Order to Dealsheet screen
* BSIBSO-1031 Move procure from sale order to dealsheet
* BSIBSO-1031 Hide Set cost button on sale order line

**Bugfixes**

**Build**

* Fix minion (increase memory used)
* Update project from odoo template. Install camptocamp_tools.


10.3.6 (2018-02-19)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1030: Switch positions of payment mode and bank account on invoice report

**Bugfixes**

* Fix : change of the payment mode on a sale order when using the company currency


10.3.5 (2018-01-25)
+++++++++++++++++++

**Features and Improvements**

* New module bso_backbone: Store X-Connects, Links, Devices & POPs
* New module bso_dealsheet: Dealsheet Costs, Margin & Validation Process
* Update customer invoice layout

**Build**

* Update odoo-cloud-platform (BIZ-1093)

10.3.4 (2018-01-12)
+++++++++++++++++++

**Features and Improvements**
* expensify: only fetch user's reports & discard expense date


10.3.3 (2018-01-12)
+++++++++++++++++++

**Features and Improvements**

* payment mode propagate from SO to invoices via subscriptions

**Bugfixes**

* do not empty contract_template field in sale order

**Build**

**Documentation**


10.3.2 (2018-01-05)
+++++++++++++++++++

**Features and Improvements**

* Install module account_multicurrency_revaluation
* display VAT in company currency + exchange rate on invoices with a different
  currency
* Invoicing release for production

**Bugfixes**

* BSIBSO-1073: Fix multicurrency flow & views in `crm.lead`

**Build**

**Documentation**


10.3.1 (2017-12-04)
+++++++++++++++++++

**Features and Improvements**

* ``expensify`` module modifications


10.2.9 (2017-12-04)
+++++++++++++++++++

**Features and Improvements**

* ``expensify`` module modifications

10.3.0 (2017-11-21)
+++++++++++++++++++

**Features and Improvements**

* install ``product_bundle``


10.2.8 (2017-11-21)
+++++++++++++++++++

**Bugfixes**

* install ``bso_hr_validation``
* delete modules ``leaves_constraints`` and ``hr_date_validated``

**Build**

* add OCA repos ``account-closing``, ``bank-payment``,
  ``l10n-france``, ``intrastat``


10.2.7 (2017-11-13)
+++++++++++++++++++


10.2.6 (2017-11-10)
+++++++++++++++++++


10.2.5 (2017-11-06)
+++++++++++++++++++

**Features and Improvements**

* install ``hr_date_validated`` from BSO

**Bugfixes**

* remove onchange and constraint on hr_expense
* migration and upgrade files
* fix date next invoice of contract to ref_date of the last
  invoice which fulfilled the delivery of mrc
* fix monthly and period recurring price
* hide 'cancel subscription' btn
* contract creation from sale order
* change computation of dates
* do not invoice ended purchase subscriptions
* purchase order generation. take care of duration
* computation of date end subscription in purchase orders
* subscription information in purchase order form view


10.2.4 (2017-10-20)
+++++++++++++++++++

**Bugfixes**

* Expensify connector
* FIX post release: upgrade failure

10.2.3 (2017-10-18)
+++++++++++++++++++

**Features and Improvements**

* Add expense_tax
* Install module account tag category BSIBSO-1021
* Expensify connector

**Bugfixes**

* issues in sale purchase sourcing (BSIBSO-1024)


10.2.2 (2017-10-17)
+++++++++++++++++++

**Features and Improvements**

* Added Employee group back to Timesheets access rights
  via song BSIBSO-1019
* Add modules date_range and account_financial_report_qweb BSIBSO-1020
* Add leaves_constraints to prevent self validation / self refusal of
  hr.holidays requests

**Bugfixes**

* Fix selectable product on expense and restrict account field



10.2.1 (2017-09-28)
+++++++++++++++++++

**Features and Improvements**

* Update with last changes from odoo-template
* Remove pending-merges in partner-contact partially removed in f71bb19
* Update PO `subscr_date_start` if there is none while processing stock.picking BSIBSO-1009
* update subscription invoicing BSIBSO-1004
* add specific_expense BSIBSO-1017
* subscription renewal/cancelation BSIBSO-1006

**Bugfixes**

* Computation of PO `_compute_has_subscription` from BSIBSO-1008
* [fix] specific_sale: SO._setup_fields refactor and add tests for state ordering
* [fix] specific_sale: make tests work


**Build**

* Update docker-image to 10.0-2.4.0

**Documentation**


10.2.0 (2017-09-19)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-1003 Invoicing process for MRP products
* BSIBSO-1012 Logic creation subscription
* Automatic Invoicing of PO BSIBSO-1010
* Overload mrc compute_qty_received BSIBSO-1010
* BSIBSO-1013 Prevent employees to edit or delete events if they are not owners
* BSIBSO-962 Invoice timesheet report
* BSIBSO-1014 employee form and kanban views enhancement
* BSIBSO-1016 enforce employee company_id leave type on holiday allocation/request
* BSIBSO-1008 fix price from supplier info


10.1.7 (2017-08-28)
+++++++++++++++++++

**Features and Improvements**

* Add DJ & Ribbon

10.1.6 (2017-08-18)
+++++++++++++++++++

**Bugfixes**

* Fix email configuration


10.1.5 (2017-08-04)
+++++++++++++++++++

**Features and Improvements**

* BSIBSO-998 Outgoing email configuration
* BSIBSO-999 Edit record rules

**Bugfixes**

**Build**

* Upgrade Docker image to 10.0-2.3.0
* Update odoo/src to latest commit
* update project from odoo-template

**Documentation**


10.1.4 (2017-07-04)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* change port used for smtp 587 --> 25
* reset all email addresses
* add logging on ``update_leaves_allocation`` method

**Build**

**Documentation**


10.1.3 (2017-05-08)
+++++++++++++++++++

**Features and Improvements**

* add mrc, nrc and duration in opportunity tree and kanban view
* add new addon adding cost indicator and button to set cost on sale lines
* install 'sale_line_cost_control'**Bugfixes**

**Bugfixes**

* Correct firstname-lastname order before importing employees

**Build**

* update Docker image to camptocamp/odoo-project:10.0-2.2.0
* Update odoo-cloud-platform to have Redis Sentinel support
* add margin-analysis OCA repository
* Upgrade base image
  Fixes security vulnerability CVE-2017-8291


10.1.2 (2017-05-05)
+++++++++++++++++++

**Bugfixes**

* fix the docker configuration again


10.1.1 (2017-05-05)
+++++++++++++++++++

**Bugfixes**

* fix the docker configuration


10.1.0 (2017-05-04)
+++++++++++++++++++

**Features and Improvements**

* port to v10


10.0.0 (2017-03-21)
+++++++++++++++++++

fake release to bump version

9.7.0 (2017-03-21)
++++++++++++++++++

**Features and Improvements**

* BSIBSO-908 Setup mail interface
* BSIBSO-935 Add triple validation on sale order


9.6.4 (2017-03-03)
++++++++++++++++++

**Features and Improvements**

* install ``subcontracted_service`` module to manage procurement of services


9.6.3 (2017-02-24)
++++++++++++++++++

**Features and Improvements**

* Base COA configuration for companies
* One warehouse by company and by POP
* better management of backup percent discount
* configure sale app to manage product variants
* configure subscription template and sale template
* show routes characteristics
* hide backup fields according if backup route is asked or not
* simplify tree view of sale order


9.6.2 (2017-02-14)
++++++++++++++++++

**Features and Improvements**

* simplify EPL management



9.6.0 (2017-02-10)
++++++++++++++++++

**Features and Improvements**
* Add module contact firstname
* Add module employee firstname
* Add access rights management for HR part
    - holidays
    - expense
    - timesheets
    - employees

**Build**
* version 2.0.0 of base odoo image



9.5.0 (2017-01-27)
++++++++++++++++++

**Features and Improvements**

* EPL: automatically filled by API calls
* Users: add fields for Expensify

**Build**

* speed up travis builds


9.4.1 (2017-01-17)
++++++++++++++++++

**Features and Improvements**

* Computation of holidays & rtt on prorata for the first month
* ``EPL`` product on sale order line
* POC on access rights

**Bugfixes**

* Change label "Per month rtt allocation" to set RTT in capitals
* Field "remaining legal leaves" to readonly
* Change Label "Is rtt" in "Is RTT"
* Change label "Exclude rest days" in "Exclude week-end"
* set group "base.group_no_one" on button "update leaves"
* Correction on days caluculation for the imposed days
* Onchange leave_type update company_id
* Domain on leave_type a company is selected
* Domain on employees if s company is selected


**Build**

**Documentation**


9.4.0 (2016-12-07)
++++++++++++++++++

**Features and Improvements**

* add Jira (7.2) connector

**Bugfixes**

* issue in ``hr_holidays_imposed_days`` module on creating an employee

**Build**

**Documentation**


9.3.0 (2016-12-06)
++++++++++++++++++

**Features and Improvements**

* install ``partner_address_street3`` and ``partner_multi_relation`` from
    ``OCA/partner-contact`` repo
* add module ``specific_product`` to manage the following objects:

    - POPs: Point of Presence
    - POP devices: devices in POPs
    - cable sytem
    - Links: links between 2 PoPs and characterized by bandwith, latency, nrc,
        mrc
    - integration of those objects in sales
* Add hr employee import
* holidays and compensatory allocations are incremented each month
* Seniority of an employee is managed on its record
* Manage holidays on half-day basis
* Add imposed days
* Manage legal leaves and compensatory allocations per company


**Bugfixes**

* Fix pep8 in specific_hr & specific_fct

**Build**

* switch to OCA/OCB
* update docker-odoo-template to 1.7.1


9.2.1 (2016-10-27)
++++++++++++++++++

**Features and Improvements**

* create a group ``BSO HR confidential`` to manage sensitive information on
    ``hr.contract`` object
* import user from LDAP with givenName + SN as name instead of cn
    add a group hr_confidential to restrict sensitive data to a indentified
    group
* when importing a user and try to map it to an employee, fill company and
    email information on partner related to the user

**Bugfixes**

* import ``hr.employee`` with ``+`` character in phone numbers

**Build**

**Documentation**
    - when creating a user, an employee is not created anymore if
      an employee with this login or with the field ``user_login`` is not found

9.2.0 (2016-10-24)
++++++++++++++++++

**Features and Improvements**

* install base modules:
    - ``hr_recruitment``
    - ``auth_ldap``
    - ``hr_timesheet_sheet``
    - ``hr_recruitment``
    - ``l10n_fr``
    - ``purchase``
    - ``stock``
    - ``connector``
    - ``hr_family``
    - ``users_ldap_populate``
    - ``web_easy_switch_company``
    - ``specific_hr``

* install ``es_ES`` language in addition of ``en_US`` and ``fr_FR``
* import companies, employees (and some HR stuff)

**Bugfixes**

**Build**

**Documentation**
    - when creating a user, an employee is created and linked to this user if
      an employee with this login or with the field ``user_login`` is not found


9.1.0 (2016-09-14)
++++++++++++++++++

**Features and Improvements**

* install base modules:
    - ``hr``
    - ``sale_contract``
    - ``sale_service``
    - ``crm``
    - ``account``
    - ``analytic``
    - ``hr_holidays``
    - ``hr_expense``
    - ``document``

* install ``fr_FR`` language in addition of ``en_US``

**Bugfixes**

**Build**

**Documentation**
