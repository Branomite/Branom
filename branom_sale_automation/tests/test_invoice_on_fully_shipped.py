from odoo.addons.sale.tests.test_sale_common import TestSale


class Test(TestSale):
    def setUp(self):
        super(Test, self).setUp()
        self.partner = self.env.ref('base.res_partner_12')
        self.product = self.env.ref('product.product_product_4d')
        self.product.invoice_policy = 'delivery'
        self.register_payments_model = self.env['account.payment.register']
        self.product_delivery = self.env.ref('delivery.product_product_delivery')
        # self.bank_journal_usd = self.env['account.journal'].create({'name': 'Bank US', 'type': 'bank', 'code': 'BNK68'})
        # self.payment_model = self.env['account.payment']
        # self.payment_method_manual_in = self.env.ref("account.account_payment_method_manual_in")

    def test_00_sale(self):
        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product.display_name,
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price,
                }),
                (0, 0, {
                    'name': self.product_delivery.display_name,
                    'product_id': self.product_delivery.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product_delivery.uom_id.id,
                    'price_unit': 0.0,
                    'is_delivery': True,
                }),
            ],
        })

        # confirm quotation
        so.action_confirm()
        self.assertIn(so.state, ('sale', 'done'))
        self.assertEqual(so.invoice_status, 'no', 'SO Should not be ready to invoice.')
        self.assertEqual(so.percent_delivered, 0.0, 'SO Should not be delivered.')

        # deliver
        self.assertTrue(so.picking_ids, 'Pickings should be created.')
        for pick in so.picking_ids:
            for line in pick.move_line_ids:
                line.qty_done = line.product_qty
            pick.action_done()
        self.assertEqual(so.percent_delivered, 100.0, 'SO Should be 100% delivered!')

        # Verify all lines were added.
        self.assertEqual(so.invoice_status, 'to invoice', 'SO Should be ready to invoice.')
        for line in so.order_line:
            self.assertEqual(line.invoice_status, 'to invoice', 'Line should be ready to invoice: %s' % (line.read(), ))

        context = {"active_model": "sale.order", "active_ids": [so.id], "active_id": so.id}
        so.with_context(context).action_confirm()
        #  create invoice.
        payment = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'delivered',
        })
        payment.with_context(context).create_invoices()
        # for invoice in so.invoice_ids:
        #     invoice.with_context(context).post()
        #     self.assertEqual(invoice.invoice_payment_state, 'not_paid')
        #     ctx = {'active_model': 'account.invoice', 'active_ids': [invoice.id]}
        #
        #     register_payments = self.register_payments_model.with_context(ctx).create({
        #         'payment_date': time.strftime('%Y') + '-07-15',
        #         'journal_id': self.bank_journal_usd.id,
        #         'payment_method_id': self.payment_method_manual_in.id,
        #     })
        #     register_payments.create_payments()
        #     payment = self.payment_model.search([], order="id desc", limit=1)
        #     self.assertIn(invoice.invoice_payment_state, ['in_payment', 'paid'])
        # self.assertEqual(so.is_paid, True)
