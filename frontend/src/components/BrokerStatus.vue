<template>
  <div class="broker-status">
    <div class="broker-status__info">
      <div class="broker-status__row">
        <div class="broker-status__label">{{ $t('common.date') }}</div>
        <div class="broker-status__value">{{ formattedDate }}</div>
      </div>
      <div class="broker-status__row">
        <div class="broker-status__label">{{ $t('broker.timeMoscow') }}</div>
        <div class="broker-status__value">{{ formattedTime }}</div>
      </div>
      <div v-if="providers.length === 0" class="broker-status__row">
        <div class="broker-status__label">No providers available</div>
      </div>
      <div v-for="provider in providers" :key="provider.name">
        <div class="broker-status__row">
          <div class="broker-status__label">
            {{ getBrokerDisplayName(provider.name) }} {{ $t('broker.connection') }}
          </div>
          <div class="broker-status__value">
            <span :class="getConnectionStatusClass(provider)">
              {{ provider.connected ? $t('common.connected') : $t('common.disconnected') }}
            </span>
            <button 
              class="broker-status__button" 
              @click="toggleConnection(provider)"
              :disabled="loading"
            >
              {{ provider.connected ? $t('broker.disconnect') : $t('broker.connect') }}
            </button>
          </div>
        </div>
        <!-- Add account selector row -->
        <div class="broker-status__row" v-if="!provider.connected">
          <div class="broker-status__label">Account:</div>
          <div class="broker-status__value">
            <div class="broker-status__account-container">
              <input
                type="text"
                class="broker-status__account-input"
                v-model="provider.selectedAccount"
                @focus="loadAccounts(provider)"
                @blur="handleBlur"
                @click="toggleAccountDropdown(provider)"
                :placeholder="getAccountPlaceholder(provider)"
              />
              <div class="broker-status__dropdown" v-show="provider.showAccountDropdown && provider.accounts.length > 0">
                <div 
                  v-for="account in provider.accounts" 
                  :key="account.id" 
                  class="broker-status__dropdown-item"
                  @mousedown="selectAccount(provider, account)"
                >
                  {{ account.name }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useI18n } from 'vue-i18n';
import { useSettingsStore } from '@/stores/useSettingsStore';

export default {
  name: 'BrokerStatus',
  setup() {
    const { t } = useI18n();
    return { t };
  },
  data() {
    return {
      currentDate: new Date(),
      providers: [],
      loading: false,
      clockInterval: null
    };
  },
  computed: {
    formattedDate() {
      return this.currentDate.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    },
    formattedTime() {
      return this.currentDate.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Europe/Moscow'
      });
    }
  },
  methods: {
    getBrokerDisplayName(name) {
      const displayNames = {
        'tinkoff': 'Т-Банк'
      };
      return displayNames[name] || name;
    },
    getConnectionStatusClass(provider) {
      return {
        'broker-status__connection--connected': provider.connected,
        'broker-status__connection--disconnected': !provider.connected
      };
    },
    getAccountPlaceholder(provider) {
	if (provider.accounts && provider.accounts.length > 0) {
        return 'Select an account';
      } else {
        return 'Enter account name';
      }
    },
    async toggleConnection(provider) {
      this.loading = true;
      try {
        if (provider.connected) {
          await axios.post(`${import.meta.env.VITE_API_URL}/trading/market-data/providers/${provider.name}/disconnect/`);
          provider.connected = false;
          const settingsStore = useSettingsStore();
          settingsStore.setAccount(null, null);
        } else {
          let accountId = provider.selectedAccountId;
          if (!accountId && provider.accounts && provider.accounts.length > 0) {
            accountId = provider.accounts[0].id;
            provider.selectedAccountId = accountId;
            provider.selectedAccount = provider.accounts[0].name;
          }
          if (!accountId) {
            this.$notify && this.$notify({ text: 'No account selected', type: 'error' });
            this.loading = false;
            return;
          }
          const response = await axios.post(
            `${import.meta.env.VITE_API_URL}/trading/market-data/providers/${provider.name}/connect/`, 
            { account_id: accountId }
          );
          provider.connected = true;
          provider.currentAccount = accountId;
          const settingsStore = useSettingsStore();
          settingsStore.setAccount(accountId, provider.name);
        }
      } catch (error) {
        console.error('Error toggling connection:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadAccounts(provider) {
      if (provider.loadingAccounts || provider.connected) return;
      
      provider.loadingAccounts = true;
      provider.showAccountDropdown = true;
      
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/trading/market-data/providers/${provider.name}/accounts/`
        );
        provider.accounts = response.data || [];
      } catch (error) {
        console.error('Error loading accounts:', error);
        provider.accounts = [];
      } finally {
        provider.loadingAccounts = false;
      }
    },
    toggleAccountDropdown(provider) {
      if (!provider.connected) {
        provider.showAccountDropdown = !provider.showAccountDropdown;
        if (provider.showAccountDropdown) {
          this.loadAccounts(provider);
        }
      }
    },
    selectAccount(provider, account) {
      provider.selectedAccount = account.name;
      provider.selectedAccountId = account.id;
      provider.showAccountDropdown = false;
    },
    handleBlur() {
      setTimeout(() => {
        this.providers.forEach(provider => {
          provider.showAccountDropdown = false;
        });
      }, 200);
    },
    async loadProviders() {
      this.loading = true;
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/trading/market-data/providers/`);
        this.providers = (response.data || []).map(provider => ({
          ...provider,
          accounts: [],
          selectedAccount: '',
          selectedAccountId: null,
          currentAccount: null,
          showAccountDropdown: false,
          loadingAccounts: false
        }));
        
      } catch (error) {
        console.error('Error loading providers:', error);
        this.providers = [
          { 
            name: 'tinkoff', 
            connected: false, 
            isActive: false,
            accounts: [],
            selectedAccount: '',
            selectedAccountId: null,
            currentAccount: null,
            showAccountDropdown: false,
            loadingAccounts: false
          }
        ];
      } finally {
        this.loading = false;
      }
    },
    startClock() {
      this.clockInterval = setInterval(() => {
        this.currentDate = new Date();
      }, 1000);
    },
    stopClock() {
      if (this.clockInterval) {
        clearInterval(this.clockInterval);
      }
    }
  },
  mounted() {
    this.loadProviders();
    this.startClock();
  },
  beforeUnmount() {
    this.stopClock();
  }
};
</script>

<style scoped>
.broker-status {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px;
  font-size: 14px;
}

.broker-status__row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  align-items: center;
}

.broker-status__label {
  font-weight: bold;
  color: #333;
  min-width: 140px;
  text-align: left;
  padding-right: 10px;
}

.broker-status__value {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
  flex: 1;
}

.broker-status__connection--connected {
  color: #1e8e3e;
  min-width: 80px;
}

.broker-status__connection--disconnected {
  color: #d93025;
  min-width: 80px;
}

.broker-status__button {
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  height: auto;
  width: auto;
  min-width: 80px;
}

.broker-status__button:hover {
  background-color: #174ea6;
}

.broker-status__button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.broker-status__account-container {
  position: relative;
  width: 100%;
}

.broker-status__account-input {
  width: 100%;
  padding: 4px 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 12px;
}

.broker-status__dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.broker-status__dropdown-item {
  padding: 4px 4px;
  cursor: pointer;
  font-size: 12px;
}

.broker-status__dropdown-item:hover {
  background-color: #f5f7fa;
}
</style> 