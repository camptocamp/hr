{
    'name': 'BSO Internal Tools Drawer',
    'description': '',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'web_kanban'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/internal_tool_views.xml',
        'views/assets_backend.xml',
        'views/internal_tool_tag_views.xml'
    ],
    'application': True,
}
