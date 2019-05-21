{
    'name': 'BSO Sales Forecast',
    'category': 'sales',
    'description': 'Sales Forecast',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'mail', 'sale_contract', 'bso_purchase',
                # 'bso_mis_builder',
                # 'currency_monthly_rate',
                'specific_sale',
                # 'account',
                ],
    'data': [
        'security/bso_sales_forecast_security.xml',
        'security/ir.model.access.csv',
        'data/forecast_report_data.xml',
        'views/forecast_report.xml',
        'views/forecast_line_revenue.xml',
        'views/forecast_month.xml',
        'views/forecast_line_cost.xml',
        'views/forecast_line_manual.xml',
        'views/forecast_line_invoice.xml',
        'views/forecast_line_diff.xml',
        'views/sale_subscription.xml',
        'views/menuitem.xml',
    ],
    'application': True,
}
