<template>
  <div>
    <CButton type="submit" class="mx-2" color="primary" variant="outline" @click="update">
      Установить
    </CButton>
    <CButton type="submit" class="mx-2" color="success" variant="outline" @click="updateAndRun">
      Установить и запустить
    </CButton>
    <CModal title="Установка" color="info" :show.sync="modal" @update:show="updateModal">
      <p>Сервера для установки сборки {{ pack.name }}:</p>
      <CListGroup>
        <CListGroupItem tag="label" class="clickable" v-for="server in servers" v-bind:key="server.id">
          <CInputCheckbox :checked.sync="selected[server.id]"></CInputCheckbox>
          <span class="mx-4">{{ server.name }}</span>
        </CListGroupItem>
        <CListGroupItem tag="label" class="clickable" color="secondary">
          <CInputCheckbox :checked.sync="selected.length > 0 && selected.every(e => e)"
                          @update:checked="selectAll"></CInputCheckbox>
          <span class="mx-4"><b>Выбрать все</b></span>
        </CListGroupItem>
      </CListGroup>
    </CModal>
  </div>
</template>

<script>

import Action from "@/services/Action";

export default {
  name: "InstallPackage",
  props: {
    pack: {},
    type: null,
    servers: [],
  },
  data() {
    return {
      selected: [],
      modal: false,
      action: "",
    }
  },
  watch: {
    servers() {
      this.servers.forEach(server => this.selected[server.id] = false);
    },
  },
  methods: {
    update() {
      this.modal = true;
      this.action = "update";
    },
    updateAndRun() {
      this.modal = true;
      this.action = "updateAndRun";
    },
    updateModal(open, e, accept) {
      if (!open && accept) {
        for (let server in this.selected) {
          if (this.selected[server]) {
            Action.serverAction("update", server, {'package': this.pack.id});
            if (this.action === "updateAndRun") {
              Action.quickAction("start", server);
            }
          }
        }
      }
    },
    selectAll(checked) {
      let newSelected = []
      this.servers.forEach(server => newSelected[server.id] = checked);
      this.selected = newSelected;
    },
  },
}
</script>

<style scoped>

</style>