import frappe
from frappe.model.document import Document
from frappe import _


class Expense(Document):
	def validate(self):
		if self.is_group_expense and not self.group:
			frappe.throw(_("Expense Group is required for group expenses"))
		if not self.is_group_expense:
			self.group = None
			self.is_split = 0
			self.splits = []
		if self.is_split and self.splits:
			self._validate_splits()
		if not self.paid_by:
			self.paid_by = frappe.session.user

	def _validate_splits(self):
		total = sum(s.share_amount for s in self.splits)
		if abs(total - self.amount) > 0.01:
			frappe.throw(_("Split amounts {0} must equal total amount {1}").format(total, self.amount))

	def before_submit(self):
		self.status = "Submitted"

	def on_cancel(self):
		self.status = "Cancelled"
