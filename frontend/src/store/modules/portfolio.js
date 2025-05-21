import { brokerApi } from '../broker-api'

export default {
	namespaced: true,

	state: {
		balance: 0,
		currency: 'RUB',
		loading: false,
		error: null
	},

	mutations: {
		SET_BALANCE(state, balance) {
			state.balance = balance
		},
		SET_CURRENCY(state, currency) {
			state.currency = currency
		},
		SET_LOADING(state, loading) {
			state.loading = loading
		},
		SET_ERROR(state, error) {
			state.error = error
		}
	},

	actions: {
		async fetchBalance({ commit }) {
			try {
				commit('SET_LOADING', true)
				const response = await brokerApi.get('/api/portfolio/balance')
				commit('SET_BALANCE', response.data.balance)
				commit('SET_CURRENCY', response.data.currency)
				commit('SET_ERROR', null)
			} catch (error) {
				commit('SET_ERROR', error.message)
			} finally {
				commit('SET_LOADING', false)
			}
		},

		async setSandboxBalance({ commit }, balance) {
			try {
				commit('SET_LOADING', true)
				await brokerApi.post('/api/portfolio/sandbox/balance', { balance })
				await this.dispatch('portfolio/fetchBalance')
				commit('SET_ERROR', null)
			} catch (error) {
				commit('SET_ERROR', error.message)
				throw error
			} finally {
				commit('SET_LOADING', false)
			}
		}
	}
} 