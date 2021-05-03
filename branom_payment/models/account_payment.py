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


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    discount = fields.Float(string='Term Calculation', help='Discount on Invoice', digits='Discount')

    @api.constrains('discount')
    def _check_discount_range(self):
        for term in self:
            if not (0.0 <= term.discount <= 1.0):
                raise ValidationError("Term discount must be in range [0.0, 1.0].")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # refund_invoice_ids = fields.Many2many(comodel_name='account.invoice', string='Credit Notes', compute='_compute_refund_invoice_ids', inverse='_set_refund_invoice_ids', store=True, reaonly=False)

    # @api.depends('invoice_ids', 'invoice_ids.refund_invoice_ids')
    # def _compute_refund_invoice_ids(self):
    #     for payment in self:
    #         payment.refund_invoice_ids = payment.invoice_ids.mapped('refund_invoice_ids') if payment.invoice_ids else False

    # def _set_refund_invoice_ids(self):
    #     pass

    def post(self):
        res = super(AccountPayment, self).post()
        if res and self.payment_difference_handling == 'reconcile' and self.payment_difference:
            total = sum(self.invoice_ids.mapped('amount_total'))
            for invoice in self.invoice_ids:
                invoice.write({
                    'payment_difference': self.payment_difference * (invoice.amount_discounted_signed / total)
                })
        return res

    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date, with_discount=True):
        '''Compute the total amount for the payment wizard.

        :param invoices:    Invoices on which compute the total as an account.invoice recordset.
        :param currency:    The payment's currency as a res.currency record.
        :param journal:     The payment's journal as an account.journal record.
        :param date:        The payment's date as a datetime.date object.
        :return:            The total amount to pay the invoices.
        '''

        if not with_discount:
            return super(AccountPayment, self)._compute_payment_amount(invoices, currency, journal, date)

        company = journal.company_id
        currency = currency or journal.currency_id or company.currency_id
        date = date or fields.Date.today()

        if not invoices:
            return 0.0

        self.env['account.move'].flush(['type', 'currency_id'])
        self.env['account.move.line'].flush(['amount_residual', 'amount_residual_currency', 'move_id', 'account_id'])
        self.env['account.account'].flush(['user_type_id'])
        self.env['account.account.type'].flush(['type'])
        self._cr.execute('''
                SELECT
                    move.type AS type,
                    move.currency_id AS currency_id,
                    move.invoice_payment_term_id AS payment_term_id,
                    move.amount_total_signed AS amount_total_company_signed,
                    move.amount_discounted_signed AS amount_discounted_signed,
                    move.amount_undiscounted_signed AS amount_undiscounted_signed,
                    move.amount_discounted_company_signed AS amount_discounted_company_signed,
                    move.amount_undiscounted_company_signed AS amount_undiscounted_company_signed,
                    SUM(line.price_total) AS amount_total_signed,
                    SUM(line.amount_residual) AS amount_residual,
                    SUM(line.amount_residual_currency) AS residual_currency
                FROM account_move move
                LEFT JOIN account_move_line line ON line.move_id = move.id
                LEFT JOIN account_account account ON account.id = line.account_id
                LEFT JOIN account_account_type account_type ON account_type.id = account.user_type_id
                WHERE move.id IN %s
                AND account_type.type IN ('receivable', 'payable')
                GROUP BY move.id, move.type
            ''', [tuple(invoices.ids)])
        query_res = self._cr.dictfetchall()

        total = 0.0
        for res in query_res:
            discount = 0.0
            if res['payment_term_id']:
                payment_term = self.env['account.payment.term'].browse(res['payment_term_id'])
                # TODO: get discount from term lines based on date and remove manually-entered discount value
                discount = payment_term.discount

            sign = MAP_INVOICE_TYPE_PAYMENT_SIGN[res['type']]
            paid_total = sign * (res['amount_total_signed'] - res['residual_currency'])
            paid_total_company = sign * (res['amount_total_company_signed'] - res['amount_residual'])
            # if discount is 0.0, do we risk the float precision here?
            amount_total = sign * res['amount_discounted_signed'] * (1.0 - discount) + sign * res['amount_undiscounted_signed'] - paid_total
            amount_total_company_signed = sign * res['amount_discounted_company_signed'] * (1.0 - discount) + sign * res['amount_undiscounted_company_signed'] - paid_total_company
            move_currency = self.env['res.currency'].browse(res['currency_id'])
            if move_currency == currency and move_currency != company.currency_id:
                total += amount_total
            else:
                total += company.currency_id._convert(amount_total_company_signed, currency, company, date)
        return total

    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'payment_type')
    def _compute_payment_difference(self):
        draft_payments = self.filtered(lambda p: p.invoice_ids and p.state == 'draft')
        for pay in draft_payments:
            payment_amount = -pay.amount if pay.payment_type == 'outbound' else pay.amount
            pay.payment_difference = pay._compute_payment_amount(pay.invoice_ids, pay.currency_id, pay.journal_id, pay.payment_date, with_discount=False) - payment_amount
        (self - draft_payments).payment_difference = 0
