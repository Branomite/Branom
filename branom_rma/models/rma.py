from odoo import api, fields, models


class RMATemplate(models.Model):
    _inherit = 'rma.template'

    branom_sequence_suffix = fields.Char(string='Sequence Suffix', help='enter "-STOCK" to make "RMA001-STOCK"')

class RMA(models.Model):
    _inherit = 'rma.rma'

    @api.model
    def create(self, vals):
        res = super(RMA, self).create(vals)
        if res.template_id.branom_sequence_suffix:
            res.name = str(res.name) + res.template_id.branom_sequence_suffix
        return res
