import frappe
from frappe import _
from frappe.utils import today, getdate, flt


@frappe.whitelist()
def get_dashboard(mode="personal", group=None):
	user = frappe.session.user
	if mode == "personal":
		return _personal_dashboard(user)
	return _group_dashboard(group, user)


def _personal_dashboard(user):
	expenses = frappe.get_all(
		"Expense",
		filters={"paid_by": user, "is_group_expense": 0, "status": ["!=", "Cancelled"]},
		fields=["name", "title", "amount", "type", "category", "transaction_date"],
		order_by="transaction_date desc",
		limit=10,
	)
	total_income = frappe.db.sql(
		"""SELECT COALESCE(SUM(amount), 0) FROM `tabExpense`
		   WHERE paid_by=%s AND type='Income' AND is_group_expense=0 AND status!='Cancelled'""",
		user,
	)[0][0]
	total_expense = frappe.db.sql(
		"""SELECT COALESCE(SUM(amount), 0) FROM `tabExpense`
		   WHERE paid_by=%s AND type='Expense' AND is_group_expense=0 AND status!='Cancelled'""",
		user,
	)[0][0]
	return {
		"mode": "personal",
		"total_income": flt(total_income),
		"total_expense": flt(total_expense),
		"balance": flt(total_income) - flt(total_expense),
		"recent_transactions": expenses,
	}


def _group_dashboard(group_name, user):
	if not group_name:
		frappe.throw(_("Group name is required"))
	group = frappe.get_doc("Expense Group", group_name)
	if not group.is_member(user):
		frappe.throw(_("Not a member of this group"), frappe.PermissionError)

	expenses = frappe.get_all(
		"Expense",
		filters={"group": group_name, "is_group_expense": 1, "status": ["!=", "Cancelled"]},
		fields=["name", "title", "amount", "type", "paid_by", "transaction_date"],
		order_by="transaction_date desc",
	)

	balances = _compute_group_balances(group_name)

	return {
		"mode": "group",
		"group": group_name,
		"members": [{"user": m.user, "display_name": m.display_name} for m in group.members],
		"recent_transactions": expenses[:10],
		"balances": balances,
		"settlements": _suggest_settlements(balances),
	}


def _compute_group_balances(group_name):
	"""Compute net balance for each member: positive = owed money, negative = owes money."""
	paid = frappe.db.sql(
		"""SELECT paid_by, COALESCE(SUM(amount), 0) as total
		   FROM `tabExpense`
		   WHERE `group`=%s AND is_group_expense=1 AND status!='Cancelled'
		   GROUP BY paid_by""",
		group_name,
		as_dict=True,
	)
	owed = frappe.db.sql(
		"""SELECT se.user, COALESCE(SUM(se.share_amount), 0) as total
		   FROM `tabSplit Entry` se
		   JOIN `tabExpense` e ON se.parent=e.name
		   WHERE e.`group`=%s AND e.is_group_expense=1 AND e.status!='Cancelled' AND se.settled=0
		   GROUP BY se.user""",
		group_name,
		as_dict=True,
	)
	balances = {}
	for row in paid:
		balances.setdefault(row.paid_by, 0)
		balances[row.paid_by] += flt(row.total)
	for row in owed:
		balances.setdefault(row.user, 0)
		balances[row.user] -= flt(row.total)
	return [{"user": u, "balance": b} for u, b in balances.items()]


def _suggest_settlements(balances):
	creditors = sorted([b for b in balances if b["balance"] > 0], key=lambda x: -x["balance"])
	debtors = sorted([b for b in balances if b["balance"] < 0], key=lambda x: x["balance"])
	settlements = []
	i, j = 0, 0
	creditors = [dict(b) for b in creditors]
	debtors = [dict(b) for b in debtors]
	while i < len(creditors) and j < len(debtors):
		amount = min(creditors[i]["balance"], -debtors[j]["balance"])
		settlements.append({"from": debtors[j]["user"], "to": creditors[i]["user"], "amount": flt(amount)})
		creditors[i]["balance"] -= amount
		debtors[j]["balance"] += amount
		if creditors[i]["balance"] == 0:
			i += 1
		if debtors[j]["balance"] == 0:
			j += 1
	return settlements


