import { apiClient } from '@/services/http/clients'

function getLocalUser() {
  try {
    return JSON.parse(localStorage.getItem('current_user') || '{}')
  } catch {
    return {}
  }
}

export async function fetchSidebarData(apiEndpoint = '') {
  const localUser = getLocalUser()

  const [profileResult, sidebarResult] = await Promise.allSettled([
    apiClient.get('/api/user-app/auth/profile/'),
    apiEndpoint ? apiClient.get(apiEndpoint) : Promise.resolve({ data: null }),
  ])

  const profile = profileResult.status === 'fulfilled' ? profileResult.value.data : {}
  const sidebarPayload = sidebarResult.status === 'fulfilled' ? sidebarResult.value.data : null

  const roles = profile?.roles || {}

  const isStaff = Boolean(sidebarPayload?.user?.is_staff ?? roles.is_staff)
  const isSuperuser = Boolean(sidebarPayload?.user?.is_superuser ?? roles.is_superuser)
  const userId = Number(sidebarPayload?.user?.id ?? profile?.id ?? localUser?.id ?? 0)

  return {
    user: {
      id: userId,
      is_staff: isStaff,
      is_superuser: isSuperuser,
    },
    menu_sections: sidebarPayload?.menu_sections || null,
  }
}

