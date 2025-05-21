import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'
import Portfolio from '../views/Portfolio.vue'
import Analysis from '../views/Analysis.vue'
import Strategies from '../views/Strategies.vue'

const routes = [
	{
		path: '/',
		name: 'Home',
		component: Home
	},
	{
		path: '/dashboard',
		name: 'Dashboard',
		component: Dashboard,
		meta: {
			requiredAuth: true
		}
	},
	{
		path: '/portfolio',
		name: 'Portfolio',
		component: Portfolio,
		meta: {
			requiredAuth: true
		}
	},
	{
		path: '/analysis',
		name: 'Analysis',
		component: Analysis,
		meta: {
			requiredAuth: true
		}
	},
	{
		path: '/strategies',
		name: 'Strategies',
		component: Strategies,
		meta: {
			requiredAuth: true
		}
	},
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

router.beforeEach((to, from) => {
	const isLoggedIn = localStorage.getItem('token') ? true : false

	if (to.meta.requiredAuth && !isLoggedIn) {
		return { path: '/', query: { login: true } }
	}
})

export default router