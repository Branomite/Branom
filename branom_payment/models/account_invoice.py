# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    payment_difference = fields.Monetary(string='Payment Difference', help="Payment difference in invoice's currency.", copy=False)
    amount_discounted_signed = fields.Monetary(string='To Be Discounted Amount in Invoice Currency', currency_field='currency_id',
        compute='_compute_amount_with_discount', store=True)
    amount_discounted_company_signed = fields.Monetary(string='To Be Discounted Amount in Company Currency', currency_field='company_currency_id',
        compute='_compute_amount_with_discount', store=True)
    # surely it's debatable if we need these two fields, 
    # but I would rather keep them in case for easy debugging in the future
    # plus it makes the payment computation much easier later
    amount_undiscounted_signed = fields.Monetary(string='Undiscounted Amount in Invoice Currency', currency_field='currency_id',
        compute='_compute_amount_with_discount', store=True)
    amount_undiscounted_company_signed = fields.Monetary(string='Undiscounted Amount in Company Currency', currency_field='company_currency_id',
        compute='_compute_amount_with_discount', store=True)

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.exclude_discount',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount_with_discount(self):
        round_curr = self.currency_id.round
        # discounted here means to be discounted, sorry future devs
        discounted, undiscounted = sum(line.price_total for line in self.invoice_line_ids.filtered(lambda l: not l.exclude_discount)), sum(line.price_total for line in self.invoice_line_ids.filtered(lambda l: l.exclude_discount))

        amount_discounted_company, amount_undiscounted_company = discounted, undiscounted
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_discounted_company = currency_id._convert(discounted, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
            amount_undiscounted_company = currency_id._convert(undiscounted, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
        
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_discounted_company_signed = amount_discounted_company * sign
        self.amount_undiscounted_company_signed = amount_undiscounted_company * sign                                                                                        
        self.amount_discounted_signed = discounted * sign
        self.amount_undiscounted_signed = undiscounted * sign            

    
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    exclude_discount = fields.Boolean('Exclude Discount')

    @api.model
    def create(self, vals):
        rids = super(AccountInvoiceLine, self).create(vals)
        for rid in rids:
            rid.exclude_discount = rid.product_id.exclude_discount  # cannot call onchange product id since it will pull the original price for products
        return rids

    @api.onchange('product_id')
    def _onchange_product_id(self):
        vals = super(AccountInvoiceLine, self)._onchange_product_id()
        self.exclude_discount = self.product_id.exclude_discount  # not using compute so that we only pull this info once
        return vals
