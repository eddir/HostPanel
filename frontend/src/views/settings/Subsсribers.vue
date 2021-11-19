<template>
  <CCol md="6">
    <CCard>
      <CCardHeader>Подписки</CCardHeader>
      <CCardBody>
        <CDataTable
            hover
            :items="subscribers"
            :fields="tableFields"
            head-color="light"
            itemsPerPageSelect
            pagination
        >
          <template slot="remove" slot-scope="{item}">
            <CButton color="danger" size="sm" @click="remove(item)" class="mt-2">Отписать</CButton>
          </template>
        </CDataTable>
        <CInput :value.sync="input.name" label="Комментарий" placeholder="Опционально"/>
        <CInput :value.sync="input.telegram_id" label="TG ID" placeholder="Telegram ID"/>
        <CButton color="success" class="m-2" @click="add">Добавить</CButton>
      </CCardBody>
    </CCard>
  </CCol>
</template>

<script>
import ServersAPI from "@/services/API";
import Action from "@/services/Action";

export default {
  name: "Subscribers",
  data() {
    return {
      input: {
        name: "",
        telegram_id: null
      },
      subscribers: [],
      tableFields: [
        {key: 'telegram_id'},
        {key: 'name', label: "Комментарий"},
        {key: 'remove'}
      ]
    }
  },
  created() {
    this.load();
  },
  methods: {
    load() {
      ServersAPI.getSubs().then(response => {
        this.subscribers = response.data.response;
      });
    },
    add() {
      Action.formAction("add_sub", this.input, this.load);
    },
    remove(sub) {
      console.log(sub);
      Action.formAction("remove_sub", sub, this.load);
    }
  }
}
</script>

<style scoped>

</style>