export default {
    state: {
        notificationList: []
    },
    mutations: {
        addNotification(state, payload) {
            state.notificationList.push(payload)
        },
        removeNotification(state, payload) {
            state.notificationList = state.notificationList.filter(notif => notif.text !== payload.text)
        }
    },
    getters: {
        notificationList: state => state.notificationList
    },
}