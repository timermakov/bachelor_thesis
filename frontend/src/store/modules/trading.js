import axios from "axios";
import Vue from 'vue'

export default {
	state: {
		positions: [],
		symbolOptions: null,
	},
	mutations: {
		setPositions(state, positions) {
			state.positions = positions
		},
		setSymbolOptions(state, options) {
			state.symbolOptions = options
		},
		addPosition(state, position) {
			state.positions.push(position)
		},
		editPosition(state, position) {
			const index = state.positions.findIndex(pos => pos.id === position.id)
			state.positions.splice(index, 1, position)
		},
		removePosition(state, position) {
			const index = state.positions.indexOf(position)
			if (index > -1) state.positions.splice(index, 1)
		}
	},
	actions: {
		loadPositions({ commit }) {
			axios(`${process.env.VUE_APP_API_URL}/trading/positions/`)
				.then(response => {
					const data = response.data
					commit('setPositions', data)
				}).catch(err => {
					return Promise.reject(err)
				})
		},
		createPosition({ commit }, position) {
			return new Promise((resolve, reject) => {
				axios(`${process.env.VUE_APP_API_URL}/trading/positions/`, {
					data: position,
					method: 'POST',
				}).then(response => {
					const data = response.data
					Vue.notify({
						text: `Position ${data.baseAsset}/${data.quoteAsset} successfully created.`,
						type: 'success'
					})
					commit('addPosition', data)
					resolve(response)
				}).catch(error => {
					Vue.notify({ text: 'An error has occurred during creating', type: 'error' })
					reject(error)
				})
			})
		},
		editPosition({ commit }, position) {
			return new Promise((resolve, reject) => {
				axios(`${process.env.VUE_APP_API_URL}/trading/positions/${position.id}/`, {
					method: 'PUT',
					data: position,
				}).then(response => {
					commit('editPosition', position)
					Vue.notify({
						text: `Position ${position.baseAsset}/${position.quoteAsset} saved.`,
					})
					resolve(response)
				}).catch(error => {
					Vue.notify({ text: 'An error has occurred during editing', type: 'error' })
					reject(error)
				})
			})

		},
		removePosition({ commit }, position) {
			axios(`${process.env.VUE_APP_API_URL}/trading/positions/${position.id}/`, {
				method: 'DELETE',
			}).then(() => {
				commit('removePosition', position)
			}).catch(() => {
				Vue.notify({ text: 'An error has occurred during removing', type: 'error' })
			})
		},
	},
	getters: {
		positions: state => state.positions,
		symbolOptions: state => state.symbolOptions
	}
}