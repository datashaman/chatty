import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    compilerOptions: {
        isCustomElement: tagName => {
            return tagName === 'vue-advanced-chat' || tagName === 'emoji-picker' || tagName === 'chat'
        }
    }
})
