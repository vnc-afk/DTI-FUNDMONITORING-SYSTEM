import { createApp } from 'vue'
import App from './App.vue'
import router from '@/router'
import pinia from '@/stores'
import { setupGlobalApiFeedback } from '@/services/apiFeedbackService'
import '@/assets/css/index.css'

const savedTheme = localStorage.getItem('dti-theme-preference')
if (savedTheme === 'light' || savedTheme === 'dark') {
	document.documentElement.setAttribute('data-theme', savedTheme)
}

setupGlobalApiFeedback(pinia)

// Create and mount app
const app = createApp(App)
app.use(router)
app.use(pinia)
app.mount('#app')
