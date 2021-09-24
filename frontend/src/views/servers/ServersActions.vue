<template>
  <div>
    <span class="float-left m-2">Выбрано: {{ selected.length }}</span>
    <CSelect class="float-left mx-2" :options="options" :value.sync="action"></CSelect>
    <CButton class="float-left" color="primary" @click="showModal">Выполнить</CButton>

    <CModal :title="title" color="warning" :show.sync="modal" @update:show="updateModal">
      Будет выполнено <b>{{ title }}</b> для серверов:
      <ul>
        <li v-for="server in selected" v-bind:key="server.host.id">{{ server.host.name }} (#{{ server.host.id }})</li>
      </ul>
    </CModal>
  </div>
</template>

<script>
import Action from "@/services/Action";

export default {
  name: "ServersActions",
  props: {
    selected: {},
  },
  data() {
    return {
      title: "",
      action: "",

      modal: false,

      options: [],

      actions: {
        'start': {label: "Запустить", title: "Запуск"},
        'stop': {label: "Остановить", title: "Остановка"},
        'reinstall': {label: "Переустановить", title: "Переустановка"},
        'updateCaretaker': {label: "Обновить скрипт", title: "Обновлние скрипта"},
        'reboot': {label: "Ребут", title: "Ребут"},
        'remove': {label: "Удалить", title: "Удаление"},
        'forget': {label: "Забыть", title: "Забытие"},
      },
    }
  },
  created() {
    this.action = Object.keys(this.actions)[0];
    for (let action in this.actions) {
      this.options.push({value: action, label: this.actions[action].label});
    }
  },
  methods: {
    showModal() {
      this.title = this.actions[this.action].title;
      this.modal = true;
    },
    updateModal(open, e, accept) {
      if (!open && accept) {
        this.selected.forEach(server => {
          Action.quickAction(this.action, server.host.id);
        })
      }
    },
  },
}
</script>

<style scoped>

</style>