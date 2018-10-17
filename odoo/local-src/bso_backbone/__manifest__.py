{
    'name': 'BSO Backbone',
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
        'views/actions/actions.xml',
        'views/menus/menuitem.xml',
        'views/backbone_device.xml',
        'views/backbone_link.xml',
        'views/backbone_pop.xml',
        'views/backbone_xco.xml',
        'views/backbone_cympa_link.xml',
        'data/backbone_cympa_link_data.xml',
        'views/backbone_settings.xml',
    ],
    'application': True,
}
