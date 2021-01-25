from odoo import http
from odoo.http import request


class ServiceRequestController(http.Controller):
    @http.route('/service', type='http', auth='public', website=True, sitemap=False)
    def service_request(self, *args, **post):
        countries = request.env['res.country'].get_website_sale_countries()

        if request.httprequest.method == 'POST':
            # copy all the basic string fields
            string_fields = ('contact_name', 'partner_name', 'street', 'street2', 'phone', 'email_from',)
            create_vals = dict(filter(lambda i: i[0] in string_fields, post.items()))
            create_vals['name'] = 'Service Request'

            country_id = post.get('country_id')
            country_id = country_id and int(country_id)
            if country_id and country_id in countries.ids:
                create_vals['country_id'] = country_id
            state_id = post.get('state_id')
            state_id = state_id and int(state_id)
            if state_id and state_id in request.env['res.country'].browse(country_id).state_ids.ids:
                create_vals['state_id'] = state_id
            create_vals['description'] = 'Calibration Level: %s\n' % post.get('calibration', '')
            create_vals['description'] += 'Repair, if needed: %s\n' % post.get('repair', '')
            create_vals['description'] += 'Method of Return: %s' % post.get('return', '')
            request.env['crm.lead'].create([create_vals])
            return request.redirect('/service-confirmation')

        render_values = {
            'countries': countries,
        }
        return request.render('branom_website_sale.service_request', render_values)

    @http.route('/service-confirmation', type='http', auth='public', website=True, sitemap=False)
    def service_confirmation(self, *args, **kwargs):
        return request.render('branom_website_sale.service_confirmation')
