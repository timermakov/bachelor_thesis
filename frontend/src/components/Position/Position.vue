<template>
	<div>
		<div class="position-card">
			<div class="position-card__top">
				<h3>{{ position.baseAsset }}/{{ position.quoteAsset }}</h3>
				<div class="crypto-icon">{{ position.baseAsset }}</div>
			</div>
			<div class="position-card__body container">
				<div class="row">
					<table class="position-card__info col-9">
						<tbody>
							<tr class="entry-point">
								<td>Entry point:</td>
								<td class="bold">{{ position.entryPoint }}</td>
							</tr>
							<tr>
								<td class="stop-loss">Stop-loss:</td>
								<td class="bold" :style="{ color: calculateColor(position.stopLoss) }">
									{{ position.stopLoss }}
								</td>
								<td class="bold" :style="{ color: calculateColor(position.stopLoss) }">
									{{ stopLossPercentage }}%
								</td>
							</tr>
							<tr v-for="(target, index) in position.targets" :key="index">
								<td class="target">
									Take Profit {{ index + 1 }}:
								</td>
								<td class="bold" :style="{ color: calculateColor(target.value) }">
									{{ target.value }}
								</td>
								<td class="bold" :style="{ color: calculateColor(target.value) }">
									{{ calculatePercentage(position.entryPoint, target.value) }}%
								</td>
							</tr>
						</tbody>
					</table>
					<div class="position-card__buttons">

					</div>
				</div>

			</div>
			<div class="position-card__bottom position-relative">
				<h3><span :class="currentPriceClass">{{ displayPrice }}</span> <span
						class="current-price-percentage" :style="{ backgroundColor: calculateColor(currentPrice) }">{{
							currentPricePercentage
						}}%</span></h3>
				<div class="position-card__menu">
					<img @click="openEdit" class="position-card__menu__icon" :src="editIcon" alt="Create similar position" title="Create similar position">
					<a :href="tradeUrl" target="_blank"><img class="position-card__menu__icon tbank_invest_logo"
							:src="brokerLogo" alt=""></a>
					<img :src="removeIcon" class="position-card__menu__icon remove-position-button"
						@click="removePosition" alt="">
				</div>
			</div>
		</div>
		<transition name="fade">
			<Modal v-show="isEditVisible" @close="closeEdit">
				<div class="add-position-modal container">
					<h4>Create new position</h4>
					<form v-on:submit.prevent="submitPosition" action="">
						<div class="form-group">
							<input v-model="editPosition.baseAsset" type="text" class="form-control"
								placeholder="Base asset" required>
							<input v-model="editPosition.quoteAsset" type="text" class="form-control"
								placeholder="Quote asset" required>
							<input v-model="editPosition.entryPoint" type="number" step="0.000000001"
								class="form-control" placeholder="Entry point" required>
							<input v-model="editPosition.stopLoss" type="number" step="0.000000001" class="form-control"
								placeholder="Stop loss" required>
							<div v-for="(target, index) in editPosition.targets" :key="index"
								class="form-group target-row">
								<input v-model="target.value" type="number" step="0.000000001" class="form-control"
									:placeholder="`Target ${index + 1}`" required>
								<img :src="closeIcon" alt="" class="delete-target" @click="removeTarget(index)">
							</div>
							<button type="button" @click.prevent="addTarget" class="add-target-button">Add
								target</button>
							<button type="submit" class="submit-position-button">Create</button>
						</div>
					</form>
				</div>
			</Modal>
		</transition>
	</div>
</template>

<script>
import client from '@/broker-api'
import _ from 'lodash'

import brokerLogo from '@/assets/img/tbank_invest_logo.png'
import editIcon from '@/assets/img/edit.svg'
import removeIcon from '@/assets/img/off_outline_close.svg'
import closeIcon from '@/assets/img/off_close.svg'

import Modal from "@/components/Modal";
import Gradient from "javascript-color-gradient"
import { useTradingStore } from '@/stores/useTradingStore'
import { useSettingsStore } from '@/stores/useSettingsStore'

function between(x, min, max) {
	return x >= min && x <= max;
}

