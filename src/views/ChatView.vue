<script setup>
import { defineProps } from 'vue'
import Chat from '../components/Chat.vue'

const { uuid } = defineProps({
    uuid: String,
})
</script>
<template>
    <Chat :uuid="uuid" />
</template>
