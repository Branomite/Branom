{
    'name': 'Branom Website Partner Delivery',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'description': """
Allow clients to manage their own shipping accounts in the portal
    """,
    'website': 'https://hibou.io/',
    'depends': [
        'delivery_partner',
        'delivery_partner_dhl',
        'delivery_partner_fedex',
        'delivery_partner_ups',
    ],
    'data': [
        'views/shipping_accounts_templates.xml',
        'views/website_templates.xml',
        'views/web_assets.xml',
        'views/website_sale_templates.xml',
    ],
    'installable': True,
    'application': False,
}
