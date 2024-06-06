<script setup>
import { defineProps, ref, onMounted } from 'vue'
import { onBeforeRouteUpdate } from 'vue-router'
import markdownit from 'markdown-it'
import katex from 'markdown-it-katex'
import hljs from 'highlight.js'
import {
    Button,
    Card,
    CardActions,
    CardBody,
    CardTitle,
    FileInput,
    TextArea,
} from 'daisy-ui-kit'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

const md = markdownit({
    breaks: true,
    linkify: true,
    typographer: true,
    highlight: function (str, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return '<pre><code class="hljs">' +
                    hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
                    '</code></pre>';
            } catch (__) {}
        }

        return '<pre><code class="hljs">' + md.utils.escapeHtml(str) + '</code></pre>';
    }
})

md.use(katex)

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
const files = ref([])

const fetchChat = async () => {
    chat.value = await fetch(`${apiBaseUrl}/chats/${uuid.value}`).then(response => response.json())
    messages.value = await fetch(`${apiBaseUrl}/chats/${uuid.value}/messages`).then((response) => response.json())
    newMessage.value = chat.value.new_message
}

const sendMessage = async () => {
    const formData = new FormData()

    formData.append('content', newMessage.value)
    files.value.forEach((file) => {
        console.log(file)
        formData.append('files', file)
    })

    messages.value.push({
        role: 'user',
        content: newMessage.value,
    })
    newMessage.value = ''

    const message = await fetch(`${apiBaseUrl}/chats/${uuid.value}/messages`, {
        method: 'POST',
        body: formData,
    }).then((response) => response.json())

    messages.value.push(message)
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

const uploadFiles = async () => {
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
    <Card class="shadow-xl">
        <CardBody class="flex flex-col">
            <CardTitle is="h2">{{ chat.title }}</CardTitle>

            <ul>
                <li v-for="message in messages" :key="message.uuid">
                    <div v-if="message.role == 'assistant'" class="chat chat-start">
                        <div class="chat-bubble chat-bubble-secondary" v-html="md.renderInline(message.content)"></div>
                    </div>
                    <div v-else class="chat chat-end">
                        <div class="chat-bubble chat-end chat-bubble-accent" v-html="md.renderInline(message.content)"></div>
                    </div>
                </li>
            </ul>

            <CardActions>
                <form @submit.prevent="sendMessage">
                    <div class="flex gap-2">
                        <TextArea class="grow" bordered placeholder="Type a message" v-model="newMessage" @blur.prevent="updateChat"></TextArea>
                        <Button primary type="submit">Send</Button>
                    </div>
                    <FileInput class="mt-4" ghost accept="image/*" multiple v-model="files" @change="uploadFiles"/>
                </form>
                <ul class="flex gap-2 mt-2">
                    <li v-for="file in files" :key="file.name">
                        <img :src="URL.createObjectURL(file)" class="w-16 h-16 object-cover" />
                    </li>
                </ul>
            </CardActions>
        </CardBody>
    </Card>
</template>
