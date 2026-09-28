from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property offer"
    _order = "price desc"

    price = fields.Float(required=True)
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused")
        ],
        copy=False,
        readonly=True
    )
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True, precompute=True)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    _check_price = models.Constraint(
        "CHECK (price > 0)",
        "The price must be strictly positive.",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            start = fields.Date.context_today(record, record.create_date)
            record.date_deadline = fields.Date.add(start, days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if not record.date_deadline:
                continue

            start = fields.Date.context_today(record, record.create_date)
            record.validity = (record.date_deadline - start).days

    def action_accept(self):
        self.ensure_one()

        if "accepted" in self.property_id.offer_ids.mapped("status"):
            raise UserError("You can accept an offer if there are no other offer accepted")

        self.status = "accepted"
        self.property_id.selling_price = self.price
        self.property_id.buyer_id = self.partner_id
        self.property_id.state = "offer_accepted"
        (self.property_id.offer_ids - self).write({"status": "refused"})

    def action_refuse(self):
        self.ensure_one()
        self.status = "refused"
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property = self.env["estate.property"].browse(vals["property_id"])

            if vals["price"] < property.best_price:
                raise UserError(f"The offer must be higher than {property.best_price}")

            property.state = "offer_received"

        return super().create(vals_list)
