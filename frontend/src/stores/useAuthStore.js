import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
	state: () => ({
		status: '',
		token: localStorage.getItem('token') || '',
	}),

	getters: {
		isLoggedIn: (state) => !!state.token,
		authStatus: (state) => state.status
	},

	actions: {
		async login(user) {
			try {
				this.status = 'loading'

				const response = await axios({
					url: `${import.meta.env.VITE_API_URL}/auth/login/`,
					data: user,
					method: 'POST'
				})

				const token = response.data.key
				localStorage.setItem('token', token)
				axios.defaults.headers.common['Authorization'] = `Token ${token}`

				this.status = 'success'
				this.token = token

				return Promise.resolve(response)
			} catch (error) {
				this.status = 'error'
				localStorage.removeItem('token')
				return Promise.reject(error)
			}
		},

		async register(user) {
			try {
				this.status = 'loading'

				const response = await axios({
					url: `${import.meta.env.VITE_API_URL}/auth/signup/`,
					data: user,
					method: 'POST'
				})

				const token = response.data.key
				localStorage.setItem('token', token)
				axios.defaults.headers.common['Authorization'] = `Token ${token}`

				this.status = 'success'
				this.token = token

				return Promise.resolve(response)
			} catch (error) {
				this.status = 'error'
				localStorage.removeItem('token')
				return Promise.reject(error)
			}
		},

		logout() {
			this.status = ''
			this.token = ''
			localStorage.removeItem('token')
			delete axios.defaults.headers.common['Authorization']
		}
	}
})