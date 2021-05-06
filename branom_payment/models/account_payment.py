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

    refund_invoice_ids = fields.Many2many(comodel_name='account.move', string='Credit Notes', compute='_compute_refund_invoice_ids')#, inverse='_set_refund_invoice_ids', store=True, reaonly=False)

    @api.depends('invoice_ids')
    def _compute_refund_invoice_ids(self):
        for payment in self:
            payment.refund_invoice_ids = self.env['account.move']
            for invoice in payment.invoice_ids:
                t = self.env['account.move'].browse([i['move_id'] for i in invoice._get_reconciled_info_JSON_values()])
                payment.refund_invoice_ids |= t.filtered(lambda i: i.type in ('in_refund', 'out_refund'))

    def post(self):
        res = super(AccountPayment, self).post()
        if res and self.payment_difference_handling == 'reconcile' and self.payment_difference:
            total = sum(self.invoice_ids.mapped('amount_discounted_signed'))
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

        # Avoid currency rounding issues by summing the amounts according to the company_currency_id before
        invoice_datas = invoices.read_group(
            [('id', 'in', invoices.ids)],
            ['currency_id', 'type', 'amount_residual', 'amount_residual_signed', 'amount_total', 'amount_total_signed', 'invoice_payment_term_id', 'amount_discounted_signed', 'amount_discounted_company_signed', 'amount_undiscounted_signed', 'amount_undiscounted_company_signed'],
            ['currency_id', 'type', 'invoice_payment_term_id'], lazy=False)

        total = 0.0
        for res in invoice_datas:
            discount = 0.0
            if res['invoice_payment_term_id']:
                payment_term = self.env['account.payment.term'].browse(res['invoice_payment_term_id'][0])
                # TODO: get discount from term lines based on date and remove manually-entered discount value
                discount = payment_term.discount

            sign = MAP_INVOICE_TYPE_PAYMENT_SIGN[res['type']]
            # Amounts in the invoice currency are not signed
            paid_total = sign * res['amount_total'] - sign * res['amount_residual']
            # Amounts in company currency are already signed
            paid_total_company = company.currency_id.round(res['amount_total_signed'] - res['amount_residual_signed'])
            # if discount is 0.0, do we risk the float precision here?
            amount_total = sign * res['amount_discounted_signed'] * (1.0 - discount) + sign * res['amount_undiscounted_signed'] - paid_total
            amount_total_company_signed = company.currency_id.round(sign * res['amount_discounted_company_signed'] * (1.0 - discount) + sign * res['amount_undiscounted_company_signed'] - paid_total_company)
            move_currency = self.env['res.currency'].browse(res['currency_id'][0])
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
