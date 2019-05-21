{
    'name': 'BSO MIS builder',
    'description': 'Extend MIS builder & add redirection to details '
                   'in case of kpi based on query',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'mis_builder',
                'bso_sales_forecast'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/mis_report.xml',
    ],
    'qweb': [
        "static/src/xml/mis_widget.xml",
    ],
    'application': False,
}
