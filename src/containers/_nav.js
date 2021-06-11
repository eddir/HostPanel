export default [
  {
    _name: 'CSidebarNav',
    _children: [
      {
        _name: 'CSidebarNavItem',
        name: 'Dashboard',
        to: '/dashboard',
        icon: 'cil-speedometer',
        badge: {
          color: 'primary',
          text: 'NEW'
        }
      },
      {
        _name: 'CSidebarNavTitle',
        _children: ['Сервера']
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Активные',
        to: '/theme/typography',
        icon: 'cil-pencil'
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Отключенные',
        to: '/theme/typography',
        icon: 'cil-pencil'
      },
      {
        _name: 'CSidebarNavTitle',
        _children: ['Сборки']
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Master',
        to: '/theme/typography',
        icon: 'cil-pencil'
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Spawner',
        to: '/charts',
        icon: 'cil-pencil'
      },
    ]
  }
]