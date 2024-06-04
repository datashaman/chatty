<script setup>
import { defineProps, ref, onMounted } from 'vue'
import { onBeforeRouteUpdate } from 'vue-router'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const props = defineProps({
    uuid: String,
})

const chat = ref({
    title: '',
    newMessage: '',
})
const messages = ref([])

const uuid = ref(props.uuid)
const newMessage = ref('')

const fetchChat = async () => {
    chat.value = await fetch(`${apiBaseUrl}/chats/${uuid.value}`).then(response => response.json())
    messages.value = await fetch(`${apiBaseUrl}/chats/${uuid.value}/messages`).then((response) => response.json())
    newMessage.value = chat.value.new_message
}

const sendMessage = async () => {
    const message = await fetch(`${apiBaseUrl}/chats/${uuid.value}/messages`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            role: 'user',
            content: newMessage.value,
        }),
    }).then((response) => response.json())

    messages.value.push(message)
    newMessage.value = ''
}

const updateChat = async () => {
    chat.value = await fetch(`${apiBaseUrl}/chats/${uuid.value}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            new_message: newMessage.value,
            title: chat.value.title,
        }),
    }).then((response) => response.json())
}

onMounted(async () => {
    await fetchChat()
})

onBeforeRouteUpdate(async (to, from) => {
    uuid.value = to.params.uuid
    await fetchChat()
})
</script>
<template>
    <div class="card shadow-xl h-full">
        <div class="card-body flex flex-col">
            <h2 class="card-title">{{ chat.title }}</h2>
            <ul class="grow">
                <li v-for="message in messages" :key="message.uuid">
                    <div v-if="message.role == 'assistant'" class="chat chat-start">
                        <div class="chat-bubble chat-bubble-secondary">
                            {{ message.content }}
                        </div>
                    </div>
                    <div v-else class="chat chat-end">
                        <div class="chat-bubble chat-end chat-bubble-accent">
                            {{ message.content }}
                        </div>
                    </div>
                </li>
            </ul>
            <form @submit.prevent="sendMessage" class="flex gap-2">
                <textarea class="grow textarea textarea-bordered" placeholder="Type a message" v-model="newMessage" @blur.prevent="updateChat"></textarea>
                <button type="submit" class="btn btn-primary">Send</button>
            </form>
        </div>
    </div>
</template>
