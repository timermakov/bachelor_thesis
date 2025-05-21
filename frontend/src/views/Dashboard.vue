<template>
  <div>
    <div class="container">
      <section class="positions">
        <div class="positions-tools">
          <AddPosition/>
        </div>
        <div v-if="positions" class="row">
            <Position v-for="pos in positions" :key="pos.id" :position="pos" class="col-xxl-4 col-lg-6 col-12"/>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import Position from "@/components/Position/Position";
import AddPosition from "@/components/Position/AddPosition";
import { useTradingStore } from '@/stores/useTradingStore'

export default {
  title: 'Dashboard',
  components: {
    AddPosition,
    Position
  },
  computed: {
    positions() {
      const store = useTradingStore()
      return store.positions?.slice().reverse() || []
    }
  },
  mounted() {
    const store = useTradingStore()
    //store.loadAllSymbols()
    store.loadPositions()
    console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
  }
}
</script>

<style scoped>
h1 {
  font-size: 60px;
}

.positions-tools {
  display: flex;
  margin-bottom: 21px;
}
</style>