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

**Bugfixes**

**Build**

**Documentation**


10.2.6 (2017-11-10)
+++++++++++++++++++

**Features and Improvements**

* add ``product_bundle`` module


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
