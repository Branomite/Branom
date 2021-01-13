from odoo import api, fields, models
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.tools import float_compare
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _check_amount_and_invoice_ids_sum_equality(self, amount, invoice_ids):
        invoice_amount = 0

        for i in invoice_ids:
            precision = self.env['decimal.precision'].precision_get('Account')
            invoice = self.env['account.move'].browse(int(i))
            invoice.exists()
            invoice_amount += invoice.amount_residual

        if not float_compare(amount, invoice_amount, precision_rounding=precision) == 0:
            raise UserError('Invalid Amount')

    @api.model
    def get_partner_credit_amount(self, data):
        partner = self.env['res.partner'].sudo().browse(int(data['partner_id']))
        if partner.parent_id:
            return partner.parent_id.credit
        else:
            return partner.credit

    @api.model
    def create_account_payment(self, data):
        # Data values from payment.js
        amount = data['amount']
        partner_id = data['partner_id']
        token_id = data['token_id']
        payment_name = data['payment_name']
        memo = data['memo']
        website_id = data['website_id']
        invoice_ids = data['invoice_ids']
        payment_type = data['payment_type']

        # Sanitize Data from JS
        amount = float(amount)
        partner_id = int(partner_id)
        token_id = int(token_id)
        website_id = int(website_id)

        # get requested website
        website = self.env['website'].browse(website_id)

        # Get current partner
        partner = self.env['res.partner'].browse(partner_id)
        if self.env.user.partner_id != partner:
            raise UserError('Invalid data.')

        # Enter Sudo
        self = self.sudo()
        payment_token = self.env['payment.token'].browse(token_id)
        acquirer = payment_token.acquirer_id
        journal = acquirer.journal_id
        payment_method = payment_token.acquirer_id.inbound_payment_method_ids.filtered(
            lambda pm: pm.code == 'electronic')
        company = journal.company_id

        if not all((partner, payment_token, acquirer, journal, payment_method, company)):
            raise UserError('Invalid data.')

        if partner != payment_token.partner_id:
            raise UserError('Invalid token.')

        # Handle for custom arbitrary payments
        if payment_type == 'custom':

            payment = self.env['account.payment'].create({
                'amount': amount,
                'company_id': company.id,
                'currency_id': company.currency_id.id,
                'journal_id': journal.id,
                'partner_id': partner.id,
                'payment_token_id': payment_token.id,
                'partner_type': 'customer',
                'payment_date': fields.Date.today(),
                'payment_type': 'inbound',
                'payment_method_id': payment_method.id,
                'payment_reference': payment_name,
                'communication': memo,
            })

            # Post Payment
            payment.post()
            # Try to Force Process Payment
            try:
                payment.payment_transaction_id._post_process_after_done()
            except:
                pass

            # Create scheduled activity for transaction
            if website.website_payment_reviewer_id:
                try:
                    # hardcoded user id, allow any exception
                    self.env['mail.activity'].create({
                        'date_deadline': fields.Date.today(),
                        'user_id': website.website_payment_reviewer_id.id,
                        'res_id': payment.partner_id.id,
                        'res_model_id': self.env.ref('base.model_res_partner').id,
                        'summary': 'New Payment for Review',
                    })
                except:
                    pass

            return payment.id

        # Handle for multi invoice payments
        elif payment_type == 'invoice':
            # Verify amount match before proceeding
            self._check_amount_and_invoice_ids_sum_equality(amount, invoice_ids)
            for i in invoice_ids:
                # Check invoice existence
                invoice = self.env['account.move'].browse(int(i))
                invoice.exists()
                if not invoice:
                    raise UserError('Invalid invoice.')

                vals = {
                    'currency_id': company.currency_id.id,
                    'partner_id': partner.id,
                    'payment_token_id': payment_token.id,
                    'invoice_ids': [(6, 0, invoice.id)],
                }

                transaction = invoice._create_payment_transaction(vals)
                PaymentProcessing.add_payment_transaction(transaction)
                transaction._post_process_after_done()

            return invoice_ids

        else:
            return {'Warning': 'Payment could not be processed'}