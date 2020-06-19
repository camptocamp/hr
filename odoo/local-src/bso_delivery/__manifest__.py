{
    'name': 'BSO Delivery',
    'category': 'Delivery',
    'description': 'BSO Service Delivery',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'bso_dealsheet',
        'bso_connector_jira',
        'sale',
        'website',
        'bso_pop_up_message'
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/actions/act_window.xml',
        'views/menus/menuitem.xml',
        'views/delivery_project.xml',
        'views/sale_order.xml',
        'views/backend_assets.xml',
        'views/checklist_view.xml',
        'views/reports/delivery_report.xml',
        'views/reports/delivery_report_file.xml',
        'data/email_template.xml',
        'views/jira_product_template_view.xml',
        'views/delivery_project_line_view.xml'
    ],
    'application': True,
}
