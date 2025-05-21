import { defineStore } from 'pinia'
import axios from 'axios'
import { useNotificationStore } from './useNotificationStore'

const DEFAULT_CURRENCY = 'RUB'

export const usePortfolioStore = defineStore('portfolio', {
	state: () => ({
		balance: 0,
		currency: DEFAULT_CURRENCY,
		positions: [],
		expectedYield: {
			value: 0,
			relative: 0
		},
		loading: false,
		positionsLoading: false,
		error: null
	}),

	actions: {
		async fetchBalance() {
			try {
				this.loading = true
				this.error = null

				const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/portfolio/balance/`, {
					headers: {
						'Authorization': `Token ${localStorage.getItem('token')}`
					}
				})

				const balance = parseFloat(response.data.balance)
				this.balance = !isNaN(balance) ? balance : 0
				this.currency = response.data.currency || DEFAULT_CURRENCY

				return response.data
			} catch (error) {
				console.error('Error fetching balance:', error)
				this.error = error.response?.data?.error || error.message
				const notificationStore = useNotificationStore()
				notificationStore.error(`Failed to fetch balance: ${this.error}`)
				throw error
			} finally {
				this.loading = false
			}
		},

		async fetchPositions() {
			try {
				this.positionsLoading = true
				this.error = null

				const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/portfolio/positions/`, {
					headers: {
						'Authorization': `Token ${localStorage.getItem('token')}`
					}
				})

				this.positions = response.data.positions || []

				if (response.data.total && response.data.total.expected_yield) {
					this.expectedYield = response.data.total.expected_yield
				}

				return response.data
			} catch (error) {
				console.error('Error fetching positions:', error)
				this.error = error.response?.data?.error || error.message
				const notificationStore = useNotificationStore()
				notificationStore.error(`Failed to fetch positions: ${this.error}`)
				throw error
			} finally {
				this.positionsLoading = false
			}
		},

		async setSandboxBalance(balance) {
			try {
				this.loading = true
				this.error = null

				await axios.post(`${import.meta.env.VITE_API_URL}/trading/portfolio/sandbox/balance/`,
					{
						balance,
						provider: 'tinkoff',
						currency: 'rub'
					},
					{
						headers: {
							'Authorization': `Token ${localStorage.getItem('token')}`
						}
					}
				)

				await this.fetchBalance()

				const notificationStore = useNotificationStore()
				notificationStore.success('Balance updated successfully')
			} catch (error) {
				console.error('Error setting sandbox balance:', error)
				this.error = error.response?.data?.error || error.message
				const notificationStore = useNotificationStore()
				notificationStore.error(`Failed to set balance: ${this.error}`)
				throw error
			} finally {
				this.loading = false
			}
		}
	}
}) 