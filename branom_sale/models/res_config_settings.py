from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    commission_account_id = fields.Many2one('account.account', string="Commission Account", readonly=False,
                                            help="Account designated for Commission Type Sales.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commission_account_id = fields.Many2one('account.account', string="Commission Account", readonly=False,
                                            related='company_id.commission_account_id',
                                            help="Account designated for Commission Type Sales.")
