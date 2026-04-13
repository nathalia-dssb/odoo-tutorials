from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstateTestCase, cls).setUpClass()

        cls.Property = cls.env["estate.property"]
        cls.Offer = cls.env["estate.property.offer"]
        cls.Partner = cls.env["res.partner"]

        cls.property_new = cls.Property.create(
            {
                "name": "New House",
                "expected_price": 200000,
                "state": "new",
            }
        )
        cls.property_offer_accepted = cls.Property.create(
            {
                "name": "House With Accepted Offer",
                "expected_price": 300000,
                "state": "offer_accepted",
            }
        )
        cls.property_sold = cls.Property.create(
            {
                "name": "Sold House",
                "expected_price": 250000,
                "state": "sold",
            }
        )
        cls.partner = cls.Partner.create({"name": "Test Buyer"})

        cls.accepted_offer = cls.Offer.create(
            {
                "price": 300000,
                "partner_id": cls.partner.id,
                "property_id": cls.property_offer_accepted.id,
                "status": "accepted",
            }
        )

    def test_cannot_create_offer_on_sold_property(self):
        """Test that creating an offer for a sold property raises a UserError."""
        with self.assertRaises(UserError):
            self.Offer.create(
                {
                    "price": 250000,
                    "partner_id": self.partner.id,
                    "property_id": self.property_sold.id,
                }
            )

    def test_cannot_sell_without_accepted_offer(self):
        """Test that selling a property with no accepted offers raises a UserError."""
        with self.assertRaises(UserError):
            self.property_new.action_sold()

    def test_sell_property_with_accepted_offer(self):
        """Test that a property with an accepted offer can be sold and state is updated."""
        self.property_offer_accepted.action_sold()
        self.assertRecordValues(
            self.property_offer_accepted,
            [{"name": "House With Accepted Offer", "state": "sold"}],
        )

    def test_garden_fields_reset_on_uncheck(self):
        """Test that garden_area and garden_orientation are reset when garden is unchecked."""
        with Form(self.Property) as form:
            form.name = "Garden House"
            form.expected_price = 150000
            form.garden = True
            form.garden_area = 50
            form.garden_orientation = "south"  
            form.garden = False
        property_record = form.save()
        self.assertFalse(property_record.garden_area)
        self.assertFalse(property_record.garden_orientation)
