<template>
  <div class="analysis-container">
    <h2>{{ $t('analysis.technicalAnalysis') }}</h2>

    <!-- Selection panel -->
    <div class="selection-panel">
      <div class="ticker-selection">
        <label for="ticker-select">{{ $t('analysis.selectTicker') }}</label>
        <select id="ticker-select" v-model="selectedTicker" @change="handleTickerChange">
          <option v-for="ticker in availableTickers" :key="ticker" :value="ticker">{{ ticker }}</option>
        </select>
      </div>

      <div class="timeframe-selection">
        <label for="timeframe-select">{{ $t('analysis.timeframe') }}</label>
        <select id="timeframe-select" v-model="selectedTimeframe" @change="fetchTickerData">
          <option v-for="timeframe in availableTimeframes" :key="timeframe" :value="timeframe">{{ timeframe }}</option>
        </select>
      </div>

      <div class="date-range">
        <div>
          <label for="start-date">{{ $t('analysis.startDate') }}</label>
          <input type="date" id="start-date" v-model="startDate" @change="fetchTickerData">
        </div>
        <div>
          <label for="end-date">{{ $t('analysis.endDate') }}</label>
          <input type="date" id="end-date" v-model="endDate" @change="fetchTickerData">
        </div>
      </div>
    </div>

    <!-- Technical indicators panel -->
    <div class="indicators-panel">
        <h3>{{ $t('analysis.indicators') }}</h3>
      
      <div class="indicators-table">
        <div class="indicators-row">
          <div class="indicators-column">
            <h4>{{ $t('analysis.trendIndicators') }}</h4>
            
        <div class="indicator">
          <input type="checkbox" id="sma-checkbox" v-model="indicators.sma.enabled">
          <label for="sma-checkbox">SMA</label>
          <div v-if="indicators.sma.enabled" class="indicator-settings">
            <div>
              <label for="sma-periods">{{ $t('analysis.periods') }}:</label>
              <input type="number" id="sma-periods" v-model.number="indicators.sma.periods" min="1" max="100">
            </div>
          </div>
        </div>

            <div class="indicator">
              <input type="checkbox" id="ema-checkbox" v-model="indicators.ema.enabled">
              <label for="ema-checkbox">EMA</label>
              <div v-if="indicators.ema.enabled" class="indicator-settings">
                <div>
                  <label for="ema-periods">{{ $t('analysis.periods') }}:</label>
                  <input type="number" id="ema-periods" v-model.number="indicators.ema.periods" min="1" max="100">
                </div>
              </div>
            </div>

        <div class="indicator">
          <input type="checkbox" id="bollinger-checkbox" v-model="indicators.bollinger.enabled">
          <label for="bollinger-checkbox">Bollinger Bands</label>
          <div v-if="indicators.bollinger.enabled" class="indicator-settings">
            <div>
              <label for="bollinger-periods">{{ $t('analysis.periods') }}:</label>
              <input type="number" id="bollinger-periods" v-model.number="indicators.bollinger.periods" min="1" max="100">
            </div>
            <div>
              <label for="bollinger-std">{{ $t('analysis.standardDeviations') }}:</label>
              <input type="number" id="bollinger-std" v-model.number="indicators.bollinger.stdDev" min="1" max="4" step="0.5">
            </div>
          </div>
        </div>
          </div>


          <div class="indicators-column">
            <h4>{{ $t('analysis.oscillators') }}</h4>
            
            <div class="indicator">
              <input type="checkbox" id="macd-checkbox" v-model="indicators.macd.enabled">
              <label for="macd-checkbox">MACD</label>
              <div v-if="indicators.macd.enabled" class="indicator-settings">
                <div>
                  <label for="macd-fast">{{ $t('analysis.fastPeriod') }}:</label>
                  <input type="number" id="macd-fast" v-model.number="indicators.macd.fastPeriod" min="1" max="100">
                </div>
                <div>
                  <label for="macd-slow">{{ $t('analysis.slowPeriod') }}:</label>
                  <input type="number" id="macd-slow" v-model.number="indicators.macd.slowPeriod" min="1" max="100">
                </div>
                <div>
                  <label for="macd-signal">{{ $t('analysis.signalPeriod') }}:</label>
                  <input type="number" id="macd-signal" v-model.number="indicators.macd.signalPeriod" min="1" max="100">
                </div>
              </div>
            </div>

        <div class="indicator">
          <input type="checkbox" id="rsi-checkbox" v-model="indicators.rsi.enabled">
          <label for="rsi-checkbox">RSI</label>
          <div v-if="indicators.rsi.enabled" class="indicator-settings">
            <div>
              <label for="rsi-periods">{{ $t('analysis.periods') }}:</label>
              <input type="number" id="rsi-periods" v-model.number="indicators.rsi.periods" min="1" max="100">
            </div>
            <div>
              <label for="rsi-upper">{{ $t('analysis.upperBound') }}:</label>
              <input type="number" id="rsi-upper" v-model.number="indicators.rsi.upper" min="50" max="90">
            </div>
            <div>
              <label for="rsi-lower">{{ $t('analysis.lowerBound') }}:</label>
              <input type="number" id="rsi-lower" v-model.number="indicators.rsi.lower" min="10" max="50">
            </div>
          </div>
        </div>


            <div class="indicator">
              <input type="checkbox" id="stochastic-checkbox" v-model="indicators.stochastic.enabled">
              <label for="stochastic-checkbox">Stochastic Oscillator</label>
              <div v-if="indicators.stochastic.enabled" class="indicator-settings">
                <div>
                  <label for="stochastic-k">{{ $t('analysis.kPeriod') }}:</label>
                  <input type="number" id="stochastic-k" v-model.number="indicators.stochastic.kPeriod" min="1" max="100">
      </div>
                <div>
                  <label for="stochastic-d">{{ $t('analysis.dPeriod') }}:</label>
                  <input type="number" id="stochastic-d" v-model.number="indicators.stochastic.dPeriod" min="1" max="100">
                </div>
                <div>
                  <label for="stochastic-upper">{{ $t('analysis.upperBound') }}:</label>
                  <input type="number" id="stochastic-upper" v-model.number="indicators.stochastic.upper" min="50" max="100">
                </div>
                <div>
                  <label for="stochastic-lower">{{ $t('analysis.lowerBound') }}:</label>
                  <input type="number" id="stochastic-lower" v-model.number="indicators.stochastic.lower" min="0" max="50">
                </div>
              </div>
            </div>

            <div class="indicator">
              <input type="checkbox" id="williams-r-checkbox" v-model="indicators.williamsR.enabled">
              <label for="williams-r-checkbox">Williams %R</label>
              <div v-if="indicators.williamsR.enabled" class="indicator-settings">
                <div>
                  <label for="williams-r-periods">{{ $t('analysis.periods') }}:</label>
                  <input type="number" id="williams-r-periods" v-model.number="indicators.williamsR.periods" min="1" max="100">
                </div>
                <div>
                  <label for="williams-r-upper">{{ $t('analysis.upperBound') }}:</label>
                  <input type="number" id="williams-r-upper" v-model.number="indicators.williamsR.upper" min="-50" max="0">
                </div>
                <div>
                  <label for="williams-r-lower">{{ $t('analysis.lowerBound') }}:</label>
                  <input type="number" id="williams-r-lower" v-model.number="indicators.williamsR.lower" min="-100" max="-50">
                </div>
              </div>
            </div>
          </div>


          <div class="indicators-column">
            <h4>{{ $t('analysis.volumeIndicators') }}</h4>
            
            <div class="indicator">
              <input type="checkbox" id="obv-checkbox" v-model="indicators.obv.enabled">
              <label for="obv-checkbox">{{ $t('analysis.obv') }}</label>
            </div>

            <div class="indicator">
              <input type="checkbox" id="vwap-checkbox" v-model="indicators.vwap.enabled">
              <label for="vwap-checkbox">{{ $t('analysis.vwap') }}</label>
            </div>
          </div>
          
        </div>
      </div>

      <button class="apply-button" @click="generateAnalysis">{{ $t('common.apply') }}</button>
    </div>

    <!-- Chart container -->
    <div class="chart-container" ref="chartContainer">
      <div v-if="isLoading" class="loading">
        <div class="spinner"></div>
      </div>
      <div v-else-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      <div v-else-if="!chartData.length" class="no-data">
        {{ $t('analysis.selectTickerAndDateRange') }}
      </div>
      <div v-else class="charts-wrapper">
        <div class="chart-info">
          <div class="info-item">
            <span class="info-label">{{ $t('analysis.ticker') }}:</span>
            <span class="info-value">{{ selectedTicker }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ $t('analysis.timeframe') }}:</span>
            <span class="info-value">{{ selectedTimeframe }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">{{ $t('analysis.period') }}:</span>
            <span class="info-value">{{ startDate }} to {{ endDate }}</span>
          </div>
          <div class="info-item" v-if="chartData.length">
            <span class="info-label">{{ $t('analysis.lastUpdate') }}:</span>
            <span class="info-value">{{ formatDateTime(chartData[chartData.length-1].datetime) }}</span>
          </div>
        </div>
        <div class="main-chart-container">
          <canvas id="mainChart" ref="mainChart"></canvas>
        </div>
        
        <!-- Oscillator charts -->
        <!-- RSI Indicator Chart -->
        <div v-if="showRsiChart" class="indicator-chart-container">
          <h4>{{ $t('analysis.rsiIndicator') }}</h4>
          <canvas id="rsiChart" ref="rsiChart"></canvas>
        </div>
        
        <!-- MACD Indicator Chart -->
        <div v-if="showMacdChart" class="indicator-chart-container">
          <h4>{{ $t('analysis.macdIndicator') }}</h4>
          <canvas id="macdChart" ref="macdChart"></canvas>
      </div>
        
        <!-- Stochastic Oscillator Chart -->
        <div v-if="showStochasticChart" class="indicator-chart-container">
          <h4>{{ $t('analysis.stochasticOscillator') }}</h4>
          <canvas id="stochasticChart" ref="stochasticChart"></canvas>
        </div>
        
        <!-- Williams %R Chart -->
        <div v-if="showWilliamsRChart" class="indicator-chart-container">
          <h4>{{ $t('analysis.williamsRIndicator') }}</h4>
          <canvas id="williamsRChart" ref="williamsRChart"></canvas>
        </div>
        
        <!-- Volume Indicators -->
        <!-- On-Balance Volume Chart -->
        <div v-if="showObvChart" class="indicator-chart-container">
          <h4>{{ $t('analysis.obvIndicator') }}</h4>
          <canvas id="obvChart" ref="obvChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'
import { useI18n } from 'vue-i18n'

export default {
  name: 'Analysis',
  setup() {
    const { t } = useI18n()
    const availableTickers = ref([])
    const selectedTicker = ref('')
    const availableTimeframes = ref([])
    const selectedTimeframe = ref('1day')
    const startDate = ref('')
    const endDate = ref('')
    const chartData = ref([])
    const isLoading = ref(false)
    const errorMessage = ref('')
    const mainChart = ref(null)
    const rsiChart = ref(null)
    const macdChart = ref(null)
    const stochasticChart = ref(null)
    const williamsRChart = ref(null)
    const obvChart = ref(null)
    const showRsiChart = ref(false)
    const showMacdChart = ref(false)
    const showStochasticChart = ref(false)
    const showWilliamsRChart = ref(false)
    const showObvChart = ref(false)
    const chartContainer = ref(null)
    const mainChartInstance = ref(null)
    const rsiChartInstance = ref(null)
    const macdChartInstance = ref(null)
    const stochasticChartInstance = ref(null)
    const williamsRChartInstance = ref(null)
    const obvChartInstance = ref(null)

    // Chart references
    const mainChartRef = ref(null)
    const rsiChartRef = ref(null)
    const macdChartRef = ref(null)
    const stochasticChartRef = ref(null)
    const williamsRChartRef = ref(null)
    const obvChartRef = ref(null)

    const indicators = reactive({
      // Trend Indicators
      sma: {
        enabled: false,
        periods: 20
      },
      ema: {
        enabled: false,
        periods: 20
      },
      bollinger: {
        enabled: false,
        periods: 20,
        stdDev: 2
      },
      // Oscillators
      macd: {
        enabled: false,
        fastPeriod: 12,
        slowPeriod: 26,
        signalPeriod: 9
      },
      rsi: {
        enabled: false,
        periods: 14,
        upper: 70,
        lower: 30
      },
      stochastic: {
        enabled: false,
        kPeriod: 14,
        dPeriod: 3,
        upper: 80,
        lower: 20
      },
      williamsR: {
        enabled: false,
        periods: 14,
        upper: -20,
        lower: -80
      },
      // Volume Indicators
      obv: {
        enabled: false
      },
      vwap: {
        enabled: false
      }
    })

    const initializeDates = () => {
      const today = new Date()
      const oneYearAgo = new Date()
      oneYearAgo.setFullYear(today.getFullYear() - 1)
      
      endDate.value = today.toISOString().split('T')[0]
      startDate.value = oneYearAgo.toISOString().split('T')[0]
    }

    const fetchTickers = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/analysis/tickers/`)
        
        if (response.data && Array.isArray(response.data.tickers)) {
          availableTickers.value = response.data.tickers
          
          if (availableTickers.value.length > 0) {
            selectedTicker.value = availableTickers.value[0]
            fetchTickerData()
          } else {
            errorMessage.value = 'No tickers available. Please check your configuration.'
          }
        } else {
          availableTickers.value = []
          errorMessage.value = response.data?.error || 'Invalid response structure'
        }
      } catch (error) {
        availableTickers.value = []
        errorMessage.value = 'Failed to load tickers'
        console.error('Error fetching tickers:', error)
      }
    }

    const fetchTimeframes = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/analysis/timeframes/`)
        
        if (response.data && Array.isArray(response.data.timeframes)) {
          availableTimeframes.value = response.data.timeframes
          
          if (availableTimeframes.value.length > 0) {
            selectedTimeframe.value = availableTimeframes.value.includes('1day') 
              ? '1day' 
              : availableTimeframes.value[0]
          }
        } else {
          availableTimeframes.value = ['1min', '5min', '15min', '30min', '1hour', '1day', '1week', '1month']
          selectedTimeframe.value = '1day'
        }
      } catch (error) {
        availableTimeframes.value = ['1min', '5min', '15min', '30min', '1hour', '1day', '1week', '1month']
        selectedTimeframe.value = '1day'
        console.error('Error fetching timeframes:', error)
      }
    }

    // Fetch ticker data when ticker or date changes
    const fetchTickerData = async () => {
      if (!selectedTicker.value || !startDate.value || !endDate.value) {
        return
      }

      isLoading.value = true
      errorMessage.value = ''

      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/analysis/ticker-data/`, {
          params: {
            ticker: selectedTicker.value,
            start_date: startDate.value,
            end_date: endDate.value,
            timeframe: selectedTimeframe.value
          }
        })
        
        if (response.data && response.data.data) {
          chartData.value = response.data.data
          setTimeout(() => {
            updateChart()
          }, 0)
        } else {
          chartData.value = []
          errorMessage.value = 'No data available for selected ticker and date range'
        }
      } catch (error) {
        chartData.value = []
        errorMessage.value = `Error: ${error.response?.data?.error || 'Failed to load data'}`
        console.error('Error fetching ticker data:', error)
      } finally {
        isLoading.value = false
      }
    }

    const handleTickerChange = () => {
      fetchTickerData()
    }

    const generateAnalysis = async () => {
      if (!selectedTicker.value || !startDate.value || !endDate.value) {
        errorMessage.value = 'Please select ticker and date range'
        return
      }

      isLoading.value = true
      errorMessage.value = ''

      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/trading/analysis/generate/`, {
          ticker: selectedTicker.value,
          start_date: startDate.value,
          end_date: endDate.value,
          timeframe: selectedTimeframe.value,
          indicators: {
            // Trend Indicators
            sma: {
              enabled: indicators.sma.enabled,
              periods: indicators.sma.periods
            },
            ema: {
              enabled: indicators.ema.enabled,
              periods: indicators.ema.periods
            },
            bollinger: {
              enabled: indicators.bollinger.enabled,
              periods: indicators.bollinger.periods,
              std_dev: indicators.bollinger.stdDev
            },
            // Oscillators
            macd: {
              enabled: indicators.macd.enabled,
              fast_period: indicators.macd.fastPeriod,
              slow_period: indicators.macd.slowPeriod,
              signal_period: indicators.macd.signalPeriod
            },
            rsi: {
              enabled: indicators.rsi.enabled,
              periods: indicators.rsi.periods,
              upper: indicators.rsi.upper,
              lower: indicators.rsi.lower
            },
            stochastic: {
              enabled: indicators.stochastic.enabled,
              k_period: indicators.stochastic.kPeriod,
              d_period: indicators.stochastic.dPeriod,
              upper: indicators.stochastic.upper,
              lower: indicators.stochastic.lower
            },
            williams_r: {
              enabled: indicators.williamsR.enabled,
              periods: indicators.williamsR.periods,
              upper: indicators.williamsR.upper,
              lower: indicators.williamsR.lower
            },
            // Volume Indicators
            obv: {
              enabled: indicators.obv.enabled
            },
            vwap: {
              enabled: indicators.vwap.enabled
            }
          }
        })
        
        if (response.data && response.data.data) {
          chartData.value = response.data.data
          
          console.log("Williams %R enabled:", indicators.williamsR.enabled);
          console.log("Complete response:", response.data);
          if (response.data.analysis) {
            console.log("Analysis section:", response.data.analysis);
            console.log("Williams %R data:", response.data.analysis.williams_r);
          }
          
          setTimeout(() => {
            updateChartWithAnalysis(response.data)
          }, 0)
        }
      } catch (error) {
        errorMessage.value = `Error: ${error.response?.data?.error || 'Failed to generate analysis'}`
        console.error('Error generating analysis:', error)
      } finally {
        isLoading.value = false
      }
    }

    const formatDateTime = (datetimeStr) => {
      if (!datetimeStr) return '';
      
      const date = new Date(datetimeStr);
      
      if (isNaN(date.getTime())) {
        return datetimeStr;
      }
      
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };

    const updateChart = () => {
      if (mainChartInstance.value) {
        mainChartInstance.value.destroy();
      }

      if (rsiChartInstance.value) {
        rsiChartInstance.value.destroy();
      }

      showRsiChart.value = false;

      if (!chartData.value.length) return;

      const mainChartElement = document.getElementById('mainChart');
      if (!mainChartElement) {
        console.error('Main chart element not found');
        return;
      }

      const ctx = mainChartElement.getContext('2d');
      if (!ctx) {
        console.error('Failed to get 2d context from canvas');
        return;
      }
      
      const dates = chartData.value.map(item => {
        const date = new Date(item.datetime || item.index || item.date);
        
        if (['1min', '5min', '15min', '30min', '1hour'].includes(selectedTimeframe.value)) {
          return date.toLocaleTimeString();
        }
        return date.toLocaleDateString();
      });
      
      const prices = chartData.value.map(item => item.close);
      
      mainChartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: dates,
          datasets: [{
            label: 'Close Price',
            data: prices,
            borderColor: 'rgba(54, 162, 235, 1)',
            tension: 0.1,
            fill: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              ticks: {
                maxTicksLimit: 10
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                title: function(tooltipItems) {
                  const idx = tooltipItems[0].dataIndex;
                  const datetime = chartData.value[idx].datetime || chartData.value[idx].index || chartData.value[idx].date;
                  return formatDateTime(datetime);
                }
              }
            }
          }
        }
      });
    };

    const updateChartWithAnalysis = (analysisData) => {
      if (mainChartInstance.value) mainChartInstance.value.destroy();
      if (rsiChartInstance.value) rsiChartInstance.value.destroy();
      if (macdChartInstance.value) macdChartInstance.value.destroy();
      if (stochasticChartInstance.value) stochasticChartInstance.value.destroy();
      if (williamsRChartInstance.value) williamsRChartInstance.value.destroy();
      if (obvChartInstance.value) obvChartInstance.value.destroy();

      showRsiChart.value = false;
      showMacdChart.value = false;
      showStochasticChart.value = false;
      showWilliamsRChart.value = false;
      showObvChart.value = false;
      
      console.log("Chart flags reset:", {
        rsi: showRsiChart.value,
        macd: showMacdChart.value,
        stochastic: showStochasticChart.value,
        williamsR: showWilliamsRChart.value,
        obv: showObvChart.value
      });

      if (!analysisData.data.length) return;

      const mainChartElement = document.getElementById('mainChart');
      if (!mainChartElement) {
        console.error('Main chart element not found');
        return;
      }

      const ctx = mainChartElement.getContext('2d');
      if (!ctx) {
        console.error('Failed to get 2d context from canvas');
        return;
      }
      
      const dates = analysisData.data.map(item => {
        const date = new Date(item.datetime || item.index || item.date);
        
        if (['1min', '5min', '15min', '30min', '1hour'].includes(selectedTimeframe.value)) {
          return date.toLocaleTimeString();
        }
        return date.toLocaleDateString();
      });
      
      const prices = analysisData.data.map(item => item.close);
      
      const datasets = [{
        label: 'Close Price',
        data: prices,
        borderColor: 'rgba(54, 162, 235, 1)',
        tension: 0.1,
        fill: false
      }];

      // Add Trend Indicators

      // Add SMA
      if (analysisData.analysis.sma) {
        const smaData = analysisData.analysis.sma.values.map(item => item[1]);
        
        datasets.push({
          label: `SMA (${analysisData.analysis.sma.periods})`,
          data: smaData,
          borderColor: 'rgba(255, 159, 64, 1)',
          tension: 0.1,
          fill: false
        });
      }
      
      // Add EMA
      if (analysisData.analysis.ema) {
        const emaData = analysisData.analysis.ema.values.map(item => item[1]);
        
        datasets.push({
          label: `EMA (${analysisData.analysis.ema.periods})`,
          data: emaData,
          borderColor: 'rgba(75, 192, 192, 1)',
          tension: 0.1,
          fill: false
        });
      }

      // Add Bollinger Bands
      if (analysisData.analysis.bollinger) {
        const middleData = analysisData.analysis.bollinger.middle.map(item => item[1]);
        const upperData = analysisData.analysis.bollinger.upper.map(item => item[1]);
        const lowerData = analysisData.analysis.bollinger.lower.map(item => item[1]);
        
        datasets.push({
          label: `Bollinger Middle (${analysisData.analysis.bollinger.periods})`,
          data: middleData,
          borderColor: 'rgba(255, 99, 132, 1)',
          tension: 0.1,
          fill: false
        });
        
        datasets.push({
          label: 'Bollinger Upper',
          data: upperData,
          borderColor: 'rgba(255, 99, 132, 0.6)',
          borderDash: [5, 5],
          tension: 0.1,
          fill: false
        });
        
        datasets.push({
          label: 'Bollinger Lower',
          data: lowerData,
          borderColor: 'rgba(255, 99, 132, 0.6)',
          borderDash: [5, 5],
          tension: 0.1,
          fill: false
        });
      }
      
      // Add VWAP
      if (analysisData.analysis.vwap) {
        const vwapData = analysisData.analysis.vwap.values.map(item => item[1]);
        
        datasets.push({
          label: 'VWAP',
          data: vwapData,
          borderColor: 'rgba(153, 102, 255, 1)',
          tension: 0.1,
          fill: false
        });
      }

      mainChartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: dates,
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              ticks: {
                maxTicksLimit: 10
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                title: function(tooltipItems) {
                  const idx = tooltipItems[0].dataIndex;
                  const datetime = analysisData.data[idx].datetime || analysisData.data[idx].index || analysisData.data[idx].date;
                  return formatDateTime(datetime);
                }
              }
            }
          }
        }
      });

      // Create RSI
      if (analysisData.analysis.rsi) {
        showRsiChart.value = true;
        
        setTimeout(() => {
          const rsiChartElement = document.getElementById('rsiChart');
          if (!rsiChartElement) {
            console.error('RSI chart element not found');
            return;
          }
          
          const rsiCtx = rsiChartElement.getContext('2d');
          if (!rsiCtx) {
            console.error('Failed to get 2d context from RSI canvas');
            return;
          }
          
          const rsiData = analysisData.analysis.rsi.values.map(item => item[1]);
          
          rsiChartInstance.value = new Chart(rsiCtx, {
            type: 'line',
            data: {
              labels: dates,
              datasets: [{
                label: `Relative Strength Index (${analysisData.analysis.rsi.periods})`,
                data: rsiData,
                borderColor: 'rgba(153, 102, 255, 1)',
                tension: 0.1,
                fill: false
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  min: 0,
                  max: 100,
                  grid: {
                    color: (context) => {
                      if (context.tick.value === analysisData.analysis.rsi.upper_bound) {
                        return 'rgba(255, 0, 0, 0.5)';
                      } else if (context.tick.value === analysisData.analysis.rsi.lower_bound) {
                        return 'rgba(0, 255, 0, 0.5)';
                      }
                      return 'rgba(0, 0, 0, 0.1)';
                    }
                  }
                },
                x: {
                  ticks: {
                    maxTicksLimit: 10
                  }
                }
              },
              plugins: {
                tooltip: {
                  callbacks: {
                    title: function(tooltipItems) {
                      const idx = tooltipItems[0].dataIndex;
                      const datetime = analysisData.data[idx].datetime || analysisData.data[idx].index || analysisData.data[idx].date;
                      return formatDateTime(datetime);
                    }
                  }
                }
              }
            }
          });
        }, 0);
      } else {
        showRsiChart.value = false;
      }
      
      // Create MACD
      if (analysisData.analysis.macd) {
        showMacdChart.value = true;
        
        setTimeout(() => {
          const macdChartElement = document.getElementById('macdChart');
          if (!macdChartElement) {
            console.error('MACD chart element not found');
            return;
          }
          
          const macdCtx = macdChartElement.getContext('2d');
          if (!macdCtx) {
            console.error('Failed to get 2d context from MACD canvas');
            return;
          }
          
          const macdData = analysisData.analysis.macd.macd.map(item => item[1]);
          const signalData = analysisData.analysis.macd.signal.map(item => item[1]);
          const histogramData = analysisData.analysis.macd.histogram.map(item => item[1]);
          
          macdChartInstance.value = new Chart(macdCtx, {
            type: 'line',
            data: {
              labels: dates,
              datasets: [
                {
                  label: `MACD (${analysisData.analysis.macd.fast_period},${analysisData.analysis.macd.slow_period})`,
                  data: macdData,
                  borderColor: 'rgba(54, 162, 235, 1)',
                  tension: 0.1,
                  fill: false,
                  yAxisID: 'y'
                },
                {
                  label: `Signal (${analysisData.analysis.macd.signal_period})`,
                  data: signalData,
                  borderColor: 'rgba(255, 99, 132, 1)',
                  tension: 0.1,
                  fill: false,
                  yAxisID: 'y'
                },
                {
                  label: 'Histogram',
                  data: histogramData,
                  type: 'bar',
                  backgroundColor: (context) => {
                    const value = context.dataset.data[context.dataIndex];
                    return value >= 0 ? 'rgba(75, 192, 192, 0.5)' : 'rgba(255, 99, 132, 0.5)';
                  },
                  borderColor: (context) => {
                    const value = context.dataset.data[context.dataIndex];
                    return value >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)';
                  },
                  yAxisID: 'y'
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  position: 'left'
                },
                x: {
                  ticks: {
                    maxTicksLimit: 10
                  }
                }
              },
              plugins: {
                tooltip: {
                  callbacks: {
                    title: function(tooltipItems) {
                      const idx = tooltipItems[0].dataIndex;
                      const datetime = analysisData.data[idx].datetime || analysisData.data[idx].index || analysisData.data[idx].date;
                      return formatDateTime(datetime);
                    }
                  }
                }
              }
            }
          });
        }, 0);
      } else {
        showMacdChart.value = false;
      }
      
      // Create Stochastic chart
      if (analysisData.analysis && analysisData.analysis.stochastic) {
        console.log('Stochastic data:', analysisData.analysis.stochastic);
        
        // Get the k_line/kLine and d_line/dLine properties (supporting both naming styles)
        const kLine = analysisData.analysis.stochastic.kLine || analysisData.analysis.stochastic.k_line;
        const dLine = analysisData.analysis.stochastic.dLine || analysisData.analysis.stochastic.d_line;
        const kPeriod = analysisData.analysis.stochastic.kPeriod || analysisData.analysis.stochastic.k_period || 14;
        const dPeriod = analysisData.analysis.stochastic.dPeriod || analysisData.analysis.stochastic.d_period || 3;
        const upperBound = analysisData.analysis.stochastic.upperBound || analysisData.analysis.stochastic.upper_bound || 80;
        const lowerBound = analysisData.analysis.stochastic.lowerBound || analysisData.analysis.stochastic.lower_bound || 20;
        
        if (kLine && dLine && Array.isArray(kLine) && Array.isArray(dLine)) {
          if (kLine.length > 0 && dLine.length > 0) {
            showStochasticChart.value = true;
            
            setTimeout(() => {
              const stochasticChartElement = document.getElementById('stochasticChart');
              if (!stochasticChartElement) {
                console.error('Stochastic chart element not found');
                return;
              }
              
              const stochasticCtx = stochasticChartElement.getContext('2d');
              if (!stochasticCtx) {
                console.error('Failed to get 2d context from Stochastic canvas');
                return;
              }
              
              const kData = kLine.map(item => item[1]);
              const dData = dLine.map(item => item[1]);
              
              console.log('Stochastic K data points:', kData.length);
              console.log('Stochastic D data points:', dData.length);
              
              stochasticChartInstance.value = new Chart(stochasticCtx, {
                type: 'line',
                data: {
                  labels: dates,
                  datasets: [
                    {
                      label: `%K (${kPeriod})`,
                      data: kData,
                      borderColor: 'rgba(54, 162, 235, 1)',
                      tension: 0.1,
                      fill: false
                    },
                    {
                      label: `%D (${dPeriod})`,
                      data: dData,
                      borderColor: 'rgba(255, 99, 132, 1)',
                      tension: 0.1,
                      fill: false
                    }
                  ]
                },
                options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      min: 0,
                      max: 100,
                      grid: {
                        color: (context) => {
                          if (context.tick.value === upperBound) {
                            return 'rgba(255, 0, 0, 0.5)';
                          } else if (context.tick.value === lowerBound) {
                            return 'rgba(0, 255, 0, 0.5)';
                          }
                          return 'rgba(0, 0, 0, 0.1)';
                        }
                      }
                    },
                    x: {
                      ticks: {
                        maxTicksLimit: 10
                      }
                    }
                  },
                  plugins: {
                    tooltip: {
                      callbacks: {
                        title: function(tooltipItems) {
                          const idx = tooltipItems[0].dataIndex;
                          const datetime = analysisData.data[idx].datetime || analysisData.data[idx].index || analysisData.data[idx].date;
                          return formatDateTime(datetime);
                        }
                      }
                    }
                  }
                }
              });
            }, 0);
          } else {
            console.error('Stochastic data arrays are empty');
            showStochasticChart.value = false;
          }
        } else {
          console.error('Invalid stochastic data structure:', analysisData.analysis.stochastic);
          showStochasticChart.value = false;
        }
      } else {
        showStochasticChart.value = false;
      }
      
      // Create Williams %R
      if (analysisData.analysis && (analysisData.analysis.williamsR || analysisData.analysis.williams_r)) {
        const williamsRData = analysisData.analysis.williamsR || analysisData.analysis.williams_r;
        console.log('Williams %R data found in response:', williamsRData);
        
        try {
          const values = williamsRData.values;
          const periods = williamsRData.periods || 14;

          const upperBound = williamsRData.upperBound || williamsRData.upper_bound || -20;
          const lowerBound = williamsRData.lowerBound || williamsRData.lower_bound || -80;
          
          console.log('Williams %R values:', values);
          console.log('Williams %R periods:', periods);
          console.log('Williams %R bounds:', { upperBound, lowerBound });
          
          if (values && Array.isArray(values) && values.length > 0) {
            const williamsRPoints = values.map(item => item[1]);
            console.log('Williams %R data points:', williamsRPoints.length, williamsRPoints.slice(0, 5));
            
            showWilliamsRChart.value = true;
            console.log('Williams %R chart will be shown');
            
            setTimeout(() => {
              const williamsRChartElement = document.getElementById('williamsRChart');
              if (!williamsRChartElement) {
                console.error('Williams %R chart element not found in DOM');
                return;
              }
              
              console.log('Williams %R chart element found:', williamsRChartElement);
              
              const williamsRCtx = williamsRChartElement.getContext('2d');
              if (!williamsRCtx) {
                console.error('Failed to get 2d context from Williams %R canvas');
                return;
              }
              
              console.log('Creating Williams %R chart with', williamsRPoints.length, 'data points');
              
              williamsRChartInstance.value = new Chart(williamsRCtx, {
                type: 'line',
                data: {
                  labels: dates,
                  datasets: [{
                    label: `Williams %R (${periods})`,
                    data: williamsRPoints,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    tension: 0.1,
                    fill: false
                  }]
                },
                options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      min: -100,
                      max: 0,
                      grid: {
                        color: (context) => {
                          if (context.tick.value === upperBound) {
                            return 'rgba(255, 0, 0, 0.5)';
                          } else if (context.tick.value === lowerBound) {
                            return 'rgba(0, 255, 0, 0.5)';
                          }
                          return 'rgba(0, 0, 0, 0.1)';
                        }
                      }
                    },
                    x: {
                      ticks: {
                        maxTicksLimit: 10
                      }
                    }
                  },
                  plugins: {
                    tooltip: {
                      callbacks: {
                        title: function(tooltipItems) {
                          const idx = tooltipItems[0].dataIndex;
                          const datetime = analysisData.data[idx].datetime || analysisData.data[idx].index || analysisData.data[idx].date;
                          return formatDateTime(datetime);
                        }
                      }
                    }
                  }
                }
              });
              console.log('Williams %R chart created successfully');
            }, 0);
          } else {
            console.error('Williams %R data array is empty or invalid:', values);
            showWilliamsRChart.value = false;
          }
        } catch (err) {
          console.error('Error setting up Williams %R chart:', err);
          showWilliamsRChart.value = false;
        }
      } else {
        console.log('No Williams %R data in response:', analysisData.analysis ? Object.keys(analysisData.analysis) : 'no analysis');
        showWilliamsRChart.value = false;
      }
      
      // Create OBV
      if (analysisData.analysis && analysisData.analysis.obv) {
        console.log('OBV data:', analysisData.analysis.obv);
        
        if (analysisData.analysis.obv.values && 
            Array.isArray(analysisData.analysis.obv.values) && 
            analysisData.analysis.obv.values.length > 0) {
          
          showObvChart.value = true;
          
          setTimeout(() => {
            const obvChartElement = document.getElementById('obvChart');
            if (!obvChartElement) {
              console.error('OBV chart element not found');
              return;
            }
            
            const obvCtx = obvChartElement.getContext('2d');
            if (!obvCtx) {
              console.error('Failed to get 2d context from OBV canvas');
              return;
            }
            
            const obvData = analysisData.analysis.obv.values.map(item => item[1]);
            
            console.log('OBV data points:', obvData.length);
            
            obvChartInstance.value = new Chart(obvCtx, {
              type: 'line',
              data: {
                labels: dates,
                datasets: [{
                  label: 'On-Balance Volume (OBV)',
                  data: obvData,
                  borderColor: 'rgba(75, 192, 192, 1)',
                  tension: 0.1,
                  fill: false
                }]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  x: {
                    ticks: {
                      maxTicksLimit: 10
                    }
                  }
                },
                plugins: {
                  tooltip: {
                    callbacks: {
                      title: function(tooltipItems) {
                        const idx = tooltipItems[0].dataIndex;
                        const datetime = analysisData.data[idx].datetime || analysisData.data[idx].index || analysisData.data[idx].date;
                        return formatDateTime(datetime);
                      }
                    }
                  }
                }
              }
            });
          }, 0);
        } else {
          console.error('Invalid OBV data structure or empty data array');
          showObvChart.value = false;
        }
      } else {
        showObvChart.value = false;
      }
    }

	onMounted(() => {
      initializeDates()
      fetchTickers()
      fetchTimeframes()
    })

    return {
      availableTickers,
      selectedTicker,
      availableTimeframes,
      selectedTimeframe,
      startDate,
      endDate,
      chartData,
      isLoading,
      errorMessage,
      indicators,
      showRsiChart,
      showMacdChart,
      showStochasticChart,
      showWilliamsRChart,
      showObvChart,
      chartContainer,
      mainChart: mainChartRef,
      rsiChart: rsiChartRef,
      macdChart: macdChartRef,
      stochasticChart: stochasticChartRef,
      williamsRChart: williamsRChartRef,
      obvChart: obvChartRef,
      handleTickerChange,
      fetchTickerData,
      generateAnalysis,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.analysis-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.selection-panel {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 20px;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.ticker-selection, .timeframe-selection, .date-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

label {
  margin-right: 10px;
}

select, input[type="date"] {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.indicators-panel {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
.indicators-table {
    display: flex;
    flex-direction: column;
  gap: 20px;
  }
  
  .indicators-row {
  display: flex;
  gap: 20px;
}

.indicators-column {
  flex: 1;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 10px;
  background-color: white;
  min-width: 250px;
  column-span: all;
}

.indicators-column h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
  text-align: center;
  }
  
  .indicator {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.indicator:last-child {
  border-bottom: none;
}

.indicator input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

.indicator label {
  cursor: pointer;
  margin-bottom: 0;
}

.indicator-settings {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-left: 25px;
  width: 100%;
}

.indicator-settings > div {
  display: flex;
  align-items: center;
}

.indicator-settings > div label {
  margin-right: 5px;
  white-space: nowrap;
}

.indicator-settings input[type="number"] {
  width: 70px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.apply-button {
  align-self: flex-end;
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.apply-button:hover {
  background-color: #45a049;
}

.chart-container {
  min-height: 400px;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.charts-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 20px;
}

.main-chart-container {
  height: 400px;
  width: 100%;
  position: relative;
}

.indicator-chart-container {
  height: 200px;
  width: 100%;
  position: relative;
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.indicator-chart-container h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
}

.loading, .error-message, .no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  color: #666;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #4CAF50;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

canvas {
  width: 100% !important;
}

/* Responsive design for tablets and small laptops */
@media (max-width: 1024px) {
  .indicators-row {
    flex-wrap: wrap;
  }
  
  .indicators-column {
    min-width: 200px;
  }
}

/* Responsive design for mobile devices */
@media (max-width: 768px) {
  .selection-panel {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .ticker-selection, .timeframe-selection {
    width: 100%;
  }
  
  .ticker-selection select, .timeframe-selection select {
    flex: 1;
  }
  
  .indicators-row {
    flex-direction: column;
    gap: 15px;
  }
  
  .indicators-column {
    width: 100%;
    min-width: auto;
    overflow-x: hidden;
    margin-bottom: 5px;
    padding: 12px;
  }
  
  .indicator-settings {
    margin-left: 10px;
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .indicator {
    flex-direction: column;
    align-items: flex-start;
    padding: 12px 8px;
  }
  
  .indicator label {
    margin-left: 8px;
  }
  
  .indicator input[type="checkbox"] {
    width: 18px;
    height: 18px;
  }
  
  .indicator-settings > div {
    display: flex;
    align-items: center;
    width: 100%;
  }
  
  .indicator-settings > div label {
    min-width: 100px;
    margin-right: 10px;
  }
  
  .date-range {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }
  
  .date-range > div {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .chart-info {
    flex-direction: column;
  }
  
  .indicator-settings input[type="number"] {
    width: 100%;
    max-width: 120px;
    padding: 8px 5px;
    height: 36px;
  }
  
  select, input[type="date"] {
    width: 100%;
    max-width: 300px;
    padding: 8px;
    height: 36px;
  }
}

/* Extra small devices */
@media (max-width: 480px) {
  .indicators-panel {
    padding: 10px;
  }
  
  .indicators-column h4 {
    font-size: 14px;
  }
  
  .indicator {
    padding: 8px 5px;
    gap: 6px;
  }
  
  .indicator-settings {
    margin-left: 5px;
  }
  
  .indicator-settings > div {
    flex-wrap: wrap;
  }
  
  .indicator-settings > div label {
    min-width: 90px;
    font-size: 13px;
  }
  
  .indicator-settings input[type="number"] {
    max-width: 80px;
    padding: 4px;
    font-size: 13px;
  }
  
  select, input[type="date"], label {
    font-size: 13px;
  }
  
}

/* Very small screens */
@media (max-width: 320px) {
  .indicators-panel {
    padding: 8px;
  }
  
  .indicators-column {
    padding: 8px;
  }
  
  .indicator-settings > div label {
    min-width: 80px;
    font-size: 12px;
  }
  
  .indicator-settings input[type="number"] {
    max-width: 70px;
  }
}

.chart-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-label {
  font-weight: bold;
  color: #666;
}

.info-value {
  color: #333;
}
</style> 