import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Axios from 'axios'
import Notifications from '@kyvg/vue3-notification'
import i18n from './i18n'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Notifications)
app.use(i18n)

app.config.globalProperties.$http = Axios
const token = localStorage.getItem('token')
if (token) {
	Axios.defaults.headers.common['Authorization'] = `Token ${token}`
}

const locale = i18n.global.locale.value
const appName = i18n.global.t('global.appName')
app.config.globalProperties.$pageTitle = appName

app.mount('#app')
