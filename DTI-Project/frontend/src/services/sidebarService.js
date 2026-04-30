import { apiClient } from '@/services/http/clients'

function getLocalUser() {
  try {
    return JSON.parse(localStorage.getItem('current_user') || '{}')
  } catch {
    return {}
  }
}

function computeDisplayName(profile, localUser, sidebarUser) {
  const firstName = String(
    sidebarUser?.first_name ?? profile?.first_name ?? localUser?.first_name ?? ''
  ).trim()
  const lastName = String(
    sidebarUser?.last_name ?? profile?.last_name ?? localUser?.last_name ?? ''
  ).trim()
  const fullName = `${firstName} ${lastName}`.trim()

  if (fullName) {
    return fullName
  }

  return String(
    sidebarUser?.display_name ??
    sidebarUser?.full_name ??
    profile?.display_name ??
    profile?.full_name ??
    localUser?.display_name ??
    localUser?.full_name ??
    sidebarUser?.username ??
    profile?.username ??
    localUser?.username ??
    'User'
  ).trim() || 'User'
}

function computeRoleLabel(sidebarUser, isStaff, isSuperuser) {
  const rawRole = String(
    sidebarUser?.role_label ??
    sidebarUser?.role ??
    ''
  ).trim()

  if (rawRole) {
    return rawRole
  }

  if (isSuperuser) return 'Superuser'
  if (isStaff) return 'Staff'
  return 'User'
}

export async function fetchSidebarData(apiEndpoint = '') {
  const localUser = getLocalUser()

  const [profileResult, sidebarResult] = await Promise.allSettled([
    apiClient.get('/api/user-app/auth/profile/'),
    apiEndpoint ? apiClient.get(apiEndpoint) : Promise.resolve({ data: null }),
  ])

  const profile = profileResult.status === 'fulfilled' ? profileResult.value.data : {}
  const sidebarPayload = sidebarResult.status === 'fulfilled' ? sidebarResult.value.data : null
  const sidebarUser = sidebarPayload?.user || null

  const roles = profile?.roles || {}

  const isStaff = Boolean(sidebarUser?.is_staff ?? profile?.is_staff ?? roles.is_staff ?? localUser?.is_staff)
  const isSuperuser = Boolean(
    sidebarUser?.is_superuser ?? profile?.is_superuser ?? roles.is_superuser ?? localUser?.is_superuser
  )
  const userId = Number(sidebarUser?.id ?? profile?.id ?? localUser?.id ?? 0)
  const displayName = computeDisplayName(profile, localUser, sidebarUser)
  const roleLabel = computeRoleLabel(sidebarUser, isStaff, isSuperuser)

  return {
    user: {
      id: userId,
      is_staff: isStaff,
      is_superuser: isSuperuser,
      display_name: displayName,
      role_label: roleLabel,
    },
    menu_sections: sidebarPayload?.menu_sections || null,
  }
}

