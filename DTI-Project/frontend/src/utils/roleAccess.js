function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('current_user') || '{}')
  } catch {
    return {}
  }
}

export function canManageRecords() {
  const user = getStoredUser()
  return Boolean(user?.is_staff || user?.is_superuser)
}
