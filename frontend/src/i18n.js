import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import ru from './locales/ru.json'

const getBrowserLocale = () => {
	const storedLocale = localStorage.getItem('locale')

	if (storedLocale) {
		return storedLocale
	}

	const navigatorLocale = navigator.language.split('-')[0]

	return navigatorLocale === 'ru' ? 'ru' : 'en'
}

export const availableLocales = [
	{
		code: 'en',
		name: 'English'
	},
	{
		code: 'ru',
		name: 'Русский'
	}
]

export const defaultLocale = 'ru'

export default createI18n({
	legacy: false,
	locale: getBrowserLocale() || defaultLocale,
	fallbackLocale: 'en',
	messages: {
		en,
		ru
	}
}) 