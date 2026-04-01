from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tag."

    _unique_tag_name = models.Constraint("unique (name)", "Tag name must be unique.")

    name = fields.Char(required=True)
