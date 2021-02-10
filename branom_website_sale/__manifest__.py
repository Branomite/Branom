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
        'data/mail_data.xml',
        'data/service_request.xml',
        'views/account_portal_payment_templates.xml',
        'views/payment_templates.xml',
        'views/product_views.xml',
        'views/quick_order_templates.xml',
        'views/templates.xml',
        'views/save_products_templates.xml',
        'views/service_request_templates.xml',
        'views/web_assets.xml',
        'views/website_views.xml',
    ],
    'installable': True,
    'application': False,
}
