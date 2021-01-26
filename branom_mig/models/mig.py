from odoo import api, fields, models

from logging import getLogger
_logger = getLogger(__name__)


class MigBase(models.Model):
    _name = 'mig.base'
    _description = 'Branom MIG'

    def get_model_fields(self):
        # Test comment
        return self.env['product.template'].fields_get()

    def migrate_fields(self, field, attribute_name):
        fields = self.get_model_fields()
        field = fields[field]
        new_attribute = self.env['product.attribute'].create({
            'name': attribute_name,
            'display_type': 'select',
            'create_variant': 'no_variant',
        })

        # Create Attribute Values for Selection Field Types
        if field.get('selection'):
            for selection in field['selection']:
                self.env['product.attribute.value'].create({
                    'attribute_id': new_attribute.id,
                    'name': selection[1],
                })

    def run_attr_migration(self):
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
            self.migrate_fields(item, attr_list[item])

    def run_product_migration(self):
        products = self.env['product.template'].search([])
        for product in products:
            product.match_attr_vals_to_studio_vals()
