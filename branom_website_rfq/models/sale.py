from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rfq_line_ids = fields.One2many('sale.order.rfq.line', 'order_id')
    partner_industry = fields.Char('Industry')
    rfq_quantity = fields.Integer(compute='_compute_rfq_info', string='RFQ Quantity')

    @api.depends('rfq_line_ids.request_qty', 'rfq_line_ids.product_id')
    def _compute_rfq_info(self):
        for order in self:
            order.rfq_quantity = int(sum(order.mapped('rfq_line_ids.request_qty')))

    @api.model
    def check_so_line_rfq(self):
        self.ensure_one()
        for line in self.order_line:
            if line.product_id.is_rfq_product(self.partner_shipping_id):
                self.rfq_line_ids.write({
                    'product_id': line.product_id,
                    'request_qty': line.product_uom_qty,
                })
                self.order_line.write({[(2, line.id, False)]})

    @api.model
    def convert_rfq_to_lead(self):
        self.ensure_one()
        partner = self.partner_id
        name = 'Quote request for %s' % partner.name

        values = {
            'type': 'lead',
            'name': name,
        }

        # Update dict with all available partner values
        if partner:
            values.update({'partner_id': partner.id})
        if partner.email:
            values.update({'email_from': partner.email})
        if partner.phone:
            values.update({'phone': partner.phone})
        if partner.street:
            values.update({'street': partner.street})
        if partner.city:
            values.update({'city': partner.city})
        if partner.state_id:
            values.update({'state_id': partner.state_id.id})
        if partner.country_id:
            values.update({'country_id': partner.country_id.id})
        if partner.zip:
            values.update({'zip': partner.zip})
        if self.rfq_line_ids:
            values.update({
                'rfq_line_ids': [(6, 0, self.rfq_line_ids.ids)]
            })

        # Create CRM lead
        if partner:
            new_lead = self.env['crm.lead'].create(values)
            if new_lead:
                self.write({
                            'rfq_line_ids': [(5, 0, 0)]
                        })
                return True

            else:
                return False


class SaleOrderRfqLine(models.Model):
    _name = 'sale.order.rfq.line'

    product_id = fields.Many2one('product.template', string='Product')
    request_qty = fields.Float(string='Requested Qty')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead')
