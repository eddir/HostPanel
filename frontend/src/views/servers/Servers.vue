<template>
  <div>
    <ServersMasterSpawner :servers="masterSpawnerServers" @user-interact="freezeUpdates"></ServersMasterSpawner>
    <ServersCustom :servers="customServers" @user-interact="freezeUpdates"></ServersCustom>
  </div>
</template>

<script>

import ServersAPI from "../../services/API.vue"
import Utils from "@/services/Utils";
import ServersMasterSpawner from "@/views/servers/ServersMasterSpawner";
import ServersCustom from "@/views/servers/ServersCustom";

export default {
  name: "Servers",
  mixins: [ServersAPI, Utils],
  components: {ServersMasterSpawner, ServersCustom},
  data() {
    return {
      servers: [],
      masterSpawnerServers: [],
      customServers: [],
      loadInterval: null,
    }
  },
  created() {
    this.loadServers();
    this.loadInterval = setInterval(this.loadServers, 10 * 1000);
  },
  destroyed() {
    clearInterval(this.loadInterval);
  },
  methods: {
    loadServers() {
      // Сохраняем предыдущие данные, чтобы знать их и предостеречь закрытия collapse.
      let oldTableItems = this.masterSpawnerServers;

      // Обращение к данным и их обработка
      ServersAPI.getServers().then(servers => {
        this.servers = ServersAPI.parseMasters(servers.data.response);

        // Для отображения необходима построение древовидной структуры, где во главе мастер сервера, а их потомки
        // спавнеры.
        this.masterSpawnerServers = this.servers.filter(server => server.parent === null && !server.custom).map(item => {

          // Для этого нужна узнать была ли строчка расскрыта пользователем до этого
          let old = oldTableItems.find(s => s.host.id === item.host.id);

          // Если это совершенно новая строчка, то её нужно отобразить без collapse.
          item._toggled = old ? old._toggled : false;
          item.childs = this.servers.filter(server => server.parent === item.host.id);

          return item;
        });

        this.customServers = this.servers.filter(server => server.custom);
      });
    },
    freezeUpdates() {
      clearInterval(this.loadInterval);
    },

  }
}
</script>