# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, http
from odoo.http import request


_logger = logging.getLogger(__name__)


class QuickOrder(http.Controller):
    @http.route('/quick-order', type='http', auth='public', website=True, sitemap=False)
    def quick_order(self, *args, **kwargs):
        return request.render('branom_website_sale.quick_order_page')

    @http.route('/quick-order/validate', type='json', auth='public', website=True, sitemap=False)
    def validate_sku(self, *data, **kwargs):
        _logger.warning('validate_sku')
        _logger.warning(data)
        _logger.warning(kwargs)

        sku = kwargs.get('sku')
        response = {'success': False, 'message': ''}
        if sku:
            odoo_product = request.env['product.template'].search([('default_code', '=', sku)], limit=1)
            if odoo_product and odoo_product._is_add_to_cart_possible():
                response['success'] = True
                response['message'] = odoo_product.name
        return response

    @http.route(['/quick-order/add-items'], type='json', auth='public', website=True, sitemap=False)
    def add_items(self, **data):
        products = data.get('products')
        errors = []
        if products:
            odoo_products = []
            for product in products:
                odoo_product = request.env['product.template'].search([('default_code', '=', product['sku'])], limit=1)
                if odoo_product and odoo_product._is_add_to_cart_possible():
                    odoo_products.append((odoo_product.product_variant_id.id, product['qty']))
                else:
                    errors.append('Product not found: %s' % product['sku'])
        else:
            errors.append('No products were entered')

        if errors:
            return {'success': False, 'errors': errors}
        else:
            sale_order = request.website.sale_get_order(force_create=True)
            if sale_order.state != 'draft':
                request.session['sale_order_id'] = None
                sale_order = request.website.sale_get_order(force_create=True)
            for product_id, qty in odoo_products:
                if int(qty) > 0:
                    sale_order._cart_update(product_id=product_id,
                                            add_qty=qty)

            return {'success': True, 'products_added': len(odoo_products)}
