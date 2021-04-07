{
    'name': 'Branom Shipping Weight',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'description': """
Edit product weight on sale order and delivery.
    """,
    'website': 'https://hibou.io/',
    'depends': [
        'sale',
        'stock',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/stock_views.xml',
    ],
    'installable': True,
    'application': False,
}
