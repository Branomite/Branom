from odoo import api, fields, http, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_portal_shipping_accounts(self):
        self.ensure_one()
        if self.parent_id:
            return self.parent_id.shipping_account_ids.filtered(lambda l: l.delivery_type in ['fedex', 'ups'])
        elif self.shipping_account_ids:
            return self.shipping_account_ids.filtered(lambda l: l.delivery_type in ['fedex', 'ups'])
        else:
            return False

    @api.model
    def render_shipping_account_modal(self, data):
        partner_id = data.get('partner_id')
        record_id = data.get('record_id')
        operation = data.get('operation')
        # Return a record if found
        if record_id and record_id != 'new':
            record = self.env['partner.shipping.account'].search([('partner_id', '=', partner_id),
                                                                  ('id', '=', record_id)])
        else:
            record = False

        vals = {
            'partner_id': partner_id,
            'record': record,
            'operation': operation,
        }

        return http.request.env['ir.ui.view'].render_template('branom_website_partner_delivery.modal_form_data', vals)
