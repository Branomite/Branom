from odoo import http
from odoo.http import request


class ServiceRequestController(http.Controller):
    @http.route('/service', type='http', auth='public', website=True, sitemap=False)
    def service_request(self, *args, **post):
        countries = request.env['res.country'].get_website_sale_countries()

        if request.httprequest.method == 'POST':
            # copy all the basic string fields
            string_fields = ('contact_name', 'partner_name', 'street', 'street2',
                             'city', 'zip', 'phone', 'email_from',)
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
            create_vals['description'] = 'Resale: %s\n' % post.get('resale', '')
            create_vals['description'] += 'Calibration Level: %s\n' % post.get('calibration', '')
            create_vals['description'] += 'Repair, if needed: %s\n' % post.get('repair', '')
            create_vals['description'] += 'Expedite: %s\n' % post.get('expedite', 'No')
            notes = post.get('notes', '')
            if notes:
                notes = notes.replace('\n', '\n\t')
                create_vals['description'] += 'Special instructions:\n\t%s\n' % notes
            create_vals['description'] += 'Payment: %s\n' % post.get('payment', '')
            if 'po' in post:
                create_vals['description'] += 'PO: %s\n' % post['po']
            create_vals['description'] += 'Method of Return: %s\n' % post.get('return', '')
            if 'return_info' in post:
                create_vals['description'] += 'Return Info: %s\n' % post['return_info']
                if 'collect_num' in post:
                    create_vals['description'] += 'Collect #: %s\n' % post['collect_num']


            lead = request.env['crm.lead'].create([create_vals])
            lead.tag_ids = [(4, request.env.ref('branom_website_sale.service_request_tag').id)]
            return request.redirect('/service-confirmation')

        render_values = {
            'countries': countries,
        }
        return request.render('branom_website_sale.service_request', render_values)

    @http.route('/service-confirmation', type='http', auth='public', website=True, sitemap=False)
    def service_confirmation(self, *args, **kwargs):
        return request.render('branom_website_sale.service_confirmation')