export default {
	name: "Position",
	components: {
		Modal,
	},
	data() {
		return {
			previousPrice: 0,
			currentPrice: this.position.entryPoint || 0,
			brokerLogo: brokerLogo,
			editIcon: editIcon,
			removeIcon: removeIcon,
			closeIcon: closeIcon,
			editPosition: _.cloneDeep(this.position),
			isEditVisible: false,
		}
	},
	props: {
		position: {
			required: true,
		}
	},
	mounted() {
		this.startTimer()
		this.updatePrice()
		this.priceInterval = setInterval(() => {
			this.updatePrice()
		}, 5000) 
	},
	beforeUnmount() {
		if (this.timerInterval) {
			clearInterval(this.timerInterval)
		}
		if (this.priceInterval) {
			clearInterval(this.priceInterval)
		}
	},
	computed: {
		tradeUrl() {
			const lang = navigator.language || navigator.userLanguage;
			return `https://www.tbank.ru/terminal/`
		},
		stopLossPercentage() {
			return this.calculatePercentage(this.position.entryPoint, this.position.stopLoss)
		},
		currentPricePercentage() {
			if (!this.currentPrice || this.currentPrice <= 0) return "0.00";
			return this.calculatePercentage(this.position.entryPoint, this.currentPrice)
		},
		currentPriceClass() {
			if (!this.currentPrice || this.currentPrice <= 0) return '';
			return (this.currentPrice > this.previousPrice) ? 'long-text' : 'short-text'
		},
		currentPricePercentageClass() {
			if (!this.currentPrice || this.currentPrice <= 0) return '';
			return (this.currentPrice > this.position.entryPoint) ? 'long-bg' : 'short-bg'
		},
		displayPrice() {
			if (!this.currentPrice || this.currentPrice <= 0) return "Loading...";
			return this.currentPrice;
		}
	},
	methods: {
		updatePrice() {
			const baseAsset = this.position.baseAsset
			
			client.getFigiByTicker(baseAsset)
				.then(figiData => {
					return client.prices({ symbol: figiData.figi })
				})
				.then(response => {
					if (response && response.price && parseFloat(response.price) > 0) {
						const price = Number.parseFloat(response.price)
						this.setPrice(price)
					} else {
						throw new Error("Invalid price returned")
					}
				})
				.catch(error => {
					console.error('Error updating price:', error)
					const symbol = `${baseAsset}${this.position.quoteAsset}`
					client.prices({ symbol: symbol })
						.then(response => {
							if (response && response.price && parseFloat(response.price) > 0) {
								const price = Number.parseFloat(response.price)
								this.setPrice(price)
							} else {
								console.error('Received invalid price data:', response)
							}
						})
						.catch(fallbackError => {
							console.error('Fallback price update also failed:', fallbackError)
						})
				})
		},
		setPrice(price) {
			if (!price || price <= 0) {
				console.warn('Ignoring invalid price:', price)
				return
			}
			
			this.previousPrice = this.currentPrice
			this.currentPrice = price

			if (between(this.position.stopLoss, this.previousPrice, this.currentPrice)) {
				this.$notify({
					type: 'error',
					title: 'Stop-loss',
					text: `Price reached ${this.position.stopLoss}`
				})
				this.$notification.show('Stop-loss', {
					body: `Price reached ${this.position.stopLoss}`
				}, {})

			}
			this.position.targets.forEach((target, index) => {
				if (between(target.value, this.previousPrice, this.currentPrice)) {
					this.$notify({
						type: 'success',
						title: `Take ${index + 1}!`,
						text: `Price reached ${target.value}`
					})
					this.$notification.show(`Take ${index + 1}!`, {
						body: `Price reached ${target.value}`
					}, {})
				}
			})
		},
		calculatePercentage(startValue, endValue) {
			const percentage = (endValue / startValue) * 100 - 100
			return percentage.toFixed(2)
		},
		startTimer() {
			this.timerInterval = setInterval(() => this.timePassed += 1, 100)
		},
		addTarget() {
			this.editPosition.targets.push({ value: null })
		},
		removeTarget(index) {
			this.editPosition.targets.splice(index, 1)
		},
		submitPosition() {
			const payload = {
				base_asset: this.editPosition.baseAsset,
				quote_asset: this.editPosition.quoteAsset,
				entry_point: this.editPosition.entryPoint,
				stop_loss: this.editPosition.stopLoss,
				targets: this.editPosition.targets.map(target => ({
					value: target.value
				})),
			}
			
			const tradingStore = useTradingStore()
			tradingStore.createPosition(payload)
				.then(() => {
					this.closeEdit()
				}).catch(err => console.error(err))
		},
		async removePosition() {
			const tradingStore = useTradingStore()
			const settingsStore = useSettingsStore()
			const accountId = settingsStore.accountId
			if (!accountId) {
				this.$notify({ text: 'No broker account connected', type: 'error' })
				return
			}
			try {
				const figiData = await client.getFigiByTicker(this.position.baseAsset)
				await client.placeSandboxOrder({
					accountId,
					figi: figiData.figi,
					direction: 'sell',
					quantity: 1
				})
				await tradingStore.removePosition(this.position)
			} catch (error) {
				this.$notify({ text: 'Failed to place SELL order', type: 'error' })
			}
		},
		openEdit() {
			this.isEditVisible = true
			this.$notify({
				type: 'info',
				title: 'Create New Position',
				text: `Creating a new position based on ${this.position.baseAsset}/${this.position.quoteAsset}`
			})
		},
		closeEdit() {
			this.isEditVisible = false
			this.editPosition = _.cloneDeep(this.position)
		},
		calculateColor(currentValue) {
			const gradient = new Gradient();

			const red = "#CE3D4E";
			const midred = "#D05A68";
			const grey = "#BDBDBD";
			const midgreen = "#5FD396";
			const green = "#5EBA89";
			const maxNumber = 100

			const colorNumber = maxNumber / 2 + parseInt(this.calculatePercentage(
				this.position.entryPoint, currentValue))

			gradient.setGradient(red, midred, grey, midgreen, green)
			gradient.setMidpoint(maxNumber)

			try {
				return gradient.getColor(colorNumber)
			} catch (e) {
				return grey
			}
		}
	}
}
</script>

