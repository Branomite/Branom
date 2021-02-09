import json
from odoo import _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route, Controller


class WebsiteSaleDeliveryManager(Controller):
    @route('/sale_change_shipping_account', type='json', auth='user', website=True, sitemap=False)
    def website_sale_assign_partner_account(self):
        data = json.loads(request.httprequest.data)
        shipping_id = data.get('params').get('carrier_id')
        partner_acct = data.get('params').get('partner_acct')
        partner = request.env.user.partner_id
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id and shipping_id:
            partner_shipping_accts = partner._get_portal_shipping_accounts()
            partner_ship_id = partner_shipping_accts.search([('id', '=', shipping_id)])
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            # Write partners shipping account if verified
            if order and partner_ship_id and partner_acct:
                order.write({
                    'shipping_account_id': partner_ship_id.id,
                })
                return {'result': 'shipping_acct'}
            # Remove shipping account from SO
            else:
                order.write({
                    'shipping_account_id': False,
                })
                return {'result': 'no_acct'}


class WebsitePortalDeliveryManager(Controller):
    @route('/my/account/delivery/methods', type='http', auth='user', website=True, sitemap=False)
    def website_portal_delivery_manager(self, **kwargs):
        partner = request.env.user.partner_id
        data = {
            'partner': partner or False,
            'page_name': 'shipping_accounts',
        }
        # Retrieve list of partner shipping accounts
        if partner:
            accounts = partner.sudo()._get_portal_shipping_accounts()
            if accounts:
                data.update({'accounts': accounts})

        return request.render('branom_website_partner_delivery.manage_shipping_accounts', data)

    @route('/my/account/delivery/method_update', type='json', auth='user', website=True, sitemap=False)
    def website_portal_delivery_method_update(self, **kwargs):
        partner = request.env.user.partner_id
        data = json.loads(request.httprequest.data)
        operation = data.get('params').get('operation')
        record_id = data.get('params').get('record_id')
        description = data.get('params').get('description')
        name = data.get('params').get('name')
        ups_zip = data.get('params').get('account_zip')
        delivery_type = data.get('params').get('delivery_type')
        ShippingAccount = request.env['partner.shipping.account']

        values = {
                'partner_id': partner.id,
                'description': description,
                'name': name,
                'delivery_type': delivery_type
            }
        # Only accept zip for UPS
        if delivery_type == 'ups':
            values.update({'ups_zip': ups_zip})

        if partner and operation == 'create':
            # Create a new record - Return for confirmation msg
            new_account = ShippingAccount.create(values)

            return {'status': 'complete', 'message': 'Shipping account created', 'new_account': new_account}

        # Verify that requested record belongs to current partner
        record = ShippingAccount.search([('id', '=', record_id), ('partner_id', '=', partner.id)])

        # Edit or remove record per operation
        if operation and record:
            if operation == 'edit':
                partner.write({
                    'shipping_account_ids': [(1, record.id, values)]
                })
                return {'status': 'complete', 'message': 'Shipping account updated'}

            if operation == 'delete':
                partner.write({
                    'shipping_account_ids': [(2, record.id)]
                })
                return {'status': 'complete', 'message': 'Shipping account removed'}

        else:
            return {'status': 'error', 'message': 'Could not update, please contact us for assistance'}

class PortalShippingAccounts(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalShippingAccounts, self)._prepare_portal_layout_values()
        shipping_accounts = request.env.user.partner_id._get_portal_shipping_accounts()
        shipping_accounts_count = 0
        if shipping_accounts:
            shipping_accounts_count = len(shipping_accounts)
        values['shipping_accounts_count'] = shipping_accounts_count

        return values
