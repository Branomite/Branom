# -*- coding: utf-8 -*-
{
    'name': "Branom: Sale Workflow Adjustment for Commission Sales",

    'summary': """
        Branom's development for change in Sale workflow for Sales of the Commission Type.""",

    'description': """
        Task Spec[2009294]:

        1. Prevent the triggering of the procurement process for sales marked as "commission sales"

        2. Bring the customer pricelist functionality to invoices as well

        3. Adjust the unit price on invoice lines automatically
    """,

    'author': "Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock', 'account', 'product'],

    # always loaded
    'data': [
        'views/sale_order_views.xml',
        'views/account_invoice_views.xml',
        'views/price_list_views.xml',
    ],

}
