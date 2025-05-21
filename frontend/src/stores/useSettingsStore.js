import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
	state: () => ({
		isSandbox: true,
		language: localStorage.getItem('locale') || 'ru',
		accountId: null,
		provider: null,
	}),

	actions: {
		setSandboxMode(value) {
			this.isSandbox = value
		},

		setLanguage(lang) {
			this.language = lang
			localStorage.setItem('locale', lang)
		},

		setAccount(accountId, provider) {
			this.accountId = accountId
			this.provider = provider
		}
	}
}) 