<template>
  <div class="portfolio-page">
    <h1>{{ $t('portfolio.title') }}</h1>
    
    <div class="card portfolio-card">
      <div class="card-header">
        <h2>{{ $t('portfolio.balance') }}</h2>
      </div>
      <div class="card-body balance-section">
        <div v-if="portfolioStore.loading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm" role="status">
            <span class="visually-hidden">{{ $t('common.loading') }}</span>
          </div>
          <span class="ms-2">{{ $t('portfolio.loadingBalance') }}</span>
        </div>
        <div v-else class="balance-info">
          <span class="balance-label">{{ $t('portfolio.currentBalance') }}</span>
          <span class="balance-value">
            {{ formatBalance(portfolioStore.balance) }} {{ portfolioStore.currency || 'RUB' }}
          </span>
        </div>
        
        <div v-if="portfolioStore.expectedYield && portfolioStore.expectedYield.relative !== 0" class="yield-info">
          <span class="yield-label">Expected Yield:</span>
          <span :class="getPnLClass(portfolioStore.expectedYield.relative)">
            {{ formatPnL(portfolioStore.expectedYield.relative) }} 
            <span v-if="portfolioStore.expectedYield.value !== undefined">
              ({{ formatMoney(portfolioStore.expectedYield.value) }})
            </span>
          </span>
        </div>
        
        <div v-if="settingsStore.isSandbox" class="sandbox-controls">
          <div class="balance-input">
            <input 
              type="number" 
              v-model="newBalance" 
              :placeholder="$t('portfolio.moneyAmount')"
              class="balance-textfield"
            />
            <button 
              @click="setBalance" 
              class="set-balance-btn"
              :disabled="!isValidBalance || portfolioStore.loading"
            >
              {{ portfolioStore.loading ? $t('common.loading') : $t('portfolio.addMoney') }}
            </button>
          </div>
          <span v-if="portfolioStore.error" class="error-message">{{ portfolioStore.error }}</span>
        </div>
      </div>
    </div>
    
    <div class="card assets-card">
      <div class="card-header">
        <h2>{{ $t('portfolio.assets') }}</h2>
      </div>
      <div class="card-body">
        <div v-if="portfolioStore.positionsLoading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="!positions.length" class="text-center py-4">
          <p>No assets found in your portfolio.</p>
        </div>
        <table v-else class="table assets-table">
          <thead>
            <tr>
              <th>Asset</th>
              <th>Ticker</th>
              <th>Type</th>
              <th>Quantity</th>
              <th>Avg. Price</th>
              <th>Current Price</th>
              <th>Value</th>
              <th>P&L</th>
              <th>P&L (%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(position, index) in positions" :key="position.figi || index">
              <td>{{ position.name || position.figi || '-' }}</td>
              <td>{{ position.ticker || position.figi?.replace('000UTSTOM', '') || '-' }}</td>
              <td>{{ formatInstrumentType(position.instrumentType) }}</td>
              <td>{{ formatQuantity(position.quantity) }}</td>
              <td>{{ formatMoneyValue(position.averagePositionPrice) }}</td>
              <td>{{ formatMoneyValue(position.currentPrice) }}</td>
              <td>{{ formatMoneyValue(position.value) }}</td>
              <td :class="getPnLClass(position.pnl)">
                {{ formatMoney(position.pnl) }}
              </td>
              <td :class="getPnLClass(position.pnlPercentage)">
                {{ formatPnL(position.pnlPercentage) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="card history-card">
      <div class="card-header">
        <h2>{{ $t('portfolio.history') }}</h2>
      </div>
      <div class="card-body">
        <div v-if="historyLoading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="history.length === 0" class="text-center py-4">
          <p>No transaction history found.</p>
          <p class="text-muted">Transaction history API is not yet implemented.</p>
        </div>
        <table v-else class="table history-table">
          <thead>
            <tr>
              <th>Date</th>
			  <th>Name</th>
			  <th>Ticker</th>
              <th>FIGI</th>
              <th>Type</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in history" :key="transaction.id">
              <td>{{ formatDate(transaction.date) }}</td>
			  <td>{{ transaction.name }}</td>			  
			  <td>{{ transaction.ticker }}</td>
              <td>{{ transaction.asset }}</td>
              <td :class="getOperationTypeClass(transaction.type)">
                {{ transaction.type }}
              </td>
              <td>{{ transaction.quantity }}</td>
              <td>{{ formatMoney(transaction.price?.units || 0, transaction.price?.currency) }}</td>
              <td>{{ formatMoney(transaction.payment?.units || 0, transaction.payment?.currency) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePortfolioStore } from '../stores/usePortfolioStore'
import { useSettingsStore } from '../stores/useSettingsStore'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const portfolioStore = usePortfolioStore()
const settingsStore = useSettingsStore()
const newBalance = ref('')
const history = ref([])
const historyLoading = ref(false)

const positions = computed(() => portfolioStore.positions.map(position => {
  const avgPrice = position.averagePositionPrice?.value || 0
  const currentPrice = position.currentPrice?.value || 0
  const quantity = position.quantity || 0
  const invested = avgPrice * Math.abs(quantity)
  const pnl = (currentPrice - avgPrice) * quantity
  const pnlPercentage = invested ? (pnl / invested) * 100 : 0
  return {
    ...position,
    pnl,
    pnlPercentage
  }
}) || [])

const isValidBalance = computed(() => {
  const value = parseFloat(newBalance.value)
  return !isNaN(value) && value > 0
})

const formatBalance = (value) => {
  if (value === undefined || value === null || Number.isNaN(value)) return '-'
  
  try {
    const numValue = Number(value)
    return new Intl.NumberFormat('ru-RU').format(numValue)
  } catch (error) {
    console.error('Error formatting balance:', error)
    return '-'
  }
}

const formatMoney = (value, currency) => {
  if (value === undefined || value === null || Number.isNaN(value)) return '-';
  
  try {
    const useCurrency = currency || portfolioStore.currency || 'RUB';
    const numValue = Number(value);
    
    return new Intl.NumberFormat('ru-RU', { 
      style: 'currency', 
      currency: useCurrency 
    }).format(numValue);
  } catch (error) {
    console.error('Error formatting money:', error);
    return '-';
  }
}

const formatMoneyValue = (moneyObj) => {
  if (!moneyObj || moneyObj.value === undefined) return '-'
  
  try {
    const currency = (moneyObj.currency && moneyObj.currency !== '') 
      ? moneyObj.currency 
      : (portfolioStore.currency || 'RUB')
    
    const numValue = Number(moneyObj.value)
    if (isNaN(numValue)) return '-'
    
    return new Intl.NumberFormat('ru-RU', { 
      style: 'currency', 
      currency: currency 
    }).format(numValue)
  } catch (error) {
    console.error('Error formatting money value:', error)
    return '-'
  }
}

const formatQuantity = (value) => {
  if (value === undefined || value === null) return '-'
  
  try {
    const numValue = Number(value)
    if (isNaN(numValue)) return '-'
    
    return new Intl.NumberFormat('ru-RU', { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 8
    }).format(numValue)
  } catch (error) {
    console.error('Error formatting quantity:', error)
    return '-'
  }
}

const formatInstrumentType = (type) => {
  if (!type) return '-'
  
  const types = {
    'share': 'Share',
    'currency': 'Currency',
    'bond': 'Bond',
    'etf': 'ETF',
    'futures': 'Futures',
    'option': 'Option'
  }
  
  return types[type.toLowerCase()] || type
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
  }).format(date)
}

const formatPnL = (value) => {
  if (value === undefined || value === null || Number.isNaN(value)) return '-'
  
  try {
    const numValue = Number(value)
    if (isNaN(numValue)) return '-'
    
    return `${numValue >= 0 ? '+' : ''}${numValue.toFixed(2)}%`
  } catch (error) {
    console.error('Error formatting PnL:', error)
    return '-'
  }
}

const getPnLClass = (value) => {
  if (value === undefined || value === null) return ''
  return value >= 0 ? 'text-success' : 'text-danger'
}

const setBalance = async () => {
  try {
    const balance = parseFloat(newBalance.value)
    await portfolioStore.setSandboxBalance(balance)
    
    // Refresh portfolio data after setting balance
    await Promise.all([
      portfolioStore.fetchBalance(),
      portfolioStore.fetchPositions()
    ])
    
    newBalance.value = ''
  } catch (err) {
    // Error is handled by the store
    console.error('Error setting balance:', err)
  }
}

const fetchHistory = async () => {
  try {
    historyLoading.value = true;
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/portfolio/transaction-history/`, {
      params: {
        instrument_id: 'BBG004730N88', // Example instrument ID
        provider: 'tinkoff'
      },
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    });
    history.value = response.data.operations.map(operation => {
      const price = operation.price || { units: 0, nano: 0, currency: '' };
      const payment = operation.payment || { units: 0, nano: 0, currency: '' };
      
      return {
        id: operation.id,
        date: operation.date,
		name: operation.name,
		ticker: operation.ticker,
        asset: operation.figi, 
        type: operation.operationTypeDescription || operation.type,
        quantity: operation.quantity,
        price: price,
        payment: payment
      };
    });
  } catch (error) {
    console.error('Error fetching history:', error);
    history.value = [];
  } finally {
    historyLoading.value = false;
  }
};

const getOperationTypeClass = (type) => {
  if (!type) return '';
  
  const buyTypes = ['OPERATION_TYPE_BUY', 'OPERATION_TYPE_EXCHANGE_BUY', 'OPERATION_TYPE_DELIVERY_BUY'];
  const sellTypes = ['OPERATION_TYPE_SELL', 'OPERATION_TYPE_EXCHANGE_SELL', 'OPERATION_TYPE_DELIVERY_SELL'];
  const inputTypes = ['OPERATION_TYPE_INPUT', 'OPERATION_TYPE_INP_MULTI', 'OPERATION_TYPE_INPUT_SWIFT', 'OPERATION_TYPE_INPUT_ACQUIRING'];
  const outputTypes = ['OPERATION_TYPE_OUTPUT', 'OPERATION_TYPE_OUT_MULTI', 'OPERATION_TYPE_OUTPUT_SWIFT', 'OPERATION_TYPE_OUTPUT_ACQUIRING'];
  const paymentTypes = ['OPERATION_TYPE_COUPON', 'OPERATION_TYPE_DIVIDEND', 'OPERATION_TYPE_DIV_EXT', 'OPERATION_TYPE_OVER_INCOME'];
  const feeTypes = ['OPERATION_TYPE_BROKER_FEE', 'OPERATION_TYPE_SERVICE_FEE', 'OPERATION_TYPE_MARGIN_FEE',
      'OPERATION_TYPE_SECURITY_FEE', 'OPERATION_TYPE_OUT_FEE', 'OPERATION_TYPE_OVER_COM', 'OPERATION_TYPE_CASH_FEE',
      'OPERATION_TYPE_OUTPUT_PENALTY', 'OPERATION_TYPE_ADVICE_FEE'];
  const taxTypes = ['OPERATION_TYPE_TAX', 'OPERATION_TYPE_BOND_TAX', 'OPERATION_TYPE_TAX_PROGRESSIVE',
      'OPERATION_TYPE_BOND_TAX_PROGRESSIVE', 'OPERATION_TYPE_DIVIDEND_TAX_PROGRESSIVE',
      'OPERATION_TYPE_BENEFIT_TAX', 'OPERATION_TYPE_BENEFIT_TAX_PROGRESSIVE'];
  
  if (buyTypes.includes(type)) return 'text-success';
  if (sellTypes.includes(type)) return 'text-danger';
  if (inputTypes.includes(type)) return 'text-primary';
  if (outputTypes.includes(type)) return 'text-warning';
  if (paymentTypes.includes(type)) return 'text-info';
  if (feeTypes.includes(type)) return 'text-muted';
  if (taxTypes.includes(type)) return 'text-secondary';
  
  return '';
}

onMounted(async () => {
  try {
    await portfolioStore.fetchBalance()
    await portfolioStore.fetchPositions()
    await fetchHistory()
  } catch (error) {
    console.error('Error initializing portfolio data:', error)
  }
})
</script>

<style scoped>
.portfolio-page {
  padding: 20px;
}

.card {
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  background-color: #f8f9fa;
  padding: 15px 20px;
  border-bottom: 1px solid #e9ecef;
}

.card-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.card-body {
  padding: 20px;
}

.balance-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.balance-info, .yield-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.balance-label, .yield-label {
  font-weight: 600;
  color: #666;
}

.balance-value {
  font-size: 1.2em;
  font-weight: 700;
  color: #2c3e50;
}

.sandbox-controls {
  margin-top: 10px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.balance-input {
  display: flex;
  gap: 10px;
  align-items: center;
}

.balance-textfield {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
  width: 200px;
}

.set-balance-btn {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.set-balance-btn:hover {
  background-color: #45a049;
}

.set-balance-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  font-size: 0.9em;
  margin-top: 8px;
}

.assets-table, .history-table {
  width: 100%;
  border-collapse: collapse;
}

.assets-table th, .history-table th {
  text-align: center;
  padding: 12px;
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.assets-table td, .history-table td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
}

.assets-table tr:hover, .history-table tr:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.text-success {
  color: #28a745;
}

.text-danger {
  color: #dc3545;
}

.text-muted {
  color: #6c757d;
  font-style: italic;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .portfolio-page {
    padding: 10px;
  }
  
  .card-body {
    padding: 15px 10px;
  }
  
  .balance-info, .yield-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .balance-input {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }
  
  .balance-textfield {
    width: 100%;
  }
  
  .set-balance-btn {
    width: 100%;
    margin-top: 10px;
  }
  
  /* Table responsiveness */
  .assets-card, .history-card {
    max-width: 100%;
    overflow-x: auto;
  }
  
  .assets-table, .history-table {
    display: block;
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  /* Style for mobile-optimized tables */
  .assets-table th, .history-table th,
  .assets-table td, .history-table td {
    white-space: nowrap;
    padding: 8px;
    font-size: 0.9rem;
  }
  
  /* Highlight first column to help with horizontal scrolling */
  .assets-table td:first-child,
  .history-table td:first-child,
  .assets-table th:first-child,
  .history-table th:first-child {
    position: sticky;
    left: 0;
    background-color: #fff;
    z-index: 1;
    box-shadow: 2px 0 5px -2px rgba(0,0,0,0.1);
  }
  
  .assets-table tr:hover td:first-child,
  .history-table tr:hover td:first-child {
    background-color: rgba(0, 0, 0, 0.03);
  }
  
  .assets-table th:first-child,
  .history-table th:first-child {
    background-color: #f8f9fa;
  }
}
</style> 