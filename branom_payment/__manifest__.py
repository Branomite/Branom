{
    'name': "Branom: Discounted Payment Values and Credits",

    'summary': """
        Branom: Discounted Payment Values and Credits""",

    'description': """
Task Spec[2153456]:
1.1 Adjusted Default Payment Value
When clicking on the “Register Payment” button, the “Payment Amount” field on the pop-up wizard defaults to the remaining amount due on the invoice/vendor bill. Branom would like this field to default to the remaining amount due, but with an adjusting calculation with respect to the discount value on the payment terms. 
1.2 Stored Field for Discount Taken on Invoice
The user registers a payment on an invoice and inputs a “Payment Amount” value that is lower than the amount due on the invoice. This prompts the wizard to display several other fields to determine whether the remaining amount due should be kept open (to be paid later) or written off (normally, as a discount taken). For Branom’s purposes, when they pay an amount lower than the invoice total, and write the remainder off as a discount, they need this value to be stored somewhere on the invoice/bill itself. They need to print checks that display the discounted amount from the invoice to notify their partners that a discount was in fact taken. 
1.3 Store Credit Note Information on Associated Payment
Similar to the need expressed in the last section, Branom needs to display the credit notes taken on each invoice/bill. 
    """,

    'author': "Odoo",
    'website': "http://www.odoo.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'account_accountant',
        'account_payment',
        'sale_management',
        'account_payment_disperse',
        'account_check_printing',
        'l10n_us_check_printing',
    ],

    # always loaded
    'data': [
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
        'views/account_portal_templates.xml',
        'views/product_views.xml',
        'views/print_check_reports.xml',
    ],

}