<style scoped>
.position-card {
	background: #FFFFFF;
	border: 2px solid #BDBDBD;
	border-radius: 22px;
	transition: all 300ms ease-in-out;
	box-shadow: none;
	/*cursor: pointer;*/
	font-family: "Montserrat", sans-serif;
	font-size: 18px;
	padding: 15px 20px;
	margin: 12px 0;
}

/*.position-card:hover {*/
/*  border-color: white;*/
/*  box-shadow: 5px 5px 12px rgba(0, 0, 0, 0.25);*/
/*  transform: translate(0, -4px);*/
/*}*/

h3 {
	font-family: "Montserrat", sans-serif;
	font-style: italic;
	font-weight: 600;
	font-size: 24px;
	margin: 0;
}

.position-card__top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 9px;
}

.position-card__body {
	margin: 0 -12px;
}

.position-card__info {
	text-align: left;
	line-height: 22px;
}

.position-card__info td {
	margin: 0;
	padding: 0;
	border-width: 0;
}

.position-card__bottom {
	display: flex;
	justify-content: space-between;
	align-items: flex-end;
	margin-top: 25px;
}

.position-card__menu {
	display: flex;
	flex-direction: column-reverse;
	position: absolute;
	right: 0;
	bottom: 0;
	border: 2px solid #C4C4C4;
	box-sizing: border-box;
	border-radius: 11px;
	max-height: 38px;
	overflow: hidden;
	transition: max-height 500ms ease;
}

.position-card__menu:hover {
	max-height: 200px;
}

.position-card__menu__icon {
	transition: all 200ms ease-in-out;
	margin: 4px 4px;
	height: 25px;
}

.position-card__menu__icon:hover {
	filter: drop-shadow(0px 2px 2px rgba(0, 0, 0, 0.25));
}

.bold {
	font-weight: 600;
}

.entry-point td {
	padding-bottom: 11px;
}

.current-price-percentage {
	padding: 1px 5px;
	border-radius: 4px;
	color: white;
}

.target-row {
	display: flex;
	margin: 11px 0;
}

.target-row .form-control {
	margin: 0;
}

.add-position-modal {
	padding: 33px 88px;
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

.remove-position-button {
	transition: all 200ms ease-in-out;
}

.remove-position-button:hover {
	filter: drop-shadow(0px 2px 2px rgba(0, 0, 0, 0.25));
}

.crypto-icon {
	font-size: 24px;
	font-weight: bold;
	color: #666;
}
</style>