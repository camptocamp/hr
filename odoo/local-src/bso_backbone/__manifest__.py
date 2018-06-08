{
    'name': 'BSO Backbone',
    # 'category': 'Placeholder',
    'description': 'Backbone Links, Devices, POPs & XConnects',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/actions/act_window.xml',
        'views/menus/menuitem.xml',
        'views/backbone_device.xml',
        'views/backbone_link.xml',
        'views/backbone_pop.xml',
        'views/backbone_xco.xml',
    ],
    'application': True,
}
