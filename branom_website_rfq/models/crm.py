from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    rfq_line_ids = fields.One2many('sale.order.rfq.line', 'crm_lead_id')
