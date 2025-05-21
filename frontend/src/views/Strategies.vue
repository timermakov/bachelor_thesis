<template>
  <div class="strategies-container">
    <h2>{{ $t('strategies.backtest') }}</h2>
    <div class="strategy-form-panel">
      <!-- Form for selecting ticker, parameters, SL/TP methods, etc. -->
      <form @submit.prevent="runBacktest">
        <div class="form-group">
          <label for="ticker">{{ $t('strategies.ticker') }}</label>
          <select v-model="form.ticker" id="ticker" required>
            <option v-for="ticker in availableTickers" :key="ticker" :value="ticker">{{ ticker }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="start-date">{{ $t('strategies.startDate') }}</label>
          <input type="date" v-model="form.startDate" id="start-date" required />
        </div>
        <div class="form-group">
          <label for="end-date">{{ $t('strategies.endDate') }}</label>
          <input type="date" v-model="form.endDate" id="end-date" required />
        </div>
        <div class="form-group">
          <label for="stop-loss-method">{{ $t('strategies.stopLossMethod') }}</label>
          <select v-model="form.stopLossMethod" id="stop-loss-method" required>
            <option v-for="method in stopLossMethods" :key="method" :value="method">{{ method }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="take-profit-method">{{ $t('strategies.takeProfitMethod') }}</label>
          <select v-model="form.takeProfitMethod" id="take-profit-method" required>
            <option v-for="method in takeProfitMethods" :key="method" :value="method">{{ method }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="capital">{{ $t('strategies.capital') }}</label>
          <input type="number" v-model.number="form.capital" id="capital" min="1000" step="1000" required />
        </div>
        <div class="form-group">
          <label for="risk-percent">{{ $t('strategies.riskPercent') }}</label>
          <input type="number" v-model.number="form.riskPercent" id="risk-percent" min="0.01" max="1" step="0.01" required />
        </div>
        <button type="submit">{{ $t('strategies.runBacktest') }}</button>
      </form>
    </div>
    <div class="strategy-results-panel">
      <div class="card-header">
        <h3>{{ $t('strategies.backtestResults') }}</h3>
      </div>
      <div class="card-body">
        <div v-if="isLoading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <span class="ms-2">{{ $t('strategies.runningBacktest') }}</span>
        </div>
        <div v-else-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-else-if="results" class="results-container">
          <!-- Summary Card -->
          <div class="card summary-card">
            <div class="card-header">
              <h4>{{ $t('strategies.performanceSummary') }}</h4>
            </div>
            <div class="card-body">
              <table class="summary-table">
                <tr>
                  <td>Initial Balance:</td>
                  <td>{{ formatCurrency(results.summary.initialBalance) }}</td>
                </tr>
                <tr>
                  <td>Final Balance:</td>
                  <td>{{ formatCurrency(results.summary.finalBalance) }}</td>
                </tr>
                <tr>
                  <td>Profit/Loss:</td>
                  <td :class="results.summary.profitLoss >= 0 ? 'text-success' : 'text-danger'">
                    {{ formatCurrency(results.summary.profitLoss) }} 
                    ({{ results.summary.profitPercent.toFixed(2) }}%)
                  </td>
                </tr>
                <tr>
                  <td>Trade Count:</td>
                  <td>{{ results.summary.tradeCount }}</td>
                </tr>
                <tr>
                  <td>Win Rate:</td>
                  <td>{{ results.summary.winRate.toFixed(2) }}%</td>
                </tr>
              </table>
            </div>
          </div>

          <!-- Balance Chart -->
          <div class="card chart-container">
            <div class="card-header">
              <h4>{{ $t('strategies.balanceHistory') }}</h4>
            </div>
            <div class="card-body">
              <div class="balance-chart">
                <!-- Simple CSS-based visualization -->
                <div class="mini-chart">
                  <div class="chart-bars">
                    <div 
                      v-for="(point, index) in results.balanceCurve" 
                      :key="index"
                      class="chart-bar"
                      :style="{ 
                        height: calculateBarHeight(point.Balance), 
                        backgroundColor: getBarColor(point, index)
                      }"
                      :title="getBarTooltip(point, index)"
                    ></div>
                  </div>
                  <div class="chart-baseline"></div>
                </div>
                <div class="chart-legend">
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #4CAF50;"></span>
                    <span>Profit</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #CE3D4E;"></span>
                    <span>Loss</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #E0E0E0;"></span>
                    <span>Buy Order</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #E0E0E0;"></span>
                    <span>No Change</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Trades Table -->
          <div class="card trades-container">
            <div class="card-header">
              <h4>{{ $t('strategies.tradesHistory') }}</h4>
            </div>
            <div class="card-body">
              <table class="trades-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Action</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Price</th>
                    <th>Entry Price</th>
                    <th>Stop Loss</th>
                    <th>Take Profit</th>
                    <th>P/L</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(trade, index) in results.trades" :key="index" :class="getRowClass(trade)">
                    <td>{{ formatDate(trade.datetime) }}</td>
                    <td>{{ trade.buyOrSell }}</td>
                    <td>{{ trade.type }}</td>
                    <td>{{ Math.abs(trade.size) }}</td>
                    <td>{{ formatCurrency(trade.price, 2) }}</td>
                    <td>{{ formatCurrency(trade.entryPrice, 2) }}</td>
                    <td>{{ formatCurrency(trade.stopPrice, 2) }}</td>
                    <td>{{ formatCurrency(trade.takeProfitPrice, 2) }}</td>
                    <td :class="trade.pnl >= 0 ? 'text-success' : 'text-danger'">
                      {{ formatCurrency(trade.pnlcomm, 2) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const availableTickers = ref([])
const stopLossMethods = ref([
  'MA_50_18',
  'volatility_stop',
  'daily_minmax',
  'weekly_minmax',
  'monthly_minmax',
  'quarterly_minmax',
])
const takeProfitMethods = ref([
  'weekly_minmax',
  'monthly_minmax',
  'quarterly_minmax',
  'prev_bar_5_percent',
  'ma_distance'
])

const form = reactive({
  ticker: '',
  startDate: '',
  endDate: '',
  stopLossMethod: '',
  takeProfitMethod: '',
  capital: 1000000,
  riskPercent: 0.02,
})

const isLoading = ref(false)
const errorMessage = ref('')
const results = ref(null)

onMounted(async () => {
  // TODO: Fetch available tickers from backend
  availableTickers.value = ['OZON', 'AFLT', 'GAZP', 'SBER', 'NLMK']
  form.ticker = availableTickers.value[0]
  form.stopLossMethod = stopLossMethods.value[0]
  form.takeProfitMethod = takeProfitMethods.value[0]

  const today = new Date()
  const oneYearAgo = new Date()
  oneYearAgo.setFullYear(today.getFullYear() - 1)
  form.endDate = today.toISOString().split('T')[0]
  form.startDate = oneYearAgo.toISOString().split('T')[0]
})

async function runBacktest() {
  isLoading.value = true
  errorMessage.value = ''
  results.value = null
  try {
    // Start backtest
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/backtest/`, {
      ticker: form.ticker,
      start_date: form.startDate,
      end_date: form.endDate,
      stop_loss_method: form.stopLossMethod,
      take_profit_method: form.takeProfitMethod,
      capital: form.capital,
      risk_percent: form.riskPercent
    })
    const taskId = response.data.task_id || response.data.taskId
    if (!taskId) {
      errorMessage.value = 'No task_id returned from backend.'
      isLoading.value = false
      return
    }
    await pollForResult(taskId)
  } catch (err) {
    errorMessage.value = err.response?.data?.error || err.message || 'Failed to start backtest.'
    isLoading.value = false
  }
}

async function pollForResult(taskId) {
  let attempts = 0
  const maxAttempts = 120
  const poll = async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/backtest/${taskId}/`)
      if (res.data.status === 'pending') {
        if (++attempts < maxAttempts) {
          setTimeout(poll, 10000)
        } else {
          errorMessage.value = 'Backtest timed out.'
          isLoading.value = false
        }
      } else if (res.data.error) {
        errorMessage.value = res.data.error
        isLoading.value = false
      } else {
        results.value = res.data
        isLoading.value = false
      }
    } catch (err) {
      errorMessage.value = err.response?.data?.error || err.message || 'Failed to fetch backtest result.'
      isLoading.value = false
    }
  }
  poll()
}

function formatCurrency(value, decimals = 0) {
  if (value === undefined || value === null) return '-'
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }) + '₽'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString()
}

