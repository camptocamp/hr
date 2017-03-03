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
