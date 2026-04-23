"""
Run: bench --site myexpense.local execute myexpense.api.seed.create_seed_data
"""
import frappe
from frappe.utils import add_days, today


def create_seed_data():
	user = frappe.session.user or "Administrator"

	# ── Personal expenses ──
	personal = [
		dict(title="Blue Tokai", amount=420,   type="Expense", category="Food & Dining",    notes="Cold brew + sandwich"),
		dict(title="Uber",       amount=184,   type="Expense", category="Transportation",   notes="Koramangala → HSR"),
		dict(title="Cinepolis",  amount=560,   type="Expense", category="Entertainment",    notes="Movie night"),
		dict(title="Acme Ltd.",  amount=68000, type="Income",  category="Salary",           notes="Salary · April"),
		dict(title="Decathlon",  amount=3200,  type="Expense", category="Shopping",         notes="Running shoes"),
		dict(title="Airtel Fiber",amount=1199, type="Expense", category="Utilities",        notes="Monthly bill"),
	]
	for i, p in enumerate(personal):
		if frappe.db.exists("Expense", {"title": p["title"], "paid_by": user}):
			continue
		doc = frappe.new_doc("Expense")
		doc.update(p)
		doc.paid_by = user
		doc.currency = "INR"
		doc.transaction_date = add_days(today(), -i)
		doc.status = "Submitted"
		doc.created_via = "API"
		doc.insert(ignore_permissions=True)

	# ── Group: HSR Flat 302 ──
	if not frappe.db.exists("Expense Group", "HSR Flat 302"):
		grp = frappe.new_doc("Expense Group")
		grp.group_name = "HSR Flat 302"
		grp.description = "Shared flat expenses"
		grp.owner_user = user
		grp.append("members", {"user": user, "display_name": "Rohan", "share_percent": 33.33})
		grp.insert(ignore_permissions=True)

	# Group expense with split
	if not frappe.db.exists("Expense", {"title": "Mrs. Iyer – April Rent", "group": "HSR Flat 302"}):
		doc = frappe.new_doc("Expense")
		doc.title = "Mrs. Iyer – April Rent"
		doc.amount = 12500
		doc.type = "Expense"
		doc.category = "Rent & Housing"
		doc.transaction_date = add_days(today(), -5)
		doc.paid_by = user
		doc.currency = "INR"
		doc.is_group_expense = 1
		doc.group = "HSR Flat 302"
		doc.is_split = 1
		doc.notes = "April rent · room share"
		doc.status = "Submitted"
		doc.created_via = "API"
		for i, name in enumerate(["Rohan", "Arjun", "Dev"]):
			doc.append("splits", {
				"user": user,
				"display_name": name,
				"split_type": "Equal",
				"share_amount": 4167 if i < 2 else 4166,
				"settled": 0,
			})
		doc.insert(ignore_permissions=True)

	frappe.db.commit()
	print("✅ Seed data created successfully")
