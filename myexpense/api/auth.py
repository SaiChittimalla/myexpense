import frappe


@frappe.whitelist(allow_guest=True)
def get_session_user():
    """Returns current session user. Returns 'Guest' if not logged in."""
    return frappe.session.user


@frappe.whitelist(allow_guest=True)
def get_csrf_token():
    return {"csrf_token": frappe.local.session.get("csrf_token", "")}
