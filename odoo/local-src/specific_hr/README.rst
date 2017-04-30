HR Specifics
============


* new fields on hr.contracts, employees
* compute vacations (paid leaves and RTT) on a monthly basis (with a cron)
* customisation of hr holidays imposed to handle 1/2 days
* management of RTT holydays type


When a res.users is created from the LDAP, look for a matching employee (match
is on xmlid BSO_employee.<name> == user.<login>), if found link both.

Add a group bso_hr_confidential. Members of this group can access contract
data.
