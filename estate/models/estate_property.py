from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property."
    _order = "id desc"

    name = fields.Char(required=True, string="Title", translate=True)
    description = fields.Text(translate=True)
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False,
        default=fields.Date.add(fields.Date.today(), months=3),
        string="Available From",
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        help="Type is used to define the garden orientation of the property.",
    )
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        help="Used to define the status of the property.",
        required=True,
        default="new",
    )
    active = fields.Boolean(default=True)
    property_type_id = fields.Many2one("estate.property.type")
    buyer_id = fields.Many2one("res.partner", copy=False)
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.uid)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        string="Company",
    )
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    _positive_expected_price = models.Constraint(
        "CHECK(expected_price > 0)", "Expected price must be strictly positive and greater than 0."
    )
    _positive_selling_price = models.Constraint("CHECK(selling_price >= 0)", "Selling price must be positive.")

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue
            if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError(self.env._("The selling price cannot be lower than 90%% of the expected price."))

    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_new_or_cancelled(self):
        for record in self:
            if record.state not in ["new", "cancelled"]:
                raise UserError(
                    self.env._(
                        "The property can only be deleted if it is 'cancelled' or 'new', current state is %(current_state)s"
                    )
                    % {"current_state": record.state}
                )

    @api.onchange("garden")
    def _onchange_garden(self):
        self.garden_area = 0
        self.garden_orientation = False

        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError(self.env._("A sold property cannot be cancelled."))
            record.state = "cancelled"

    def action_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(self.env._("A cancelled property cannot be set as sold."))
            accepted_offer = record.offer_ids.filtered(lambda o: o.status == "accepted")
            if not accepted_offer:
                raise UserError(self.env._("Cannot sell a property without an accepted offer."))
            record.state = "sold"
