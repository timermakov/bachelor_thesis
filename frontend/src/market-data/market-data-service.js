import { TinkoffConnector } from './connectors/tinkoff-connector';

export class MarketDataService {
	constructor() {
		this.connectors = new Map();
		this.activeConnector = null;
	}

	initializeConnectors(configs) {
		if (configs.tinkoff) {
			this.connectors.set('tinkoff', new TinkoffConnector(configs.tinkoff));
		}
	}

	setActiveConnector(connectorName) {
		const connector = this.connectors.get(connectorName);
		if (!connector) {
			throw new Error(`Connector ${connectorName} not found`);
		}
		this.activeConnector = connector;
	}

	async getPrice(symbol) {
		if (!this.activeConnector) {
			throw new Error('No active connector set');
		}
		return this.activeConnector.getPrice(symbol);
	}

	async getDailyStats(symbol) {
		if (!this.activeConnector) {
			throw new Error('No active connector set');
		}
		return this.activeConnector.getDailyStats(symbol);
	}

	async getServerTime() {
		if (!this.activeConnector) {
			throw new Error('No active connector set');
		}
		return this.activeConnector.getServerTime();
	}

	async getSymbols() {
		if (!this.activeConnector) {
			throw new Error('No active connector set');
		}
		return this.activeConnector.getSymbols();
	}

	getAvailableConnectors() {
		return Array.from(this.connectors.keys());
	}
} 