import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_groups():
	user = frappe.session.user
	owned = frappe.get_all(
		"Expense Group",
		filters={"owner_user": user},
		fields=["name", "group_name", "description", "owner_user"],
	)
	member_of = frappe.db.sql(
		"""SELECT DISTINCT eg.name, eg.group_name, eg.description, eg.owner_user
		   FROM `tabExpense Group` eg
		   JOIN `tabGroup Member` gm ON gm.parent=eg.name
		   WHERE gm.user=%s AND eg.owner_user!=%s""",
		(user, user),
		as_dict=True,
	)
	seen = {g.name for g in owned}
	all_groups = list(owned)
	for g in member_of:
		if g.name not in seen:
			all_groups.append(g)
	return all_groups


@frappe.whitelist()
def get_group_detail(group_name):
	user = frappe.session.user
	group = frappe.get_doc("Expense Group", group_name)
	if not group.is_member(user):
		frappe.throw(_("Not a member"), frappe.PermissionError)
	total_expense = frappe.db.sql(
		"""SELECT COALESCE(SUM(amount), 0) FROM `tabExpense`
		   WHERE `group`=%s AND is_group_expense=1 AND type='Expense' AND status!='Cancelled'""",
		group_name,
	)[0][0]
	members = [{"user": m.user, "display_name": m.display_name, "share_percent": m.share_percent} for m in group.members]
	return {
		"name": group.name,
		"group_name": group.group_name,
		"description": group.description,
		"owner_user": group.owner_user,
		"members": members,
		"total_expense": flt(total_expense),
	}


@frappe.whitelist()
def create_group(group_name, description=None, members=None):
	user = frappe.session.user
	doc = frappe.new_doc("Expense Group")
	doc.group_name = group_name
	doc.description = description
	doc.owner_user = user
	if members:
		import json
		member_list = json.loads(members) if isinstance(members, str) else members
		for m in member_list:
			doc.append("members", {
				"user": m.get("user"),
				"display_name": m.get("display_name", ""),
				"share_percent": flt(m.get("share_percent", 0)),
			})
	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "status": "success"}


@frappe.whitelist()
def settle_group_balance(group_name, from_user, to_user, amount):
	user = frappe.session.user
	group = frappe.get_doc("Expense Group", group_name)
	if not group.is_member(user):
		frappe.throw(_("Not a member"), frappe.PermissionError)

	doc = frappe.new_doc("Expense")
	doc.title = f"Settlement: {from_user} → {to_user}"
	doc.amount = flt(amount)
	doc.currency = "INR"
	doc.type = "Expense"
	doc.category = "Other"
	doc.transaction_date = frappe.utils.today()
	doc.paid_by = from_user
	doc.is_group_expense = 1
	doc.group = group_name
	doc.notes = f"Settlement payment"
	doc.created_via = "Mobile"
	doc.status = "Submitted"
	doc.insert(ignore_permissions=True)
	doc.submit()
	return {"status": "success", "name": doc.name}


@frappe.whitelist()
def update_profile(full_name=None, email=None):
	user = frappe.session.user
	user_doc = frappe.get_doc("User", user)
	if full_name:
		user_doc.full_name = full_name
		parts = full_name.split(" ", 1)
		user_doc.first_name = parts[0]
		user_doc.last_name = parts[1] if len(parts) > 1 else ""
	user_doc.save(ignore_permissions=True)
	return {"status": "success"}


@frappe.whitelist()
def get_profile():
	user = frappe.session.user
	user_doc = frappe.get_doc("User", user)
	return {
		"user": user,
		"full_name": user_doc.full_name,
		"email": user_doc.email,
		"user_image": user_doc.user_image,
	}


@frappe.whitelist()
def export_data(mode="personal", group=None):
	import csv, io
	user = frappe.session.user
	if mode == "personal":
		filters = {"paid_by": user, "is_group_expense": 0}
	else:
		filters = {"group": group, "is_group_expense": 1}
	records = frappe.get_all(
		"Expense",
		filters=filters,
		fields=["name", "title", "amount", "type", "category", "transaction_date", "paid_by", "notes", "status"],
		order_by="transaction_date desc",
	)
	output = io.StringIO()
	writer = csv.DictWriter(output, fieldnames=["name", "title", "amount", "type", "category", "transaction_date", "paid_by", "notes", "status"])
	writer.writeheader()
	writer.writerows([dict(r) for r in records])
	return {"csv": output.getvalue()}
