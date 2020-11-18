# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID

from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)


class website_sale(WebsiteSale):
	
	@http.route(['/also/bought/add_to_cart'], type='json', auth="public",  website=True)
	def also_bought_add_to_cart(self, product_id, qty,  **kw):
		order = request.website.sale_get_order()
		request.website.sale_get_order(force_create=1)._cart_update(
			product_id=int(product_id),
			add_qty=float(qty),
			set_qty=float(qty),
		)
		return True
		
	