<template>
  <div>
    <button @click="openModal" class="add-position-button">{{ $t('dashboard.addPosition') }}</button>
    <transition name="fade">
      <Modal v-show="isModalVisible" @close="closeModal">
        <div class="add-position-modal container">
          <h4>{{ $t('dashboard.addPosition') }}</h4>
          <form v-on:submit.prevent="submit" action="">
            <div class="form-group">
              <input v-model="baseAsset" type="text" class="form-control" placeholder="Base asset" required>
              <input v-model="quoteAsset" type="text" class="form-control" placeholder="Quote asset" required>
              <input v-model="quantity" type="number" min="1" step="1" class="form-control" placeholder="Quantity" required>
			  <input v-model="entryPoint" type="number" step="0.000000001" class="form-control"
                     placeholder="Entry point" required>
              <input v-model="stopLoss" type="number" step="0.000000001" class="form-control" placeholder="Stop Loss"
                     required>
              <div v-for="(target, index) in targets" :key="index" class="form-group target-row">
                <input v-model="target.value" type="number" step="0.000000001" class="form-control"
                       :placeholder="`Take Profit ${index+1}`" required>
                <img :src="closeIcon" alt="" class="delete-target" @click="removeTarget(index)">
              </div>
              <button type="button" @click.prevent="addTarget" class="add-target-button">Add Take Profit</button>
              <button type="submit" class="submit-position-button">{{ $t('dashboard.addPosition') }}</button>
            </div>
          </form>
        </div>
      </Modal>
    </transition>
  </div>
</template>

<script>
import Modal from "@/components/Modal";
import closeIcon from '@/assets/img/off_close.svg'
import { useTradingStore } from '@/stores/useTradingStore'
import client from '@/broker-api'
import { useSettingsStore } from '@/stores/useSettingsStore'

export default {
  name: "AddPosition",
  components: {Modal},
  data() {
    return {
      isModalVisible: false,

      baseAsset: null,
      quoteAsset: null,
      entryPoint: null,
      stopLoss: null,
      quantity: 1,
      targets: [{value: ''}],

      closeIcon: closeIcon

    }
  },
  methods: {
    openModal() {
      this.isModalVisible = true
    },
    closeModal() {
      this.isModalVisible = false
    },
    setLabel(symbol) {
      return symbol.value
    },
    itemSelected(symbol) {
      this.symbol = symbol
    },
    addTarget() {
      this.targets.push({value: null})
    },
    removeTarget(index) {
      this.targets.splice(index, 1)
    },
    async submit() {
      const payload = {
        base_asset: this.baseAsset,
        quote_asset: this.quoteAsset,
        entry_point: this.entryPoint,
        stop_loss: this.stopLoss,
        quantity: this.quantity,
        targets: this.targets,
      }

      const tradingStore = useTradingStore()
      const settingsStore = useSettingsStore()
      const accountId = settingsStore.accountId
      if (!accountId) {
        this.$notify({ text: 'No broker account connected', type: 'error' })
        return
      }
      try {
        const figiData = await client.getFigiByTicker(this.baseAsset)
        await client.placeSandboxOrder({
          accountId,
          figi: figiData.figi,
          direction: 'buy',
          quantity: this.quantity
        })
        await tradingStore.createPosition(payload)
        this.closeModal()
      } catch (error) {
        this.$notify({ text: 'Failed to place BUY order', type: 'error' })
      }
      this.baseAsset = null
      this.quoteAsset = null
      this.entryPoint = null
      this.stopLoss = null
      this.quantity = 1
      this.targets = [{value: ''}]
    }
  },
  computed: {

  },
}
</script>

<style scoped>
.add-position-button {
  height: auto;
  font-weight: normal;
  border: 1px dashed #000000;
}

.add-position-modal {
  padding: 33px 88px;
}

.symbol-search >>> .search {
  max-height: 200px;
  overflow: scroll;
}

.target-row {
  display: flex;
  margin: 11px 0;
}

.target-row .form-control {
  margin: 0;
}

.delete-target {
  margin: 0 3px;
}

.add-target-button {
  height: 33px;
  border-width: 1px;
  font-weight: normal;
  margin: 11px 0;
}

.submit-position-button {
  margin: 11px 0;
  height: 54px;
}

</style>