<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal centered">
      <div>
        <form class="login" @submit.prevent="login">
          <div class="d-flex justify-content-center flex-column"></div>
          <h1>{{ $t('common.login') }}</h1>
          <p class="short-text" v-if="nonFieldError">{{ nonFieldError }}</p>
          <input required v-model="username" type="text" :placeholder="$t('auth.username')"/>
          <input required v-model="password" type="password" :placeholder="$t('auth.password')"/>
          <button type="submit">{{ $t('common.login') }}</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/useAuthStore'
import { useI18n } from 'vue-i18n'

export default {
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      username: "",
      password: "",

      nonFieldError: null,
      usernameError: null,
      passwordError: null,
    }
  },
  methods: {
    login() {
      this.nonFieldError = null
      let username = this.username
      let password = this.password
      const authStore = useAuthStore()
      authStore.login({username, password})
          .then(() => this.$router.push('/dashboard'))
          .catch(err => {
            console.log(err)
            if(err.response?.data) {
              const data = err.response.data
              if (data.non_field_errors && data.non_field_errors.length > 0) {
                this.nonFieldError = data.non_field_errors[0]
              } else if (data.detail) {
                this.nonFieldError = data.detail
              } else if (typeof data === 'string') {
                this.nonFieldError = data
              } else {
                this.nonFieldError = this.$t('auth.loginError')
              }
            } else {
              this.nonFieldError = this.$t('auth.networkError')
            }
          })
    },
    close() {
      this.$emit('close');
    },
    async logout() {
      try {
        const authStore = useAuthStore()
        await authStore.logout()
        this.$router.push('/')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    },
    showSettings() {
      this.isSettingsVisible = true
    },
    hideSettings() {
      this.isSettingsVisible = false
    }
  }
}
</script>

<style scoped>

form {
  padding: 33px 88px 33px;
}

input {
  width: 100%;
}

button {
  width: 100%;
  margin: 11px 0;
}
</style>