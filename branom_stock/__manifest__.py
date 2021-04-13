{
    'name': 'Branom Stock',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'category': 'Hidden',
    'version': '13.0.1.0.0',
    'description':
        """
Customizations to Stock Module Functionality
===================

Sets the delivery carrier service type and carrier on stock picking on creation
        """,
    'depends': [
        'stock',
        'delivery_ups',
    ],
    'auto_install': False,
    'data': [
        'report/report_deliveryslip.xml',
        'views/delivery_views.xml',
    ],
}