@frappe.whitelist()
def add_expense(title, amount, currency="INR", type="Expense", category=None,
				transaction_date=None, notes=None, is_group_expense=0,
				group=None, is_split=0, splits=None, attachment=None):
	user = frappe.session.user
	doc = frappe.new_doc("Expense")
	doc.title = title
	doc.amount = flt(amount)
	doc.currency = currency
	doc.type = type
	doc.category = category
	doc.transaction_date = transaction_date or today()
	doc.paid_by = user
	doc.notes = notes
	doc.is_group_expense = int(is_group_expense)
	doc.group = group if int(is_group_expense) else None
	doc.is_split = int(is_split)
	doc.attachment = attachment
	doc.created_via = "Mobile"
	doc.status = "Draft"

	if is_split and splits:
		import json
		split_list = json.loads(splits) if isinstance(splits, str) else splits
		for s in split_list:
			doc.append("splits", {
				"user": s.get("user"),
				"display_name": s.get("display_name", ""),
				"split_type": s.get("split_type", "Equal"),
				"share_percent": flt(s.get("share_percent", 0)),
				"share_amount": flt(s.get("share_amount", 0)),
				"settled": 0,
			})

	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "status": "success"}


@frappe.whitelist()
def get_history(mode="personal", group=None, type_filter=None,
				category=None, from_date=None, to_date=None,
				page=1, page_size=20):
	user = frappe.session.user
	filters = {"status": ["!=", "Cancelled"]}

	if mode == "personal":
		filters["paid_by"] = user
		filters["is_group_expense"] = 0
	else:
		if not group:
			frappe.throw(_("Group is required for group history"))
		filters["group"] = group
		filters["is_group_expense"] = 1

	if type_filter:
		filters["type"] = type_filter
	if category:
		filters["category"] = category
	if from_date:
		filters["transaction_date"] = [">=", from_date]
	if to_date:
		filters.setdefault("transaction_date", [])
		filters["transaction_date"] = ["between", [from_date or "2000-01-01", to_date]]

	page = int(page)
	page_size = int(page_size)
	records = frappe.get_all(
		"Expense",
		filters=filters,
		fields=["name", "title", "amount", "type", "category", "transaction_date", "paid_by", "group", "status"],
		order_by="transaction_date desc",
		limit=page_size,
		start=(page - 1) * page_size,
	)
	total = frappe.db.count("Expense", filters)
	return {"records": records, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist()
def delete_expense(name):
	doc = frappe.get_doc("Expense", name)
	if doc.status == "Submitted":
		frappe.throw(_("Cannot delete a submitted expense"))
	if doc.paid_by != frappe.session.user and not frappe.has_permission("Expense", "delete"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	doc.delete()
	return {"status": "success"}


@frappe.whitelist()
def get_categories():
	return [
		"Food & Dining", "Rent & Housing", "Transportation", "Utilities",
		"Entertainment", "Health & Medical", "Shopping", "Travel",
		"Education", "Salary", "Freelance", "Other",
	]


@frappe.whitelist()
def get_reports(mode="personal", group=None, year=None):
	from frappe.utils import now_datetime
	user = frappe.session.user
	year = year or now_datetime().year

	if mode == "personal":
		filters = {"paid_by": user, "is_group_expense": 0, "status": ["!=", "Cancelled"]}
	else:
		if not group:
			frappe.throw(_("Group required"))
		filters = {"group": group, "is_group_expense": 1, "status": ["!=", "Cancelled"]}

	monthly = frappe.db.sql(
		"""SELECT MONTH(transaction_date) as month,
		          SUM(CASE WHEN type='Income' THEN amount ELSE 0 END) as income,
		          SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END) as expense
		   FROM `tabExpense`
		   WHERE YEAR(transaction_date)=%s AND status!='Cancelled'
		   {extra}
		   GROUP BY MONTH(transaction_date)
		   ORDER BY month""".format(
			extra="AND paid_by=%s AND is_group_expense=0" if mode == "personal" else "AND `group`=%s AND is_group_expense=1"
		),
		(year, user if mode == "personal" else group),
		as_dict=True,
	)

	by_category = frappe.db.sql(
		"""SELECT category, SUM(amount) as total
		   FROM `tabExpense`
		   WHERE type='Expense' AND status!='Cancelled'
		   {extra}
		   GROUP BY category
		   ORDER BY total DESC""".format(
			extra="AND paid_by=%s AND is_group_expense=0" if mode == "personal" else "AND `group`=%s AND is_group_expense=1"
		),
		user if mode == "personal" else group,
		as_dict=True,
	)

	return {"monthly": monthly, "by_category": by_category, "year": year}
