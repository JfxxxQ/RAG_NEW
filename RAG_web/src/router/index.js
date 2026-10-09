import {createRouter, createWebHistory} from "vue-router";


const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            meta: {
                isLogin: false
            },
            component: () => import("../components/Login.vue")
        },
        {
            path: '/chat',
            meta: {
                isLogin: true
            },
            component: () => import("../components/Chat.vue")
        },
        {
            path: '/register',
            meta: {
                isLogin: false
            },
            component: () => import("../components/Register.vue")
        },
    ]
})

export default router;