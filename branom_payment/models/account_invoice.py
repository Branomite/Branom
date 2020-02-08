# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    payment_difference = fields.Monetary(string='Payment Difference', help="Payment difference in invoice's currency.", copy=False)

