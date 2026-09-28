from odoo import api, fields, models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = "estate.property"
    _inherit = ["mail.thread"]
    _description = "A real estate property"
    _order = "id desc"

    name = fields.Char(required=True, string="Title")
    description = fields.Text()
    active = fields.Boolean(default=True)
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda _: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=[
        ("north", "North"),
        ("south", "South"),
        ("east", "East"),
        ("west", "West")
    ])
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer received"),
            ("offer_accepted", "Offer accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled")
        ],
        required=True,
        copy=False,
        default="new",
        tracking=True
    )
    property_type_id = fields.Many2one("estate.property.type")
    buyer_id = fields.Many2one("res.partner", copy=False)
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    tag_ids = fields.Many2many("estate.property.tag")
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    _check_expected_price = models.Constraint(
        "CHECK (expected_price > 0)",
        "The expected price must be strictly positive.",
    )
    _check_selling_price = models.Constraint(
        "CHECK (selling_price >= 0)",
        "The selling price can't be negative.",
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0)

    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            record.garden_area = 10 if record.garden else 0
            record.garden_orientation = "north" if record.garden else None

    @api.onchange("date_availability")
    def _onchange_date_availability(self):
        for record in self:
            if record.date_availability < fields.Date.today():
                return {
                    "warning": {
                        "title": "Eye!!!",
                        "message": "Date availability is in the past."
                    }
                }

    def action_sold(self):
        self.ensure_one()
        if self.state != "offer_accepted":
            raise UserError("You can only sale a property when offer was accepted.")

        self.state = "sold"

    def action_cancel(self):
        self.ensure_one()
        if self.state == "sold":
            raise UserError("You can't cancel a property already sold.")

        self.state = "canceled"

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if any(record.state not in ("new", "canceled") for record in self):
            raise UserError("Can't delete a property if it is not new or canceled")

