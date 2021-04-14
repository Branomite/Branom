from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    show_address = fields.Boolean('Show Address', compute='_compute_show_address')

    @api.model
    def create(self, vals):
        carrier_id_val = vals.get('carrier_id')
        origin = vals.get('origin')
        if origin and carrier_id_val:
            carrier = self.env['delivery.carrier'].search([('id', '=', carrier_id_val)])
            sale_order = self.env['sale.order'].search([('name', '=', origin)])
            if sale_order and carrier:
                so_vals = {'ups_service_type': carrier.ups_default_service_type}
                if not sale_order.ups_carrier_account:
                    so_vals.update({'ups_carrier_account': carrier.ups_shipper_number})
                sale_order.write(so_vals)
        res = super().create(vals)
        return res

    @api.depends('picking_type_id', 'picking_type_code')
    def _compute_show_address(self):
        for picking in self:
            picking.show_address = picking.picking_type_code == 'outgoing' and picking.picking_type_id.name != 'Will Call'
