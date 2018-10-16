# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "BSO Telephony",
    "summary": "BSO specific telephony",
    "version": "10.0.1.0.0",
    "category": "Phone",
    "website": "https://www.camptocamp.com",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "asterisk_click2dial",
    ],
    "data": [
        "views/res_users.xml",
    ],
}
