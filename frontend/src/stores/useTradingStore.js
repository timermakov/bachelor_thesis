import { defineStore } from 'pinia'
import axios from 'axios'

export const useTradingStore = defineStore('trading', {
	state: () => ({
		positions: [],
		status: '',
		loading: false
	}),

	getters: {
		allPositions: (state) => state.positions
	},

	actions: {
		async loadPositions() {
			try {
				this.status = 'loading'
				this.loading = true

				const response = await axios({
					url: `${import.meta.env.VITE_API_URL}/trading/positions/`,
					method: 'GET'
				})

				this.positions = response.data
				this.status = 'success'
				this.loading = false

				return Promise.resolve(response)
			} catch (error) {
				this.status = 'error'
				this.loading = false
				return Promise.reject(error)
			}
		},

		async editPosition(position) {
			try {
				const response = await axios({
					url: `${import.meta.env.VITE_API_URL}/trading/positions/${position.id}/`,
					data: position,
					method: 'PUT'
				})

				const index = this.positions.findIndex(p => p.id === position.id)
				if (index !== -1) {
					this.positions[index] = response.data
				}

				return Promise.resolve(response)
			} catch (error) {
				return Promise.reject(error)
			}
		},

		async createPosition(position) {
			try {
				const response = await axios({
					url: `${import.meta.env.VITE_API_URL}/trading/positions/`,
					data: position,
					method: 'POST'
				})

				this.positions.push(response.data)

				return Promise.resolve(response)
			} catch (error) {
				return Promise.reject(error)
			}
		},

		async removePosition(position) {
			try {
				await axios({
					url: `${import.meta.env.VITE_API_URL}/trading/positions/${position.id}/`,
					method: 'DELETE'
				})

				this.positions = this.positions.filter(p => p.id !== position.id)

				return Promise.resolve()
			} catch (error) {
				return Promise.reject(error)
			}
		}
	}
}) 