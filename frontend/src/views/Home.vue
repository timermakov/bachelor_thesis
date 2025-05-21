<template>
  <div>
    <div class="centered">
      <div class="auth-buttons">
        <button @click="showLogin" id="login-button">{{ $t('common.login') }}</button>
        <button @click="showSignup" id="signup-button">{{ $t('common.signup') }}</button>
      </div>

    </div>
    <LogIn @close="hideLogin" v-show="isLoginVisible"/>
    <SignUp @close="hideSignup" v-show="isSignupVisible"/>
  </div>
</template>

<script>
import LogIn from "@/components/Auth/LogIn";
import SignUp from "@/components/Auth/SignUp";
import { useAuthStore } from '@/stores/useAuthStore'

export default {
  title: 'Welcome',
  components: {
    LogIn,
    SignUp,
  },
  data() {
    return {
      isLoginVisible: false,
      isSignupVisible: false,
    }
  },
  mounted() {
    const authStore = useAuthStore()
    if (authStore.isLoggedIn) {
      this.$router.push('/dashboard')
    }
  },
  methods: {
    showLogin() {
      this.isSignupVisible = false
      this.isLoginVisible = true
    },
    showSignup() {
      this.isLoginVisible = false
      this.isSignupVisible = true
    },
    hideLogin() {
      this.isLoginVisible = false
    },
    hideSignup() {
      this.isSignupVisible = false
    }
  }
}
</script>

<style scoped>


h1 {
  font-weight: bold;
  font-size: 80px;
}

.auth-buttons {
  margin-top: 11px;
}

button {
  margin: 0 16px;
}

#signup-button {
  background: linear-gradient(161.4deg, rgba(255, 236, 67, 0) -15.4%, #FFEC43 95.93%);
}


</style>