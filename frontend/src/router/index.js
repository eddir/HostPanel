import Vue from 'vue'
import Router from 'vue-router'

// Containers
const TheContainer = () => import('@/containers/TheContainer')

// Views
const Dashboard = () => import('@/views/Dashboard')

// Views - Pages
const Page404 = () => import('@/views/Page404')
const Page500 = () => import('@/views/Page500')
const Login = () => import('@/views/Login')

// Servers
const Servers = () => import('@/views/servers/Servers');
const Server = () => import('@/views/servers/details/Server');
const NewServer = () => import('@/views/servers/NewServer');

// Dedicated servers
const Dedics = () => import('@/views/dedics/Dedics');
const NewDedic = () => import('@/views/dedics/NewDedic');

// Packages
const Packages = () => import('@/views/packages/Packages');
const NewPackage = () => import('@/views/packages/NewPackage');

// Users
const Users = () => import('@/views/users/Users');

// Settings
const Settings = () => import('@/views/settings/Settings');

Vue.use(Router);

export default new Router({
    mode: 'hash', // https://router.vuejs.org/api/#mode
    linkActiveClass: 'active',
    scrollBehavior: () => ({y: 0}),
    routes: configRoutes()
})

function configRoutes() {
    return [
        {
            path: '/',
            redirect: '/dashboard',
            name: 'Home',
            component: TheContainer,
            children: [
                {
                    path: 'dashboard',
                    name: 'Dashboard',
                    component: Dashboard
                },
                {
                    path: 'servers',
                    meta: {
                        label: 'Servers'
                    },
                    component: {
                        render(c) {
                            return c('router-view')
                        }
                    },
                    children: [
                        {
                            path: '',
                            name: 'Servers',
                            component: Servers
                        },
                        {
                            path: 'create',
                            name: 'Create master',
                            meta: {
                                label: 'Create master'
                            },
                            component: NewServer,
                            children: [
                                {
                                    path: ':id',
                                    meta: {
                                        label: 'Create spawner'
                                    },
                                    name: 'Create spawner',
                                    component: NewServer
                                }
                            ]
                        },
                        {
                            path: ':id',
                            meta: {
                                label: 'Server Details'
                            },
                            name: 'Server',
                            component: Server
                        }
                    ]
                },
                {
                    path: 'dedics',
                    meta: {
                        label: 'Dedicated servers'
                    },
                    component: {
                        render(c) {
                            return c('router-view')
                        }
                    },
                    children: [
                        {
                            path: '',
                            name: 'Dedics',
                            component: Dedics
                        },
                        {
                            path: 'create',
                            name: 'Create dedic',
                            meta: {
                                label: 'Create dedicated server'
                            },
                            component: NewDedic,
                        }
                    ]
                },
                {
                    path: 'packages',
                    meta: {
                        label: 'Packages'
                    },
                    component: {
                        render(c) {
                            return c('router-view')
                        }
                    },
                    children: [
                        {
                            path: ':type',
                            meta: {
                                label: 'Packages list'
                            },
                            name: 'Packages',
                            component: {
                                render(c) {
                                    return c('router-view')
                                }
                            },
                            children: [
                                {
                                    path: '',
                                    name: 'Packages',
                                    component: Packages
                                },
                                {
                                    path: 'create',
                                    name: 'Create package',
                                    meta: {
                                        label: 'Create package'
                                    },
                                    component: NewPackage,
                                }

                            ]
                        },
                    ]
                },
                {
                    path: 'users',
                    name: 'Users',
                    component: Users
                },
                {
                    path: 'settings',
                    name: 'Settings',
                    component: Settings
                }
            ]
        },
        {
            path: '/404',
            name: 'Page404',
            component: Page404
        },
        {
            path: '/500',
            name: 'Page500',
            component: Page500
        },
        {
            path: '/login',
            name: 'Login',
            component: Login
        },
    ]
}