function calculateBarHeight(balance) {
  if (!results.value || !results.value.balanceCurve || results.value.balanceCurve.length === 0) {
    return '50%'
  }
  
  const balances = results.value.balanceCurve.map(point => point.Balance)
  const minBalance = Math.min(...balances)
  const maxBalance = Math.max(...balances)
  const range = maxBalance - minBalance
  
  if (range === 0) return '50%'
  
  const initialBalance = results.value.summary.initialBalance
  const normalized = ((balance - minBalance) / range) * 80 + 10 // Scale to 10-90% height
  return `${normalized}%`
}

function getBarColor(point, index) {
  const trade = findTradeForDate(point.Date);
  
  if (trade) {
    if (trade.pnl < 0) {
      return '#CE3D4E';
    }
    
    if (trade.buyOrSell === 'SELL') {
      return '#4CAF50';
    } else {
      return '#E0E0E0';
    }
  }
  
  if (index > 0) {
    const previousPoint = results.value.balanceCurve[index - 1];
    const pnl = point.Balance - previousPoint.Balance;
    
    if (Math.abs(pnl) < 0.01) {
      return '#E0E0E0';
    }
    
    return pnl > 0 ? '#4CAF50' : '#CE3D4E';
  } 
  
  return '#E0E0E0';
}

