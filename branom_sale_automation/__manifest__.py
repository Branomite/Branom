{
    'name': 'Branom Sale Automation',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'description': """
Customizations and automations for sales
    """,
    'website': 'https://hibou.io/',
    'depends': [
        'delivery',
        'sale',
        # to fully utilize:
        # 'sale_automatic_workflow',
    ],
    'data': [
        'data/automatic_workflow_data.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'application': False,
}
