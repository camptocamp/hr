{
    'name': 'BSO Delivery',
    # 'category': 'Placeholder',
    'description': 'BSO Service Delivery',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'bso_dealsheet',
        'connector_jira',
        'sale'
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/actions/act_window.xml',
        'views/menus/menuitem.xml',
        'views/delivery_project.xml',
        'views/sale_order.xml',
    ],
    'application': True,
}
