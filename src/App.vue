<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import ChatList from './components/ChatList.vue'
import router from './router'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const chats = ref([])

const createChat = async (title) => {
    const chat = await fetch(`${apiBaseUrl}/chats`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: title })
    }).then((res) => res.json())

    chats.value.unshift(chat)

    router.push({ name: 'chat', params: { uuid: chat.uuid } })
}

onMounted(async () => {
    chats.value = await fetch(`${apiBaseUrl}/chats`).then((res) => res.json())
})
</script>
<template>
    <div class="mx-auto flex gap-4 p-10">
        <div class="w-1/4">
            <ChatList :chats="chats" @create-chat="createChat" />
        </div>

        <div class="w-3/4">
            <RouterView />
        </div>
    </div>
</template>
