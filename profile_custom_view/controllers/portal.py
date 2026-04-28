from odoo.http import request, route

from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalExtended(CustomerPortal):

    @route(['/my', '/my/home'], auth='user', website=True)
    def home(self, **kw):
        my_values = [
            {'value': 'first',  'label': 'First Value'},
            {'value': 'second', 'label': 'Second Value'},
            {'value': 'third',  'label': 'Third Value'},
        ]

        response = super().home(**kw)
        response.qcontext['my_values'] = my_values
        return response
