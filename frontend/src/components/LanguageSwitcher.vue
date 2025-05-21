<template>
  <div class="language-switcher">
    <label>{{ $t('settings.language') }}</label>
    <select v-model="currentLocale" @change="changeLocale">
      <option v-for="locale in availableLocales" :key="locale.code" :value="locale.code">
        {{ locale.name }}
      </option>
    </select>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { availableLocales } from '@/i18n'

export default {
  name: 'LanguageSwitcher',
  setup() {
    const { locale } = useI18n()
    const currentLocale = computed({
      get: () => locale.value,
      set: (value) => { locale.value = value }
    })

    const changeLocale = () => {
      localStorage.setItem('locale', currentLocale.value)
      window.location.reload()
    }

    return {
      availableLocales,
      currentLocale,
      changeLocale
    }
  }
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

label {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: white;
  font-size: 1rem;
}
</style> 