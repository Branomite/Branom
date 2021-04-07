# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}

# deprecated
# class AccountAbstractPayment(models.AbstractModel):
#     _inherit = 'account.abstract.payment'

#     @api.multi
#     def _compute_payment_amount(self, invoices=None, currency=None, with_discount=True):
#         if not with_discount:
#             return super(AccountAbstractPayment, self)._compute_payment_amount(invoices=invoices, currency=currency)

#         # Get the payment invoices
#         if not invoices:
#             invoices = self.invoice_ids

#         # Get the payment currency
#         payment_currency = currency
#         if not payment_currency:
#             payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or invoices and invoices[0].currency_id

#         # Avoid currency rounding issues by summing the amounts according to the company_currency_id before
#         invoice_datas = invoices.read_group(
#             [('id', 'in', invoices.ids)],
#             ['currency_id', 'type', 'residual_signed', 'residual_company_signed', 'amount_total_signed', 'amount_total_company_signed', 'payment_term_id', 'amount_discounted_signed', 'amount_discounted_company_signed', 'amount_undiscounted_signed', 'amount_undiscounted_company_signed'],
#             ['currency_id', 'type', 'payment_term_id'], lazy=False)
#         total = 0.0
#         for invoice_data in invoice_datas:
#             sign = MAP_INVOICE_TYPE_PAYMENT_SIGN[invoice_data['type']]
#             discount = 0.0
#             if invoice_data['payment_term_id']:
#                 payment_term = self.env['account.payment.term'].browse(invoice_data['payment_term_id'][0])
#                 discount = payment_term.discount

#             paid_total = sign * (invoice_data['amount_total_signed'] - invoice_data['residual_signed'])
#             paid_total_company = sign * (invoice_data['amount_total_company_signed'] - invoice_data['residual_company_signed'])
#             # if discount is 0.0, do we risk the float precision here?
#             amount_total = sign * invoice_data['amount_discounted_signed'] * (1.0 - discount) + sign * invoice_data['amount_undiscounted_signed'] - paid_total
#             amount_total_company_signed = sign * invoice_data['amount_discounted_company_signed'] * (1.0 - discount) + sign * invoice_data['amount_undiscounted_company_signed'] - paid_total_company
#             invoice_currency = self.env['res.currency'].browse(invoice_data['currency_id'][0])
#             if payment_currency == invoice_currency:
#                 total += amount_total
#             else:
#                 # Here there is no chance we will reconcile on amount_currency
#                 # Hence, we need to compute with the amount in company currency as the base
#                 total += self.journal_id.company_id.currency_id._convert(
#                     amount_total_company_signed,
#                     payment_currency,
#                     self.env.user.company_id,
#                     self.payment_date or fields.Date.today()
#                 )
#         return total
        
#     @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
#     def _compute_payment_difference(self):
#         super(AccountAbstractPayment, self)._compute_payment_difference()
#         for pay in self.filtered(lambda p: p.invoice_ids):
#             payment_amount = -pay.amount if pay.payment_type == 'outbound' else pay.amount
#             pay.payment_difference = pay._compute_payment_amount(with_discount=False) - payment_amount


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    refund_invoice_ids = fields.Many2many(comodel_name='account.move', string='Credit Notes', compute='_compute_refund_invoice_ids', inverse='_set_refund_invoice_ids', store=True, reaonly=False)

    @api.depends('invoice_ids')
    def _compute_refund_invoice_ids(self):
        for payment in self:
            payment.refund_invoice_ids = self.env['account.move']
            for invoice in payment.invoice_ids:
                for move_line in invoice.invoice_line_ids:
                    if move_line.payment_id:
                        payment.refund_invoice_ids |= move_line.move_id

    def _set_refund_invoice_ids(self):
        pass

    def post(self):
        res = super(AccountPayment, self).post()
        if res and self.payment_difference_handling == 'reconcile' and self.payment_difference:
            total = sum(self.invoice_ids.mapped('amount_total'))
            for invoice in self.invoice_ids:
                invoice.write({
                    'payment_difference': self.payment_difference * (invoice.amount_discounted_signed / total)
                })
        return res
