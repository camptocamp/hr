# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Manage Disputed Supplier",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "category": "Accounting",
    "summary": "This module is useful to Manage Disputed Supplier.",
    "description": """
This module is useful to Manage Disputed Supplier. If any supplier supplies some damaged goods, late delivery, incomplete delivery that time you can create dispute and stop payment till not solve the problem using this module. This module provides one tab 'dispute' in vendor bill so you can create dispute directly. You can not make register payment till the dispute is not solved.
                    """,    
    "version":"12.0.1",
    "depends" : [
                    "base",
                    "account",
                ],
    "application" : True,
    "data" : [
        
                "data/ir_sequence_data.xml",
                'security/ir.model.access.csv',        
                "views/account_view.xml",  
                "views/dispute_view.xml",
            
            ],            
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 25,
    "currency": "EUR"   
}
