<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal centered">
      <div>
        <form @submit.prevent="signup">
          <h1>{{ $t('common.signup') }}</h1>
          <div class="fields">
            <input id="username" type="text" :placeholder="$t('auth.username')" v-model="username" required autofocus>
            <p class="error" v-if="usernameError">{{ usernameError }}</p>
            <input id="email" type="email" placeholder="email" v-model="email" required>
            <p class="error" v-if="emailError">{{ emailError }}</p>
            <input id="password" type="password" :placeholder="$t('auth.password')" v-model="password1" required>
            <p class="error" v-if="password1Error">{{ password1Error }}</p>
            <input id="password-confirm" type="password" placeholder="repeat password" v-model="password2"
                   required>
            <p class="error" v-if="password2Error">{{ password2Error }}</p>
          </div>
          <button type="submit">{{ $t('common.signup') }}</button>
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
      email: "",
      password1: "",
      password2: "",

      nonFieldError: null,
      usernameError: null,
      emailError: null,
      password1Error: null,
      password2Error: null,
    }
  },
  methods: {
    signup() {
      let data = {
        username: this.username,
        email: this.email,
        password1: this.password1,
        password2: this.password2,
      }
      const authStore = useAuthStore()
      authStore.register(data)
          .then(() => this.$router.push('/dashboard'))
          .catch(err => {
            console.log(err.response)
            if (err.response) {
              let data = err.response.data
              this.nonFieldError = (data.nonFieldErrors !== undefined) ? data.nonFieldErrors[0] : null
              this.usernameError = (data.username !== undefined) ? data.username[0] : null
              this.emailError = (data.email !== undefined) ? data.email[0] : null
              this.password1Error = (data.password1 !== undefined) ? data.password1[0] : null
              this.password2Error = (data.password2 !== undefined) ? data.password2[0] : null
            }
          })
    },
    close() {
      this.$emit('close');
    },
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

.fields {
  margin: 11px 0;
}

button {
  width: 100%;
  margin: 11px 0;
}

.error {
  font-size: 11px;
  color: red;
}
</style>