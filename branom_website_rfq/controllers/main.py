# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import Controller, request, route


class WebsiteSale(WebsiteSale):
    @route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation(self, **post):
        res = super(WebsiteSale, self).payment_confirmation()
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order and order.rfq_line_ids:
                order.convert_rfq_to_lead()

        return res

    def _prepare_product_values(self, product, category, search, **kwargs):
        res = super()._prepare_product_values(product, category, search, **kwargs)
        is_public_user = request.env.user == request.website.user_id
        if not is_public_user:
            res['partner'] = request.env.user.partner_id
        else:
            res['partner'] = request.env['res.partner']
        return res


class WebsiteSaleRFQ(Controller):
    @route('/shop/product/rfq/update', type='json', auth='public', methods=['POST'], website=True, sitemap=False)
    def product_rfq_update(self, **post):

        order = request.website.sale_get_order(force_create=True)
        data = json.loads(request.httprequest.data)

        if order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order(force_create=True)

        if data and order:
            product_id = int(data.get('params').get('product_id', False))
            operation = data.get('params').get('operation', False)
            request_qty = data.get('params').get('request_qty', False)

            _logger.warn(request_qty)
            # Process Qty
            if request_qty:
                qty = int(request_qty)
            else:
                qty = False
            _logger.warn('QTY: %s' % qty)

            # Process Product
            _logger.warn('JS product_id: %s' % product_id)
            if product_id:
                product = request.env['product.template'].search([('id', '=', product_id)])
                if product:
                    _logger.warn('product found: %s' % product.name)
            else:
                product = False

            _logger.warn('operation: %s' % operation)

            # Enforce a valid product and operation
            if product and operation:

                product_line = order.rfq_line_ids.filtered(lambda l: l.product_id.id == product.id)
                if product_line:
                    _logger.warn('Product Line: %s' % product_line.product_id.name)

                if operation == 'create':
                    _logger.warn('CREATE')
                    # update existing line if the same product is added multiple times or create a new line
                    if product_line:
                        new_qty = product_line.request_qty + 1
                        order.write({
                            'rfq_line_ids': [(1, product_line.id, {
                                'request_qty': new_qty,
                            })]
                        })
                    else:
                        order.write({
                            'rfq_line_ids': [(0, 0, {
                                'order_id': order.id,
                                'product_id': product.id,
                                'request_qty': 1,
                            })]
                        })

                if qty and operation == 'update':
                    order.write({
                        'rfq_line_ids': [(1, product_line.id, {
                            'request_qty': qty,
                        })]
                    })

                if operation == 'delete':
                    order.write({
                        'rfq_line_ids': [(2, product_line.id)]
                    })

    # Show users outcome of RFQ submit and clear lines from order if successful
    @route('/shop/rfq/form/confirmation', type='http', auth='public', website=True, sitemap=False)
    def rfq_form_confirmation(self):
        return request.render('branom_website_sale.rfq_confirmation_page')

    # Submit Data for Form and create CRM leads; Then direct to confirmation page
    @route('/shop/rfq/form/submit', type='http', auth='public', website=True, sitemap=False)
    def rfq_form_submit(self, *args, **kwargs):

        order = request.website.sale_get_order()
        partner = order.partner_id

        # Create CRM lead
        if order and partner:
            new_lead = order.convert_rfq_to_lead()
            if new_lead:
                _logger.warn(new_lead)
                _logger.warn('New Lead Created')
                return request.render('branom_website_sale.rfq_confirmation_page',
                                      {'status': 'Success', 'message': 'Your quote request has been received.'})
            else:
                _logger.warn('Failed to complete lead')
                return request.render('branom_website_sale.rfq_confirmation_page',
                                      {'status': 'Failed', 'message': 'Your quote request could not be sent.'})

    # Main RFQ page - used to allow users to submit RFQ without cart items
    @route('/shop/rfq/form', type='http', auth='public', website=True, sitemap=False)
    def rfq_form_page(self):
        return request.render('branom_website_sale.rfq_form_page')
