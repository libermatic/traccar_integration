# Copyright (c) 2024, Libermatic and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class M2MSubscription(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activation_date: DF.Date | None
		disabled: DF.Check
		expiry_date: DF.Date | None
		msin: DF.Data
		operator: DF.Data | None
	# end: auto-generated types
	pass
