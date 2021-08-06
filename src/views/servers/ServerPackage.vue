<template>
  <div>
    <CSelect :value.sync="selected" :options="packages"/>
    <CButton key="send" color="primary" class="m-2" @click="install">Установить</CButton>
  </div>
</template>

<script>
import ServersAPI from "@/services/API";
import Action from "@/services/Action";

export default {
  name: "ServerPackage",
  mixins: [ServersAPI],
  props: {
    server: Object
  },
  data() {
    return {
      packages: [],
      selected: null
    }
  },
  created() {
    this.selected = null;
    /** @param this.server.package__mpackage__id */
    (this.server.package__mpackage__id === null ? ServersAPI.getSpawnerPackages() : ServersAPI.getMasterPackages())
        // todo: переделать после cleanup api django backend
        .then(response => {
          this.packages = [];
          response.data.packages.forEach(p => this.packages.push({
            value: p.id,
            label: p.name
          }));
          this.selected = this.server.package.id;
        });
  },
  methods: {
    install() {
      Action.serverAction("update", this.server.id, {'package': this.selected});
    }
  }
}
</script>

<style scoped>

</style>