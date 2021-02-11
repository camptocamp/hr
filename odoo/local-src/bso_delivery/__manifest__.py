{
    'name': 'BSO Delivery',
    'description': 'BSO Service Delivery',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'bso_dealsheet',
        'bso_connector_jira',
        'sale',
        'website',
        'bso_pop_up_message',
        'stock',
        'purchase',
        'bso_subscription_cease',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'views/delivery_project.xml',
        'views/so_delivery_project.xml',
        'views/sale_order.xml',
        'views/checklist_view.xml',
        'views/jira_product_template_view.xml',
        'views/delivery_project_line_view.xml',
        'views/po_delivery_project.xml',
        'views/po_delivery_line.xml',
        'views/purchase_order_form.xml',
        'views/delivery_choose_line_wizard_view.xml',
        'views/backend_assets.xml',
        'views/so_delivery_line_view.xml',

        'views/actions/act_window.xml',
        'views/menus/menuitem.xml',

        'views/reports/handover_report.xml',
        'views/reports/factsheet_report.xml',
        'views/reports/delivery_report.xml',
        'data/email_template.xml',

    ],
    'application': True,
}