function findTradeForDate(date) {
  if (!results.value || !results.value.trades) return null;
  
  const dateStr = new Date(date).toLocaleDateString();
  return results.value.trades.find(trade => {
    return new Date(trade.datetime).toLocaleDateString() === dateStr;
  });
}

function getBarTooltip(point, index) {
  const trade = findTradeForDate(point.Date);
  let tooltip = `${formatDate(point.Date)}: ${formatCurrency(point.Balance)}`;
  
  if (index > 0) {
    const previousPoint = results.value.balanceCurve[index - 1];
    const pnl = point.Balance - previousPoint.Balance;
    const pnlText = pnl >= 0 ? `+${formatCurrency(pnl, 2)}` : formatCurrency(pnl, 2);
    tooltip += `\nPnL: ${pnlText}`;
  }
  
  if (trade) {
    tooltip += `\nAction: ${trade.buyOrSell}`;
    tooltip += `\nSize: ${Math.abs(trade.size)}`;
    tooltip += `\nPrice: ${formatCurrency(trade.price, 2)}`;
    
    if (trade.buyOrSell === 'SELL') {
      tooltip += `\nP/L: ${formatCurrency(trade.pnlcomm, 2)}`;
    }
  }
  
  return tooltip;
}

function getRowClass(trade) {
  if (trade.pnl < 0) {
    return 'loss-row';
  }
  
  if (trade.buyOrSell === 'SELL') {
    return 'profit-row';
  } else {
    return 'neutral-row';
  }
}
</script>

<style scoped>
.strategies-container {
  padding: 20px;
  width: 100%;
  margin: 0 auto;
}

.strategy-form-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

label {
  font-weight: 600;
  margin-bottom: 5px;
}

input, select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
}

button[type="submit"] {
  margin-top: 10px;
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}

button[type="submit"]:hover {
  background: #388e3c;
}

.strategy-results-panel {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
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

.card-header h3, .card-header h4 {
  margin: 0;
  font-size: 1.25rem;
}

.card-body {
  padding: 20px;
}

.error-message {
  color: #dc3545;
  font-weight: bold;
}

.results-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;	
}

