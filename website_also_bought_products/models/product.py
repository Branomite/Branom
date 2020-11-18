# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	wk_also_bought_products = fields.Many2many('product.product',
		'source_id',
		'destination_id',
		'rel_id',
		string="Also Bought"
	)

	