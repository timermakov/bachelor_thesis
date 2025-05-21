<template>
  <div id="app">
    <div class="header">
      <div class="header-top">
        <h1>{{ $t('global.appName') }}</h1>
		<div class="broker-status-container">
            <BrokerStatus />
        </div>
		<div class="header-buttons">
            <button @click="showSettings">{{ $t('common.settings') }}</button>
            <button @click="logout">{{ $t('common.logout') }}</button>
        </div>
      </div>
      <div class="navigation-container">
        <div class="navigation">
          <router-link to="/dashboard" class="nav-link">{{ $t('navigation.dashboard') }}</router-link>
		  <router-link to="/strategies" class="nav-link">{{ $t('navigation.strategies') }}</router-link>
		  <router-link to="/analysis" class="nav-link">{{ $t('navigation.analysis') }}</router-link>
		  <router-link to="/portfolio" class="nav-link">{{ $t('navigation.portfolio') }}</router-link>
        </div>
      </div>
    </div>
    <div class="main-content">
      <router-view />
    </div>
    <notifications position="bottom center" style="margin-bottom: 10vh" />
    <Modal v-if="isSettingsVisible" @close="hideSettings">
      <h2>{{ $t('settings.title') }}</h2>
      <div class="settings-content">
        <LanguageSwitcher />
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap/dist/js/bootstrap.min"
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/useAuthStore'
import { useNotificationStore } from './stores/useNotificationStore'
import BrokerStatus from './components/BrokerStatus.vue'
import Modal from './components/Modal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const isSettingsVisible = ref(false)

const logout = async () => {
  try {
    await authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

const showSettings = () => {
  isSettingsVisible.value = true
}

const hideSettings = () => {
  isSettingsVisible.value = false
}

onMounted(() => {
  axios.interceptors.response.use(
    response => {
      return response
    },
    err => {
      return new Promise(() => {
        if (err.status === 401 && err.config && !err.config.__isRetryRequest) {
          authStore.logout()
        } else if (err.response && err.response.status >= 500) {
          notificationStore.error(`${err.response.status} Server Error`)
        }
        throw err
      })
    }
  )
})
</script>

<style>
#app {
  font-family: "Montserrat", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2, h3, h4, h5, h6 {
  font-family: "Podkova", serif;
  font-weight: bold;
}

p {
  font-size: 18px;
}

input {
  background: #FFFFFF;
  border: 1px solid #000000;
  margin: 11px 0;
  height: 44px;
  text-align: center;
  font-family: "Podkova", Serif;
  font-size: 18px;
}

button {
  height: 40px;
  width: 150px;
  background: white;
  border: solid #2c3e50 1px;
  font-family: "Montserrat", sans-serif;
  font-weight: 500;
  border-radius: 3px;
  font-style: normal;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #f5f5f5;
}

.long-text {
  color: #5EBA89;
}

.short-text {
  color: #CE3D4E;
}

.long-bg {
  background-color: #5EBA89;
}

.short-bg {
  background-color: #CE3D4E;
}

.centered {
  position: fixed;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.modal-backdrop {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: #FFFFFF;
  box-shadow: 2px 2px 20px 1px;
  overflow-x: auto;
  display: flex;
  flex-direction: column;
  max-width: 385px;
  height: auto;
}

.header {
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  padding: 10px 20px;
  width: 100%;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  margin-bottom: 15px;
}

.navigation-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.navigation {
  display: flex;
  gap: 20px;
  justify-content: center;
  padding: 10px 0;
  border-bottom: 1px solid #e9ecef;
  width: 80%;
  max-width: 600px;
}

.header-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  flex-direction: column;
  width: 320px;
}

.broker-status-container {
  width: 100%;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-link {
  color: #2c3e50;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.router-link-active {
  color: #4CAF50;
  border-bottom: 2px solid #4CAF50;
}

.main-content {
  margin-top: 20px;
  padding: 0 20px;
}

@media (max-width: 768px) {
  #app {
    margin-top: 20px;
  }

  .header-top {
    flex-direction: column;
    align-items: center;
  }
  
  .navigation {
    flex-wrap: wrap;
    gap: 10px;
    width: 100%;
    justify-content: space-around;
    padding: 5px 0;
  }
  
  .nav-link {
    font-size: 14px;
    padding: 5px;
    white-space: nowrap;
  }
  
  .header-buttons {
    width: 100%;
    flex-direction: row;
    justify-content: center;
    margin-top: 10px;
  }
  
  .broker-status-container {
    text-align: center;
    margin: 10px 0;
  }
  
  button {
    width: 120px;
    height: 36px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .navigation {
    gap: 5px;
  }
  
  .nav-link {
    font-size: 13px;
    padding: 4px;
  }
  
  .header-buttons {
    gap: 5px;
  }
  
  button {
    width: 110px;
  }
}

.settings-content {
  padding: 1rem 2rem;
  min-width: 300px;
}
</style>
