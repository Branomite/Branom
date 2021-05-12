from odoo import api, fields
from odoo.tests import common


class TestPaymentDiscount(common.TransactionCase):

    def setUp(self):
        super().setUp()

        # Must patch new to fix the way Form creates new lines.
        # this is due to the way `account.move` saves/copies data to new lines
        from ..models.account_invoice import AccountMoveLine

        @api.model
        def new(self, values={}, origin=None, ref=None):
            res = super(AccountMoveLine, self).new(values=values, origin=origin, ref=ref)
            if origin:
                res.exclude_discount = origin.exclude_discount
            else:
                res.exclude_discount = values.get('exclude_discount',
                                                  res.product_id and res.product_id.exclude_discount)
            return res

        AccountMoveLine.new = new

        self.vendor = self.env.ref('base.res_partner_12')
        self.payment_term_2percent = self.env['account.payment.term'].create({
            'name': '2%10 Net 30',
            'line_ids': [
                (0, 0, {
                    'value': 'percent',
                    'value_amount': 2.0,
                    'days': 30,
                    'option': 'day_after_invoice_date',
                }),
                (0, 0, {
                    'value': 'balance',
                    'value_amount': 0.0,
                    'days': 10,
                    'option': 'day_after_invoice_date',
                }),
            ],
        })
        self.product_main = self.env['product.product'].create({
            'name': 'Main Product',
        })
        self.product_exclude = self.env['product.product'].create({
            'name': 'Exclude Discount Product',
            'exclude_discount': True,
        })

    def test_01_term_vendor_bill(self):
        move_form = common.Form(self.env['account.move'].with_context(default_type='in_invoice'))
        move_form.partner_id = self.vendor
        move_form.invoice_date = fields.Date.from_string('2021-01-01')
        move_form.date = fields.Date.from_string('2021-01-01')
        move_form.invoice_payment_term_id = self.payment_term_2percent
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_main
            line_form.quantity = 1.0
            line_form.price_unit = 70.0
            line_form.tax_ids.remove(index=0)
            self.assertFalse(line_form.exclude_discount)
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_exclude
            line_form.quantity = 1.0
            line_form.price_unit = 30.0
            line_form.tax_ids.remove(index=0)
            self.assertTrue(line_form.exclude_discount)
        invoice = move_form.save()

        # We have an even $100 invoice, but only one product is 'eligible' for discount
        self.assertEqual(invoice.amount_total, 100.0)
        ap_lines = (invoice.line_ids - invoice.invoice_line_ids).sorted('credit')
        self.assertEqual(len(ap_lines), 2)
        self.assertEqual(ap_lines[0].credit, 1.4)  # 2% of 70.0
        self.assertEqual(ap_lines[1].credit, 98.6)  # balance
