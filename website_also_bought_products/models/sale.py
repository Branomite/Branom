# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
	_inherit = "sale.order"


	def action_confirm(self):
		prd_ids = []
		use_automatic = self.env['website'].sudo().get_current_website().use_automatic
		if use_automatic:
			deliveryProduct = 0
			if self.carrier_id:
				deliveryProduct = self.carrier_id.product_id.id
			productIds = self.order_line.mapped('product_id').ids
			if deliveryProduct in productIds:
				productIds.remove(deliveryProduct)
			productObjs = self.env['product.product'].browse(productIds)
			for productObj in productObjs:
				alsoIds = list(set(productObj.product_tmpl_id.wk_also_bought_products.ids + productIds)-set(productObj.ids))
				productObj.product_tmpl_id.wk_also_bought_products = [(6, 0, alsoIds)]
		return super(SaleOrder, self).action_confirm()
