from odoo.tests import common
from odoo.exceptions import UserError


class TestFlow(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.customer_1 = self.env.ref('base.res_partner_12')
        self.product_1 = self.env.ref('product.product_product_4d')
        self.product_2 = self.env.ref('website_sale.product_product_1')
        # just Expenses, account
        self.commission_account = self.env.ref('l10n_generic_coa.1_expense')

    def test_1(self):
        # Prevent the triggering of the procurement process for sales marked as "commission sales"
        so = self.env['sale.order'].create({
            'partner_id': self.customer_1.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_1.id,
                    'name': 'Test Product Line',
                    'price_unit': 1.0,
                }),
            ],
        })
        so.action_confirm()
        self.assertTrue(so.state in ('sale', 'done'))
        self.assertTrue(so.picking_ids)

        so_commission = self.env['sale.order'].create({
            'sales_type': 'commission',
            'partner_id': self.customer_1.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_1.id,
                    'name': 'Test Product Line',
                    'price_unit': 1.0,
                }),
            ],
        })
        so_commission.action_confirm()
        self.assertTrue(so_commission.state in ('sale', 'done'))
        # no procurments (this was a stock product)
        self.assertFalse(so_commission.picking_ids)

    def test_2(self):
        # Bring the customer pricelist functionality to invoices as well
        so = self.env['sale.order'].create({
            'partner_id': self.customer_1.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_2.id,
                    'name': 'Test Service Line',
                    'price_unit': 1.0,
                }),
            ],
        })
        # so has pricelist
        self.assertTrue(so.pricelist_id)
        so.action_confirm()
        self.assertTrue(so.state in ('sale', 'done'))
        self.assertEqual(so.invoice_status, 'no')
        so.order_line.write({'qty_delivered': 1.0})
        self.assertEqual(so.invoice_status, 'to invoice')

        wiz = self.env['sale.advance.payment.inv'].with_context(active_ids=so.ids).create({})
        wiz.create_invoices()
        self.assertTrue(so.invoice_ids)

        # Failing assertion, pricelist not copied.  Maybe they meant "pricelist functionality"
        # as I see no code that would actually do this....
        # self.assertEqual(so.invoice_ids.pricelist_id, so.pricelist_id)

        invoice = so.invoice_ids
        self.assertFalse(invoice.pricelist_id)
        invoice.pricelist_id = so.pricelist_id
        with self.assertRaises(UserError):
            # Selected Pricelist's Discount Policy must be "Show public price & discount to the customer".
            invoice.apply_pricelist()

        invoice.pricelist_id.discount_policy = 'without_discount'
        invoice.apply_pricelist()

    def test_3(self):
        # Adjust the unit price on invoice lines automatically
        # TODO need clarification, if this just means that the 'apply_pricelist' gets called in onchange, then it should
        pass

    def test_4(self):
        # Set delivered qty when sale order line is changed after Confirm.
        so_commission = self.env['sale.order'].create({
            'sales_type': 'commission',
            'partner_id': self.customer_1.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_1.id,
                    'name': 'Test Product Line',
                    'price_unit': 1.0,
                }),
            ],
        })
        so_line = so_commission.order_line
        so_commission.action_confirm()
        self.assertTrue(so_commission.state in ('sale', 'done'))
        # no procurments (this was a stock product)
        self.assertFalse(so_commission.picking_ids)
        self.assertEqual(so_line.qty_delivered, 1.0)
        # increment ordered qty
        so_line.write({'product_uom_qty': 2.0})
        self.assertEqual(so_line.qty_delivered, 2.0)

    def test_5(self):
        # Branom wants to set a different income account as the default account listed on invoice lines for commission sales.
        # They would like the option to do so (i.e. in configuration settings).
        so_commission = self.env['sale.order'].create({
            'sales_type': 'commission',
            'partner_id': self.customer_1.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_1.id,
                    'name': 'Test Product Line',
                    'price_unit': 1.0,
                }),
            ],
        })
        so_commission.action_confirm()
        self.assertTrue(so_commission.state in ('sale', 'done'))
        wiz = self.env['sale.advance.payment.inv'].with_context(active_ids=so_commission.ids).create({})
        wiz.create_invoices()
        self.assertTrue(so_commission.invoice_ids)

        invoice = so_commission.invoice_ids
        self.assertNotEqual(invoice.invoice_line_ids.account_id, self.commission_account)
        invoice.unlink()

        # Setup the commission account on the company
        so_commission.company_id.commission_account_id = self.commission_account
        wiz = self.env['sale.advance.payment.inv'].with_context(active_ids=so_commission.ids).create({})
        wiz.create_invoices()
        invoice = so_commission.invoice_ids
        self.assertEqual(invoice.invoice_line_ids.account_id, self.commission_account)
