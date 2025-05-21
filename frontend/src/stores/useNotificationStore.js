import { defineStore } from 'pinia'
import { notify } from '@kyvg/vue3-notification'

export const useNotificationStore = defineStore('notification', {
	state: () => ({
		notifications: []
	}),

	actions: {
		notify(notification) {
			notify({
				title: notification.title,
				text: notification.text,
				type: notification.type || 'info',
				duration: notification.duration || 5000
			})

			this.notifications.push({
				...notification,
				id: Date.now(),
				timestamp: new Date()
			})
		},

		success(text, title = 'Success') {
			this.notify({
				title,
				text,
				type: 'success'
			})
		},

		error(text, title = 'Error') {
			this.notify({
				title,
				text,
				type: 'error'
			})
		},

		info(text, title = 'Info') {
			this.notify({
				title,
				text,
				type: 'info'
			})
		},

		warning(text, title = 'Warning') {
			this.notify({
				title,
				text,
				type: 'warning'
			})
		},

		clearNotifications() {
			this.notifications = []
		}
	}
}) 