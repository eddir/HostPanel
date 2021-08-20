export default [
  {
    _name: 'CSidebarNav',
    _children: [
      {
        _name: 'CSidebarNavItem',
        name: 'Dashboard',
        to: '/dashboard',
        icon: 'cil-speedometer'
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Дедики',
        to: '/dedics',
        icon: 'cil-memory'
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Master сборки',
        to: '/packages/master',
        icon: 'cil-videogame'
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Spawner сборки',
        to: '/packages/spawner',
        icon: 'cil-gamepad'
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Пользователи',
        to: '/users',
        icon: 'cil-user'
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Настройки',
        to: '/settings',
        icon: 'cil-settings'
      },
    ]
  }
]