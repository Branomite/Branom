from odoo import http
from odoo.http import request


class ServiceRequestController(http.Controller):
    @http.route('/service', type='http', auth='public', website=True, sitemap=False)
    def service_request(self, *args, **kwargs):
        render_values = {
            'countries': request.env['res.country'].get_website_sale_countries()
        }
        return request.render('branom_website_sale.service_request', render_values)

    @http.route('/service-process', type='http', auth='public', website=True, sitemap=False, methods=['POST'])
    def process_request(self, *args, **post):
        create_vals = {}
        for key, val in post.items():
            if key in ('name', 'partner_name', 'street', 'street2', 'phone', 'email_from',):
                create_vals[key] = val
        create_vals['description'] = 'Calibration Level: %s\n' % post.get('calibration', '')
        create_vals['description'] += 'Repair, if needed: %s\n' % post.get('repair', '')
        create_vals['description'] += 'Method of Return: %s' % post.get('return', '')
        request.env['crm.lead'].create(create_vals)
        return request.redirect('/service-confirmation')

    @http.route('/service-confirmation', type='http', auth='public', website=True, sitemap=False)
    def service_confirmation(self, *args, **kwargs):
        return request.render('branom_website_sale.service_confirmation')
