const ARCHIVE_REFRESH_EVENT = 'archive:updated'

export function notifyArchiveUpdated(detail = {}) {
  window.dispatchEvent(new CustomEvent(ARCHIVE_REFRESH_EVENT, { detail }))
}

export function subscribeToArchiveUpdates(handler) {
  if (typeof handler !== 'function') {
    return () => {}
  }

  const wrappedHandler = () => handler()
  window.addEventListener(ARCHIVE_REFRESH_EVENT, wrappedHandler)

  return () => {
    window.removeEventListener(ARCHIVE_REFRESH_EVENT, wrappedHandler)
  }
}
