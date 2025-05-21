import axios from 'axios';
import { BaseConnector } from './base-connector';

export class TinkoffConnector extends BaseConnector {
	constructor(config) {
		super(config);
		this.baseUrl = 'https://sandbox-invest-public-api.tinkoff.ru/rest';
		this.token = config.token;
	}

	async getPrice(symbol) {
		try {
			const response = await axios.post(`${this.baseUrl}/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices`, {
				instrumentIds: [symbol]
			}, {
				headers: {
					'Authorization': `Bearer ${this.token}`
				}
			});
			return {
				symbol: symbol,
				price: response.data.lastPrices[0].price
			};
		} catch (error) {
			console.error('Error fetching Tinkoff price:', error);
			throw error;
		}
	}

	async getDailyStats(symbol) {
		try {
			const response = await axios.post(`${this.baseUrl}/tinkoff.public.invest.api.contract.v1.MarketDataService/GetCandles`, {
				instrumentId: symbol,
				interval: 'CANDLE_INTERVAL_DAY',
				from: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
				to: new Date().toISOString()
			}, {
				headers: {
					'Authorization': `Bearer ${this.token}`
				}
			});

			const candles = response.data.candles;
			if (candles.length === 0) {
				throw new Error('No data available');
			}

			const firstCandle = candles[0];
			const lastCandle = candles[candles.length - 1];

			return {
				symbol: symbol,
				openPrice: firstCandle.open,
				highPrice: Math.max(...candles.map(c => c.high)),
				lowPrice: Math.min(...candles.map(c => c.low)),
				lastPrice: lastCandle.close,
				volume: candles.reduce((sum, c) => sum + c.volume, 0)
			};
		} catch (error) {
			console.error('Error fetching Tinkoff daily stats:', error);
			throw error;
		}
	}

	async getServerTime() {
		try {
			const response = await axios.post(`${this.baseUrl}/tinkoff.public.invest.api.contract.v1.MarketDataService/GetServerTime`, {}, {
				headers: {
					'Authorization': `Bearer ${this.token}`
				}
			});
			return response.data;
		} catch (error) {
			console.error('Error fetching Tinkoff server time:', error);
			throw error;
		}
	}

	async getSymbols() {
		try {
			const response = await axios.post(`${this.baseUrl}/tinkoff.public.invest.api.contract.v1.InstrumentsService/GetShares`, {}, {
				headers: {
					'Authorization': `Bearer ${this.token}`
				}
			});
			return response.data.instruments.map(instrument => ({
				symbol: instrument.uid,
				baseAsset: instrument.ticker,
				quoteAsset: 'RUB',
				status: instrument.apiTradeAvailableFlag ? 'TRADING' : 'HALT'
			}));
		} catch (error) {
			console.error('Error fetching Tinkoff symbols:', error);
			throw error;
		}
	}
} 