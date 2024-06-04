/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx,vue}",
    ],
    theme: {
        container: {
            center: true,
        },
        extend: {},
    },
    plugins: [
        require('daisyui'),
    ],
}

