import axios from 'axios';

const figiCache = {};

const client = {
	prices: async (symbol) => {
		try {
			const symbolStr = typeof symbol === 'object' ? symbol.symbol : symbol;

			const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/market-data/price/`, {
				params: { symbol: symbolStr }
			});
			return response.data;
		} catch (error) {
			console.error('Error fetching prices:', error);
			throw error;
		}
	},

	getFigiByTicker: async (ticker) => {
		try {
			if (figiCache[ticker]) {
				return figiCache[ticker];
			}

			const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/market-data/figi/`, {
				params: { ticker: ticker }
			});

			figiCache[ticker] = response.data;
			return response.data;
		} catch (error) {
			console.error('Error fetching FIGI for ticker:', error);
			throw error;
		}
	},

	time: async () => {
		try {
			const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/market-data/time/`);
			return response.data;
		} catch (error) {
			console.error('Error fetching time:', error);
			throw error;
		}
	},

	dailyStats: async (symbol) => {
		try {
			const symbolStr = typeof symbol === 'object' ? symbol.symbol : symbol;

			const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/market-data/stats/`, {
				params: { symbol: symbolStr }
			});
			return response.data;
		} catch (error) {
			console.error('Error fetching daily stats:', error);
			throw error;
		}
	},

	symbols: async () => {
		try {
			const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/market-data/symbols/`);
			return response.data;
		} catch (error) {
			console.error('Error fetching symbols:', error);
			throw error;
		}
	},

	getProviders: async () => {
		try {
			const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/market-data/providers/`);
			return response.data;
		} catch (error) {
			console.error('Error fetching providers:', error);
			throw error;
		}
	},

	connectProvider: async (providerName) => {
		try {
			const response = await axios.post(`${import.meta.env.VITE_API_URL}/trading/market-data/providers/${providerName}/connect/`);
			return response.data;
		} catch (error) {
			console.error(`Error connecting to ${providerName}:`, error);
			throw error;
		}
	},

	disconnectProvider: async (providerName) => {
		try {
			const response = await axios.post(`${import.meta.env.VITE_API_URL}/trading/market-data/providers/${providerName}/disconnect/`);
			return response.data;
		} catch (error) {
			console.error(`Error disconnecting from ${providerName}:`, error);
			throw error;
		}
	},

	placeSandboxOrder: async ({ accountId, figi, direction, quantity = 1 }) => {
		try {
			const response = await axios.post(`${import.meta.env.VITE_API_URL}/trading/sandbox/order/`, {
				account_id: accountId,
				figi,
				direction,
				quantity
			});
			return response.data;
		} catch (error) {
			console.error('Error placing sandbox order:', error);
			throw error;
		}
	}
};

export default client;