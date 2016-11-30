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
* holidays allocations are incremented each month

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
