<script setup>
import { defineEmits, defineProps, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
    Button,
    Card,
    CardActions,
    CardBody,
    CardTitle,
    Menu,
    MenuItem,
    TextInput,
} from 'daisy-ui-kit'

defineEmits(['create-chat'])

const { chats }  = defineProps({
    chats: Array
})

const title = ref('')
</script>
<template>
    <Card class="shadow-xl">
        <CardBody>
            <CardTitle is="h2">Chats</CardTitle>

            <Menu class="flex flex-col gap-2">
                <MenuItem>
                    <RouterLink :to="{ name: 'home' }" activeClass="active">Home</RouterLink>
                </MenuItem>
                <MenuItem v-for="c in chats" :key="c.uuid">
                    <RouterLink :to="{ name: 'chat', params: { uuid: c.uuid }}" activeClass="active">{{ c.title }}</RouterLink>
                </MenuItem>
            </Menu>

            <form @submit.prevent="$emit('create-chat', title)" class="w-full flex gap-2">
                <TextInput class="w-full input-bordered" placeholder="Create new chat" v-model="title" />
                <Button type="submit" primary>+</Button>
            </form>
        </CardBody>
    </Card>
</template>
