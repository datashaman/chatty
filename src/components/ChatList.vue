<script setup>
import { defineEmits, defineProps, ref } from 'vue'
import { RouterLink } from 'vue-router'

defineEmits(['create-chat'])

const { chats }  = defineProps({
    chats: Array
})

const title = ref('')
</script>
<template>
    <div class="card shadow-xl">
        <div class="card-body">
            <h2 class="card-title px-6">Chats</h2>

            <ul class="menu flex flex-col gap-2">
                <li>
                    <RouterLink :to="{ name: 'home' }" activeClass="active">Home</RouterLink>
                </li>
                <li v-for="c in chats" :key="c.uuid" class="flex">
                    <RouterLink :to="{ name: 'chat', params: { uuid: c.uuid }}" activeClass="active">{{ c.title }}</RouterLink>
                </li>
            </ul>

            <form @submit.prevent="$emit('create-chat', title)" class="w-full flex gap-2">
                <input type="text" class="w-full input input-bordered" placeholder="Create new chat" v-model="title">
                <button type="submit" class="btn btn-primary">+</button>
            </form>
        </div>
    </div>
</template>
