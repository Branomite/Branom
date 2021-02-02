import json
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route


class WebsiteSalePortalAccountPayment(http.Controller):
    @route('/my/account/portal_payment', type='http', auth='public', website=True)
    def website_account_portal_payment(self, **kwargs):
        acquirers = list(request.env['payment.acquirer'].search([
            ('state', 'in', ['enabled', 'test']), ('registration_view_template_id', '!=', False),
            ('payment_flow', '=', 's2s'), ('company_id', '=', request.env.company.id)
        ]))
        partner = request.env.user.partner_id
        payment_tokens = partner.payment_token_ids
        payment_tokens |= partner.commercial_partner_id.sudo().payment_token_ids
        return_url = request.params.get('redirect', '/my/account/portal_payment')
        website = request.website
        AccountInvoice = request.env['account.move']

        domain = [('partner_id', '=', partner.id),
                  ('state', '=', 'posted'),
                  ('invoice_payment_state', '!=', 'paid'),
                  ('type', 'in', ('out_invoice', 'in_invoice'))]

        invoices = AccountInvoice.search(domain)
        request.session['my_invoices_history'] = invoices.ids[:100]
        values = {
            'pms': payment_tokens,
            'acquirers': acquirers,
            'error_message': [kwargs['error']] if kwargs.get('error') else False,
            'return_url': return_url,
            'bootstrap_formatting': True,
            'partner_id': partner.id,
            'website_id': website.id,
            'invoices': invoices,
            'page_name': 'invoice',
            'default_url': '/my/invoices',
        }

        return request.render('branom_website_sale.make_account_portal_payment', values)


class PortalAccountPayments(CustomerPortal):

    def get_user_payments(self):
        partner = request.env.user.partner_id
        partner_payments = request.env['account.payment'].sudo().search([('partner_id', '=', partner.id),
                                                                         ('state', 'not in', ('draft', 'cancelled'))])

        return partner_payments

    def _prepare_portal_layout_values(self):
        values = super(PortalAccountPayments, self)._prepare_portal_layout_values()
        payments = self.get_user_payments()
        payments_count = 0
        if payments:
            payments_count = len(payments)
        values['payments_count'] = payments_count

        return values

    @route(['/my/payments', '/my/payments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payments(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AccountPayment = request.env['account.payment']

        domain = [('partner_id', '=', partner.id)]

        searchbar_sortings = {
            'date': {'label': _('Payment Date'), 'order': 'payment_date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('account.move', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        payment_count = AccountPayment.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/payments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=payment_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        payments = AccountPayment.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_payments_history'] = payments.ids[:100]

        values.update({
            'date': date_begin,
            'payments': payments,
            'page_name': 'payments',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/payments',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render('branom_website_sale.portal_my_payments', values)

    def _check_user_payment(self, payment_id):
        partner_id = request.env.user.partner_id.id
        payment = request.env['account.payment'].sudo().search([('partner_id', '=', partner_id),
                                                                ('id', '=', payment_id)])

        return payment or None

    @route(['/my/payment/<payment_id>'], type='http', auth="public", website=True)
    def portal_my_payment_detail(self, payment_id, **kw):

        try:
            payment_sudo = self._check_user_payment(payment_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'page_name': 'payments',
            'payment': payment_sudo,
        }

        return request.render("branom_website_sale.portal_payment_page", values)
