from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def match_attr_vals_to_studio_vals(self):
        self.ensure_one()
        attr_list = {
            'x_studio_product_unit_of_measure': 'Product Unit of Measure',
            'x_studio_measurement_minimum_1': 'Measurement Minimum',
            'x_studio_measurement_maximum_1': 'Measurement Maximum',
            'x_studio_input_communication_protocol': 'Input Communication Protocol',
            'x_studio_communication_protocol': 'Output Communication Protocol',
            'x_studio_input_power': 'Input Voltage',
            'x_studio_input_amps': 'Input Amps',
            'x_studio_watts': 'Watts',
            'x_studio_heater_type': 'Heater Type',
            'x_studio_connection_type': 'Process Connection Type',
            'x_studio_connection_size': 'Process Connection Size',
            'x_studio_connection_location': 'Process Connection Location',
            'x_studio_dial_size': 'Dial Size',
            'x_studio_case_material': 'Case Material',
            'x_studio_wetted_material': 'Wetted Material',
            'x_studio_stem_length': 'Stem Length',
            'x_studio_stem_diameter': 'Stem Diameter',
            'x_studio_min_operating_pressure': 'Min Operating Pressure',
            'x_studio_min_operating_temperature': 'Min Operating Temperature',
            'x_studio_max_operating_temperature': 'Max Operating Pressure',
            'x_studio_accuracy': 'Accuracy',
            'x_studio_ingress_protection': 'Ingress Protection',
        }

        for item in attr_list:
            matched_attribute = self.env['product.attribute'].search([('name', '=', str(attr_list[item]))])

            if len(matched_attribute) > 1:
                raise UserError(_('Too Many Matched Attributes for product %s: %s' % (self.id, self.name)))

            if matched_attribute:

                product_attr_val = self[item]

                if product_attr_val:
                    matched_attr_value = self.env['product.attribute.value'].search([
                        ('attribute_id', '=', matched_attribute.id),
                        ('name', '=', str(product_attr_val))])

                    if not matched_attr_value:
                        new_attr_value = self.env['product.attribute.value'].create({
                            'attribute_id': matched_attribute.id,
                            'name': product_attr_val,
                        })
                        attr_value = new_attr_value

                    else:
                        attr_value = matched_attr_value

                    self.env['product.template.attribute.line'].create({
                        'attribute_id': matched_attribute.id,
                        'product_tmpl_id': self.id,
                        'value_ids': [(4, attr_value.id)]
                    })
