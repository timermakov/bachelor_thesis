import axios from 'axios'
import Vue from "vue";

export default {
    state: {
        status: '',
        token: localStorage.getItem('token') || '',
        // user: {}
    },
    mutations: {
        auth_request(state) {
            state.status = 'loading'
        },
        auth_success(state, token) {
            state.status = 'success'
            state.token = token
        },
        auth_error(state) {
            state.status = 'error'
        },
        logout(state) {
            state.status = ''
            state.token = ''
        }
    },
    actions: {
        login({commit}, user) {
            return new Promise((resolve, reject) => {
                commit('auth_request')
                axios({
                    url: `${process.env.VUE_APP_API_URL}/auth/login/`,
                    data: user,
                    method: 'POST'
                }).then(response => {
                    const token = response.data.key
                    localStorage.setItem('token', token)
                    axios.defaults.headers.common['Authorization'] = `Token ${token}`
                    commit('auth_success', token)
                    Vue.notify({
                        text: `Welcome, ${user.username}!`,
                        type: 'success'
                    })
                    resolve(response)
                }).catch(err => {
                    commit('auth_error')
                    localStorage.removeItem('token')
                    reject(err)
                })
            })
        },
        register({commit}, user) {
            return new Promise((resolve, reject) => {
                commit('auth_request')
                axios({
                    url: `${process.env.VUE_APP_API_URL}/auth/signup/`,
                    data: user,
                    method: 'POST'
                }).then(response => {
                    const token = response.data.key
                    localStorage.setItem('token', token)
                    axios.defaults.headers.common['Authorization'] = `Token ${token}`
                    commit('auth_success', token)
                    Vue.notify({
                        text: `Welcome, ${user.username}!`,
                        type: 'success'
                    })
                    resolve(response)
                }).catch(err => {
                    commit('auth_error', err)
                    localStorage.removeItem('token')
                    reject(err)
                })
            })
        },
        logout({commit}) {
            return new Promise(resolve => {
                commit('logout')
                localStorage.removeItem('token')
                delete axios.defaults.headers.common['Authorization']
                Vue.notify({
                    text: `Bye!`,
                })
                resolve()
            })
        }
    },
    getters: {
        isLoggedIn: state => !!state.token,
        authStatus: state => state.status
    }
}