.summary-card {
  grid-column: 1;
  grid-row: 1;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.chart-container {
  grid-column: 1;
  grid-row: 2;
  margin-top: 10px;
  width: 100%;
  max-width: 100%;
}

.trades-container {
  grid-column: 1;
  grid-row: 3;
}

.summary-table {
  width: 100%;
  border-collapse: collapse;
}

.summary-table td {
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.summary-table td:first-child {
  font-weight: 600;
  color: #666;
}

.balance-chart {
  margin-bottom: 20px;
}

.mini-chart {
  height: 300px;
  width: 100%;
  position: relative;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.chart-bars {
  display: flex;
  height: 100%;
  align-items: flex-end;
  gap: 1px;
}

.chart-bar {
  flex: 1;
  min-width: 2px;
  transition: height 0.3s;
}

.chart-baseline {
  position: absolute;
  bottom: 50%;
  width: 100%;
  height: 1px;
  background-color: rgba(0,0,0,0.2);
}

.trades-table {
  width: 100%;
  border-collapse: collapse;
}

.trades-table th {
  text-align: center;
  padding: 12px;
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.trades-table td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
  text-align: center;
}

.trades-table tr:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.profit-row {
  background-color: rgba(40, 167, 69, 0.05);
}

.loss-row {
  background-color: rgba(220, 53, 69, 0.05);
}

.neutral-row {
  background-color: rgba(255, 255, 255, 0.2);
}

.text-success {
  color: #28a745;
}

.text-danger {
  color: #dc3545;
}

.text-center {
  text-align: center;
}

.py-4 {
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

.spinner-border {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  vertical-align: text-bottom;
  border: 0.25em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border .75s linear infinite;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}

.summary-card {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.chart-container {
  max-width: 100%;
  width: 100%;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
}

.legend-color {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 5px;
  border-radius: 2px;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .strategies-container {
    padding: 10px;
  }
  
  .strategy-form-panel {
    padding: 15px;
  }
  
  .card-body {
    padding: 15px 10px;
  }
  
  /* Form grid layout for better space utilization */
  form {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 10px;
  }
  
  button[type="submit"] {
    grid-column: 1 / -1;
    width: 100%;
  }
  
  .form-group {
    margin-bottom: 10px;
  }
  
  /* Make the trades container scrollable */
  .trades-container {
    max-width: 100%;
    overflow-x: auto;
  }
  
  .trades-table {
    display: block;
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  /* Sticky first column for better scrolling experience */
  .trades-table td:first-child,
  .trades-table th:first-child {
    position: sticky;
    left: 0;
    background-color: #fff;
    z-index: 1;
    box-shadow: 2px 0 5px -2px rgba(0,0,0,0.1);
    min-width: 90px; /* Minimum width to prevent text overflow */
    max-width: 90px; /* Maximum width to keep consistent */
    overflow: hidden;
    text-overflow: clip; /* Add ellipsis for overflowing text */
    padding-right: 15px; /* Add more padding on the right side */
  }
  
  /* Apply specific background colors to first cell in different row types */
  .trades-table tr:hover td:first-child {
    background-color: rgba(0, 0, 0, 0.03);
  }
  
  .trades-table th:first-child {
    background-color: #f8f9fa;
  }
  
  .profit-row td:first-child {
    background-color: rgba(40, 167, 69, 0.05);
  }
  
  .loss-row td:first-child {
    background-color: rgba(220, 53, 69, 0.05);
  }
  
  /* Additional spacing between columns */
  .trades-table th,
  .trades-table td {
    white-space: nowrap;
    padding: 8px 12px; /* Increase horizontal padding */
    font-size: 0.9rem;
  }
  
  /* Prevent horizontal content overlap */
  .trades-table td:nth-child(2),
  .trades-table th:nth-child(2) {
    padding-left: 15px; /* Add extra padding to the second column */
  }
  
  /* Chart size adjustment for mobile */
  .mini-chart {
    height: 200px;
  }
  
  .chart-bars {
    gap: 0;
  }
  
  .chart-bar {
    min-width: 1px;
  }
  
  /* Legend adjustment */
  .chart-legend {
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-start;
  }
  
  .legend-item {
    font-size: 0.7rem;
    margin-right: 5px;
    margin-bottom: 5px;
  }
}

@media (max-width: 480px) {
  .form-group label {
    font-size: 0.9rem;
  }
  
  input, select {
    font-size: 0.9rem;
  }
  
  .card-header h3, .card-header h4 {
    font-size: 1.1rem;
  }
  
  .mini-chart {
    height: 150px;
  }
}
</style> 