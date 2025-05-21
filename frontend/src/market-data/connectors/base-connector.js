// Base connector interface for market data providers
export class BaseConnector {
	constructor(config) {
		this.config = config;
	}

	async getPrice(symbol) {
		throw new Error('Method not implemented');
	}

	async getDailyStats(symbol) {
		throw new Error('Method not implemented');
	}

	async getServerTime() {
		throw new Error('Method not implemented');
	}

	async getSymbols() {
		throw new Error('Method not implemented');
	}
} 