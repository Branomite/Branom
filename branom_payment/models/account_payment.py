from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date
from odoo.addons.account_check_printing.models import account_payment

# our checks do not have two stub pages
INV_LINES_PER_STUB = account_payment.INV_LINES_PER_STUB * 2
account_payment.INV_LINES_PER_STUB = INV_LINES_PER_STUB


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    refund_invoice_ids = fields.Many2many(comodel_name='account.move', string='Credit Notes', compute='_compute_refund_invoice_ids')

    # recompute amount in words if missing
    def do_print_checks(self):
        if self:
            check_layout = self[0].company_id.account_check_printing_layout
            # A config parameter is used to give the ability to use this check format even in other countries than US, as not all the localizations have one
            if check_layout != 'disabled' and (self[0].journal_id.company_id.country_id.code == 'US' or bool(self.env['ir.config_parameter'].sudo().get_param('account_check_printing_force_us_format'))):
                values = {'state': 'sent'}
                if not self.check_amount_in_words:
                    values['check_amount_in_words'] = self.currency_id.amount_to_text(self.amount)
                self.write(values)
                return self.env.ref('l10n_us_check_printing.%s' % check_layout).report_action(self)
        return super().do_print_checks()

    @api.depends('invoice_ids')
    def _compute_refund_invoice_ids(self):
        for payment in self:
            payment.refund_invoice_ids = self.env['account.move']
            for invoice in payment.invoice_ids:
                t = self.env['account.move'].browse([i['move_id'] for i in invoice._get_reconciled_info_JSON_values()])
                payment.refund_invoice_ids |= t.filtered(lambda i: i.type in ('in_refund', 'out_refund'))

    # Override to provide a calculated amount
    # Must override all the places that automatically calculate it
    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            if self.journal_id.currency_id:
                self.currency_id = self.journal_id.currency_id

            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            payment_methods_list = payment_methods.ids

            default_payment_method_id = self.env.context.get('default_payment_method_id')
            if default_payment_method_id:
                # Ensure the domain will accept the provided default value
                payment_methods_list.append(default_payment_method_id)
            else:
                self.payment_method_id = payment_methods and payment_methods[0] or False

            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'

            domain = {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods_list)]}

            if self.env.context.get('active_model') == 'account.move':
                active_ids = self._context.get('active_ids')
                invoices = self.env['account.move'].browse(active_ids)
                # the onchange here re-computes the aount, which means the amount from the default_get is only used in
                # tests or things that wouldn't immediately call this onchange...
                if len(invoices) == 1 and invoices.type == 'in_invoice':
                    residual, amount = self._compute_payment_residual_and_amount(invoices)
                    self.amount = abs(amount)
                else:
                    self.amount = abs(self._compute_payment_amount(invoices, self.currency_id, self.journal_id, self.payment_date))

            return {'domain': domain}
        return {}

    # Override to provide a calculated amount
    # Must override all the places that automatically calculate it
    @api.onchange('currency_id')
    def _onchange_currency(self):
        if len(self.invoice_ids) == 1 and self.invoice_ids.type == 'in_invoice':
            residual, amount = self._compute_payment_residual_and_amount(self.invoice_ids)
            self.amount = abs(amount)
        else:
            self.amount = abs(self._compute_payment_amount(self.invoice_ids, self.currency_id, self.journal_id, self.payment_date))

        if self.journal_id:  # TODO: only return if currency differ?
            return

        # Set by default the first liquidity journal having this currency if exists.
        domain = [('type', 'in', ('bank', 'cash')), ('currency_id', '=', self.currency_id.id)]
        if self.invoice_ids:
            domain.append(('company_id', '=', self.invoice_ids[0].company_id.id))
        journal = self.env['account.journal'].search(domain, limit=1)
        if journal:
            return {'value': {'journal_id': journal.id}}

    def _compute_payment_residual_and_amount(self, invoice):
        dummy_date = fields.Date.from_string('1980-01-01')

        sign = 1.0 if invoice.type in ('out_invoice', 'out_refund') else -1.0
        residual = sign * invoice.amount_residual_signed

        total_amount = 0.0
        total_reconciled = 0.0

        move_lines = invoice.line_ids.filtered(lambda r: (
                not r.reconciled
                and r.account_id.internal_type in ('payable', 'receivable')
                )).sorted(key=lambda r: r.date_maturity or dummy_date)
        if move_lines:
            move_line = move_lines[0]
            amount = move_line.debit - move_line.credit
            total_amount += amount
            for partial_line in move_line.matched_debit_ids:
                total_reconciled -= partial_line.amount
            for partial_line in move_line.matched_credit_ids:
                total_reconciled += partial_line.amount

        return residual, total_amount - total_reconciled

    def _check_make_stub_pages(self):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(self.reconciled_invoice_ids) == 0:
            return None

        multi_stub = self.company_id.account_check_printing_multi_stub

        invoices = self.reconciled_invoice_ids.sorted(key=lambda r: r.invoice_date_due or fields.Date.context_today(self))
        debits = invoices.filtered(lambda r: r.type == 'in_invoice')
        credits = invoices.filtered(lambda r: r.type == 'in_refund') + self.refund_invoice_ids

        # Prepare the stub lines
        if not credits:
            stub_lines = [self._check_make_stub_line(inv) for inv in invoices]
        else:
            stub_lines = [{'header': True, 'name': "Bills"}]
            stub_lines += [self._check_make_stub_line(inv, self.refund_invoice_ids) for inv in debits]
            stub_lines += [{'header': True, 'name': "Refunds"}]
            stub_lines += [self._check_make_stub_line(inv, self.refund_invoice_ids) for inv in credits]

        # Crop the stub lines or split them on multiple pages
        if not multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                if len(stub_lines) >= i + INV_LINES_PER_STUB and stub_lines[i + INV_LINES_PER_STUB - 1].get('header'):
                    num_stub_lines = INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
                else:
                    num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i + num_stub_lines])
                i += num_stub_lines

        return stub_pages

    def _check_make_stub_line(self, invoice, refund_invoice_ids):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in self.move_line_ids or r.debit_move_id.move_id in refund_invoice_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in self.move_line_ids or r.credit_move_id.move_id in refund_invoice_ids)

        invoice_payment_discount = None
        if len(invoice_payment_reconcile) >= 2:
            invoice_payment_discount = invoice_payment_reconcile.sorted(lambda p: abs(p.amount))[0]
            invoice_payment_reconcile = invoice_payment_reconcile - invoice_payment_discount
        amount_discount_taken = 0.0

        if self.currency_id != self.journal_id.company_id.currency_id:
            if invoice_payment_discount:
                amount_discount_taken = -abs(sum(invoice_payment_discount.mapped('amount_currency')))
            if invoice in refund_invoice_ids:
                # note that invoice does not have an equivilent to 'amount_currency'
                amount_paid = abs(invoice.amount_total)
            else:
                amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            if invoice_payment_discount:
                amount_discount_taken = -abs(sum(invoice_payment_discount.mapped('amount')))
            if invoice in refund_invoice_ids:
                amount_paid = abs(invoice.amount_total)
            else:
                amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        amount_residual = invoice_sign * invoice.amount_residual

        return {
            'due_date': format_date(self.env, invoice.invoice_date_due),
            'date': format_date(self.env, invoice.invoice_date),
            # 'number': invoice.ref and invoice.name + ' - ' + invoice.ref or invoice.name,
            'number': invoice.ref or invoice.name,
            'desc': invoice.invoice_origin or '',
            'amount_total': formatLang(self.env, invoice_sign * invoice.amount_total, currency_obj=invoice.currency_id),
            'amount_residual': formatLang(self.env, amount_residual, currency_obj=invoice.currency_id) if amount_residual * 10**4 != 0 else '-',
            'amount_discount_taken': formatLang(self.env, invoice_sign * amount_discount_taken, currency_obj=self.currency_id) if amount_discount_taken * 10**4 != 0 else '-',
            'amount_paid': formatLang(self.env, invoice_sign * amount_paid, currency_obj=self.currency_id),
            'currency': invoice.currency_id,
        }


class AccountRegisterPayments(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.onchange('is_manual_disperse')
    def _ensure_is_manual_disperse(self):
        super()._ensure_is_manual_disperse()
        # Automation based on invoice type.
        # Desired to have as little of interaction as possible.
        for payment in self.filtered(lambda p: p.is_manual_disperse and p.invoice_ids and p.invoice_ids[0].type in ('in_invoice', 'in_refund')):
            payment.due_date_behavior = 'next_due'
            payment.action_fill_residual_due()
            payment.action_toggle_close_balance()
