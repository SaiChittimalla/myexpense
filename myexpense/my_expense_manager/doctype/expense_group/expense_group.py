import frappe
from frappe.model.document import Document


class ExpenseGroup(Document):
	def before_save(self):
		if not self.owner_user:
			self.owner_user = frappe.session.user

	def is_member(self, user=None):
		user = user or frappe.session.user
		if self.owner_user == user:
			return True
		return any(m.user == user for m in self.members)
