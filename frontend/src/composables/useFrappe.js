// Thin wrapper around Frappe's fetch-based API
// __API_BASE__ is injected by vite.mobile.config.js for the APK build.
// In dev/Frappe-hosted mode it falls back to relative URLs.
const API_ROOT = (typeof __API_BASE__ !== 'undefined' && __API_BASE__) ? __API_BASE__ : ''
const BASE = `${API_ROOT}/api/method`

async function call(method, params = {}) {
  const res = await fetch(`${BASE}/${method}`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || getCsrf(),
    },
    body: JSON.stringify(params),
  })
  if (!res.ok) {
    if (res.status === 403 || res.status === 401) {
      const err = { status: res.status }
      throw Object.assign(new Error('Unauthenticated'), err)
    }
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.exc_type || err?.message || `HTTP ${res.status}`)
  }
  const data = await res.json()
  return data.message ?? data
}

function getCsrf() {
  return document.cookie.split(';').find(c => c.trim().startsWith('csrf_token='))?.split('=')[1] || ''
}

async function get(method, params = {}) {
  const qs = new URLSearchParams(params).toString()
  const res = await fetch(`${BASE}/${method}${qs ? '?' + qs : ''}`, {
    headers: { 'X-Frappe-CSRF-Token': getCsrf() },
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  return data.message ?? data
}

export function useFrappe() {
  return { call, get }
}

export async function getLoggedUser() {
  try {
    // Use our own whitelisted endpoint — frappe.auth.get_logged_user is not
    // whitelisted for guest access in Frappe 15.
    const data = await call('myexpense.api.auth.get_session_user')
    const user = typeof data === 'string' ? data : data?.message
    return (user && user !== 'Guest') ? user : null
  } catch {
    return null
  }
}

export async function login(usr, pwd) {
  const res = await fetch(`${API_ROOT}/api/method/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Frappe-CSRF-Token': getCsrf(),
    },
    body: new URLSearchParams({ usr, pwd }),
  })
  const data = await res.json()
  if (!res.ok || data.message !== 'Logged In') {
    throw new Error(data._server_messages
      ? JSON.parse(JSON.parse(data._server_messages)[0]).message
      : data.message || 'Login failed')
  }
  return data
}

export async function logout() {
  await fetch(`${API_ROOT}/api/method/logout`, { method: 'POST' })
}
