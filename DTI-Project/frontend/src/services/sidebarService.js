import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.protocol + '//' + window.location.hostname + ':8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

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
