# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################


from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)


class AlsoBoughtProductsConf(models.TransientModel):
	_name = 'also.bought.products.conf'
	_inherit = 'webkul.website.addons'

	use_automatic = fields.Boolean(
		string="Add Products Automatically",
		help="Add the products automatically to the also bought on the purchase",
		related="website_id.use_automatic",
		readonly=False
	)

	abtp_header = fields.Char(
		string="Header Message",
		required=True,
		related="website_id.abtp_header",
		readonly=False
	)
