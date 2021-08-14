<template>
  <div>
    <CButton type="submit" color="primary" variant="outline" @click="modal = true">
      Установить
    </CButton>
    <CModal title="Установка" color="info" :show.sync="modal" @update:show="updateModal">
      <p>Сервера для установки сборки {{ pack.name }}:</p>
      <CListGroup>
        <CListGroupItem tag="label" class="clickable" v-for="server in servers" v-bind:key="server.id">
          <CInputCheckbox :checked.sync="selected[server.id]"></CInputCheckbox>
          <span class="mx-4">{{ server.name }}</span>
        </CListGroupItem>
        <CListGroupItem tag="label" class="clickable" color="secondary">
          <CInputCheckbox :checked.sync="selected.every(e => e)" @update:checked="selectAll"></CInputCheckbox>
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
    }
  },
  watch: {
    servers() {
      this.servers.forEach(server => this.selected[server.id] = false);
    },
  },
  methods: {
    updateModal(open, e, accept) {
      if (!open && accept) {
        for (let server in this.selected) {
          this.selected[server] && Action.serverAction("update", server, {'package': this.pack.id});
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