from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    payment_deposit_threshold = fields.Float(string='Payment Deposit Threshold',
                                             help='Allow customers to make a deposit when their order '
                                                  'total is above this amount.')

    website_default_payment_term_id = fields.Many2one('account.payment.term', string='Default Website Payment Term')
    website_payment_reviewer_id = fields.Many2one('res.users', string='Portal Payment Notifications')
    website_sale_document_upload = fields.Boolean('Document Upload')
    website_payment_reviewer_id = fields.Many2one('res.users', string='Portal Payment Notifications')
