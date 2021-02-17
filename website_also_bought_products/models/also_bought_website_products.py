# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################


from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
	_inherit = 'website'

	use_automatic = fields.Boolean(
		string="Add Products Automatically",
		help="Add the products automatically to the also bought on the purchase"
	)

	header = fields.Char(
		string="Header Message",
		required=True,
	)
