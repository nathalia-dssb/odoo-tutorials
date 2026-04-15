from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer."
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7, string="Validity (days)")
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    _positive_offer_price = models.Constraint(
        "CHECK(price > 0)", "Offer price must be strictly positive and greater than 0."
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            date = record.create_date or fields.Date.today()
            record.date_deadline = fields.Date.add(date, days=record.validity or 0)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = vals.get("property_id")
            if property_id:
                prop = self.env["estate.property"].browse(property_id)

                if prop.state == 'sold':
                    raise UserError(self.env._("Cannot create offer on an already sold property."))
                
                max_existing = max(prop.offer_ids.mapped("price"), default=0.0)
                if vals.get("price", 0) < max_existing:
                    raise UserError(
                        self.env._("Offer amount cannot be lower than existing offer of $%(max)s.") % {"max": max_existing}
                    )
                prop.state = "offer_received"

        return super().create(vals_list)

    def action_accept(self):
        for record in self:
            # Checks if another offer has already been accepted for this property,
            # in this case scenario it's asumed that only one offer can be accepted
            # and once it has been accepted, no other offers should be accepted
            accepted_offer = record.property_id.offer_ids.filtered(lambda o: o.status == "accepted")
            if accepted_offer:
                raise UserError(self.env._("An offer for this property has already been accepted."))

            # If an offer it's accepted, all others should be refused
            other_offers = record.property_id.offer_ids.filtered(lambda o: o.id != record.id)
            other_offers.write({"status": "refused"})

            # Finally the changes to the record will be done if valitaions passed correctly
            record.property_id.write(
                {
                    "buyer_id": record.partner_id.id,
                    "selling_price": record.price,
                    "state": "offer_accepted",
                }
            )
            record.status = "accepted"

    def action_refuse(self):
        for record in self:
            if record.status == "refused":
                raise UserError(self.env._("This offer is already refused."))
            record.status = "refused"
