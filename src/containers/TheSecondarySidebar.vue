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
          icon="cil-clock"
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
  beforeRouteLeave(to, from, next) {
    clearInterval(this.loadInterval);
    next();
  },
  methods: {
    update() {
      ServersAPI.getTasks().then(tasks => {
        this.tasks = tasks.data.tasks.map(task => {
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
          }
          let params = JSON.parse(task.task_params);
          return {
            name: actions[params[0][1]],
            unit_name: task.unit_name
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