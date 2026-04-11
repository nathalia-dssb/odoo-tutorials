from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tag."
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _unique_tag_name = models.Constraint("unique (name)", "Tag name must be unique.")
