{
    'name': 'Branom Website RFQ',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'description': """
Customizations to website_sale to add quote request functionality
    """,
    'website': 'https://hibou.io/',
    'depends': [
        'crm',
        'sale',
        'website',
        'website_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_views.xml',
        'views/product_views.xml',
        'views/quote_request_template.xml',
        'views/sale_views.xml',
        'views/website_templates.xml',
        'views/web_assets.xml',
    ],
    'installable': True,
    'application': False,
}
