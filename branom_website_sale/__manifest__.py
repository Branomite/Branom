{
    'name': 'Branom Website Sale',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'description': """
Customizations to website_sale
    """,
    'website': 'https://hibou.io/',
    'depends': [
        'crm',
        'sale',
        'website_sale',
        'website_sale_wishlist',
    ],
    'data': [
        'views/quick_order_templates.xml',
        'views/save_products_templates.xml',
        'views/web_assets.xml',
    ],
    'installable': True,
    'application': False,
}
