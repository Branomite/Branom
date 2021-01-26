{
    'name': 'Branom MIG',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'version': '13.0.1.0.0',
    'category': 'RMA',
    'description': """
Various migration methods to move data for various models.
    """,
    'website': 'https://hibou.io/',
    'depends': [
        'sale_management',
    ],
    'data': [
        'data/scheduled_actions.xml',
        'data/server_actions.xml',
    ],
    'installable': True,
    'application': False,
}
