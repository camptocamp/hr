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


Latest (unreleased)
+++++++++++++++++++

**Bugfixes**

* fix view of crm.lead
* improve view of customer license
* add website_contract to get subscriptions working

10.0.12 (2017-04-26)
++++++++++++++++++++

**Features and Improvements**

* Install sale_contract
* Remove signatures on leads
* update transitions checks in crm
* Add NDA Leads in customer's form
* Email temaplate & Button for 'final_quote'
* Add Customer's Licenses models & views
* Set intercompany rules
* Update filters & rules for NDA & stage3

**Bugfixes**

* String in button to step to 'Final Quote'
* Update label 'Sales Conditions'

**Build**

**Documentation**


10.0.11 (2017-04-12)
++++++++++++++++++++

**Features and Improvements**

* Update Lead, change place of fields and add buttons
* In SO: rename/move fields and tabs
* New permissions on project and tasks for salesman
* An employee can see only his contract
* Tasks are now named after project name and not the sales order name
* Ensure that the partner of a sale.order has a proper "reference" field

**Bugfixes**

* Set 'final_quote' after 'sent' & update checks & print to it

**Build**

* Updated odoo/src & removed 'update base'

**Documentation**


10.0.10 (2017-03-30)
++++++++++++++++++++

**Features and Improvements**

* Add link inbetween 'BOM' and 'project.task / project.project'
* Add fields in views for 'BOM' and 'project.task'
* Add smartbutton on 'task' view
* install instrastat modules, product harmonized system
* Update message subtypes for RFQ so that the author receives some additional
  notification

**Bugfixes**

* Fix base.action.rules for crm.lead transition not only for admin

**Build**

**Documentation**


10.0.9 (2017-03-23)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* Correct sale validation group names
* fix missing ACLs for hr.employee.status
* fix sale order validation workflow

**Build**

**Documentation**


10.0.8 (2017-03-17)
+++++++++++++++++++

**Features and Improvements**

* Add a second user on CRM leads
* Ghosts products and indicative sales quotes: have placeholder products on
  sale orders, and have an intermediate state on sales quotations.
* install sale_order_revision


10.0.7 (2017-03-10)
+++++++++++++++++++

**Features and Improvements**

* Add new fields in 'hr.employee' & 'hr.contracts'
* Update submodule hr
* Install 'hr_employee_phone_extension'
* Install hr_emergency_contact
* Install hr_contract_reference
* Install hr_employee_birth_name
* Install hr_experience
* Install hr_seniority
* Activate PO Double validation
* Add PO double validation view filters & security
* Add Check analytic account in PO validation
* Activate lots and serial number
* Change sequence for 'stock.production.lot'
* Add SN in PO report
* Install dropshipping
* Install FEDEX delivery
* Install sales layout and product set

**Bugfixes**

**Build**

**Documentation**


10.0.6 (2017-03-02)
+++++++++++++++++++

**Features and Improvements**

* Activate PO Double validation
* Add PO double validation view filters & security
* Add Check analytic account in PO validation
* Activate lots and serial number


10.0.5 (2017-02-21)
+++++++++++++++++++

**Features and Improvements**

* users with correct groups (taken from integration instance)
* install ``hr_maintenance`` and ``maintenance`` modules

**Bugfixes**

**Build**

**Documentation**


10.0.4 (2017-02-16)
+++++++++++++++++++

**Features and Improvements**

* Add product options on SO
* Configure margin on SO
* Install ``sale_order_revision``
* Install modules to manage margins on sale
* Install COA for Japan (Odoo fixed)
* Configure Base action rules, filters and server actions to be able to block
    or trigger actions when changing stage
* Manage option lines on sale orders


10.0.3 (2017-01-24)
+++++++++++++++++++

**Features and Improvements**

* import products


10.0.1 (2017-01-11)
+++++++++++++++++++

*Features and Improvements*

* initial setup
