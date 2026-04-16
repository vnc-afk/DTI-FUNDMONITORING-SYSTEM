import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export const useSharedStore = defineStore('shared', () => {
  const data = ref({})
  const loadingFlags = ref({})

  const keys = computed(() => Object.keys(data.value))

  function setShared(key, value) {
    if (!key) return
    data.value[key] = value
  }

  function setManyShared(payload = {}) {
    if (!payload || typeof payload !== 'object') return
    Object.keys(payload).forEach((key) => {
      data.value[key] = payload[key]
    })
  }

  function getShared(key, fallback = null) {
    if (!key) return fallback
    return Object.prototype.hasOwnProperty.call(data.value, key) ? data.value[key] : fallback
  }

  function removeShared(key) {
    if (!key || !Object.prototype.hasOwnProperty.call(data.value, key)) return
    delete data.value[key]
  }

  function clearShared() {
    data.value = {}
  }

  function setLoadingFlag(key, value) {
    if (!key) return
    loadingFlags.value[key] = Boolean(value)
  }

  function isLoading(key) {
    return Boolean(loadingFlags.value[key])
  }

  function clearLoadingFlags() {
    loadingFlags.value = {}
  }

  return {
    data,
    loadingFlags,
    keys,
    setShared,
    setManyShared,
    getShared,
    removeShared,
    clearShared,
    setLoadingFlag,
    isLoading,
    clearLoadingFlags,
  }
})
