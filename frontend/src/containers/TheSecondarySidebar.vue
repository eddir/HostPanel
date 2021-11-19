<template>
  <CSidebar
      fixed
      :aside="true"
      :minimize="minimize"
      :show="show"
      @update:show="(value) => $store.commit('set', ['sidebarShow', value])"
  >
    <CSidebarNav>
      <CSidebarNavItem
          v-for="task in tasks"
          :name="task.name + ' ' + task.unit_name"
          :key="task.id"
          :icon="task.state_icon"
          :color="task.state_color"
      />
    </CSidebarNav>
    <CSidebarMinimizer
        class="d-md-down-none"
        @click.native="$store.commit('set', ['secondarySidebarMinimize', !minimize])"
    />
  </CSidebar>
</template>

<script>
import ServersAPI from "@/services/API";

export default {
  name: 'TheSecondarySidebar',
  data() {
    return {
      tasks: [],
      loadInterval: null
    }
  },
  created() {
    this.update();
    this.loadInterval = setInterval(this.update, 10 * 1000);
  },
  destroyed() {
    clearInterval(this.loadInterval);
  },
  methods: {
    update() {
      ServersAPI.getTasks().then(tasks => {
        this.tasks = tasks.data.response.map(task => {
          let actions = {
            "init": "Установка",
            "start": "Запуск",
            "update": "Обновление",
            "reboot": "Ребут",
            "update_config": "Обновление конфига",
            "stop": "Остановка",
            "delete": "Удаление",
            "install_package": "Установка сборки",
            "reconnect": "Переподключение",
            "update_caretaker_legacy": "Обновление скрипта",
            "update_caretaker": "Обновление скрипта",
            "reinstall": "Переустановка",
            "monitor": "Мониторинг",
            "stat": "Мониторинг"
          }
          let states = {
            "queue": "cil-clock",
            "locked": "cil-terminal",
            "failed": "cil-x-circle",
          }

          let icon, color;
          if (task.locked_by) {
            icon = states['locked'];
            color = "info";
          } else if (task.failed_at) {
            icon = states['failed'];
            color = "danger";
          } else {
            icon = states['queue'];
            color = "";
          }

          let params = JSON.parse(task.task_params);
          return {
            name: actions[params[0][1]],
            unit_name: task.unit_name,
            state_icon: icon,
            state_color: color
          }
        })
      });
    }
  },
  computed: {
    show() {
      return this.$store.state.secondarySidebarShow
    },
    minimize() {
      return this.$store.state.secondarySidebarMinimize
    }
  }
}
</script>

<style scoped>

</style>