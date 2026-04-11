from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type."
    _order = "name"

    name = fields.Char(required=True, string="Type")
    sequence = fields.Integer("Sequence", default=0, help="Used to order types alphabetically.")
    property_ids = fields.One2many("estate.property", "property_type_id")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_offer_count", string="Number of offers")

    _unique_type_name = models.Constraint("unique (name)", "Property type name must be unique.")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
