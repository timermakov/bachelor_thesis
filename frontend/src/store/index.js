import Vue from 'vue'
import Vuex from 'vuex'

import auth from "./modules/auth";
import trading from './modules/trading'
import notification from "./modules/notification";
import portfolio from './modules/portfolio'

Vue.use(Vuex)

export default new Vuex.Store({
	modules: {
		auth,
		trading,
		notification,
		portfolio
	}
})