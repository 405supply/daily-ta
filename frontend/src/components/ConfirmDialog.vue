<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div class="overlay" v-if="visible" @click.self="cancel">
        <div class="dialog">
          <div class="icon" v-if="icon">{{ icon }}</div>
          <h3 class="title" v-if="title">{{ title }}</h3>
          <p class="message">{{ message }}</p>
          <div class="actions">
            <button class="btn-cancel" @click="cancel">{{ cancelLabel }}</button>
            <button class="btn-confirm" :class="`variant-${variant}`" @click="confirm">{{ confirmLabel }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const title = ref('')
const message = ref('')
const icon = ref('')
const confirmLabel = ref('확인')
const cancelLabel = ref('취소')
const variant = ref('primary') // primary | danger | warning

let resolveFn = null

function open(options = {}) {
  title.value = options.title ?? ''
  message.value = options.message ?? ''
  icon.value = options.icon ?? ''
  confirmLabel.value = options.confirmLabel ?? '확인'
  cancelLabel.value = options.cancelLabel ?? '취소'
  variant.value = options.variant ?? 'primary'
  visible.value = true
  return new Promise(resolve => { resolveFn = resolve })
}

function confirm() {
  visible.value = false
  resolveFn?.(true)
}

function cancel() {
  visible.value = false
  resolveFn?.(false)
}

defineExpose({ open })
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.dialog {
  background: white;
  border-radius: 14px;
  padding: 2rem 1.8rem 1.5rem;
  width: 340px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.icon {
  font-size: 2.2rem;
  margin-bottom: 0.6rem;
}

.title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #111;
}

.message {
  font-size: 0.9rem;
  color: #555;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.actions {
  display: flex;
  gap: 0.6rem;
}

.actions button {
  flex: 1;
  padding: 0.6rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.15s;
}

.actions button:hover { filter: brightness(0.93); }

.btn-cancel {
  background: #f0f0f0;
  color: #444;
}

.btn-confirm.variant-primary { background: #1a1a2e; color: white; }
.btn-confirm.variant-danger  { background: #e53935; color: white; }
.btn-confirm.variant-warning { background: #ff9800; color: white; }

/* Transition */
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
  transform: scale(0.92);
}
</style>
