<template>
  <CContainer>
    <CRow>
      <CCol md="6">
        <CCard>
          <CCardHeader>HostPanel</CCardHeader>
          <CCardBody>
            <p><b>Версия панели:</b> {{ version.panel }}</p>
            <p><b>Версия Caretaker:</b> {{ version.caretaker }}</p>
            <p><b>Версия MySQL:</b> {{ version.mysql }}</p>
          </CCardBody>
        </CCard>
      </CCol>
      <CCol md="6">
        <CCard>
          <CCardHeader>Debug</CCardHeader>
          <CCardBody>
            <CButton variant="ghost" color="info" class="m-2" @click="cancelTasks">Отменить все задачи</CButton>
            <div class="input-table">
              <CSelect :value.sync="selectedServer" :options="servers" addInputClasses="m-2"></CSelect>
              <CSelect :value.sync="selectedStatusType" :options="statusTypes" addInputClasses="m-2"></CSelect>
              <CButton variant="ghost" color="info" class="m-2" @click="setStatus">Установить статус</CButton>
            </div>
            <CButton variant="ghost" color="success" class="m-2" @click="ping">Ping</CButton>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
import ServersAPI from "@/services/API";
import Action from "@/services/Action";
import Vue from "vue";

export default {
  name: "Settings",
  data() {
    return {
      version: {
        panel: null,
        caretaker: null,
        mysql: null,
      },
      servers: [],
      selectedServer: null,
      statusTypes: ['IN', 'ST', 'RN', 'PS', 'SP', 'TR', 'DL', 'RB'],
      selectedStatusType: 'RN',
    }
  },
  created() {
    ServersAPI.getVersion().then(response => {
      this.version = response.data.response;
    })
    ServersAPI.getServers().then(response => {
      this.servers = response.data.response.servers.map(server => {
        return {
          value: server.id,
          label: `${server.id} - '${server.name}'`,
        }
      });
      this.selectedServer = this.servers[0].value;
    })
  },
  methods: {
    cancelTasks() {
      Action.quickAction("cancelTasks");
    },
    setStatus() {
      Action.serverAction("set_status", this.selectedServer, {condition: this.selectedStatusType});
    },
    ping() {
      ServersAPI.ping().then(response => Vue.$toast.success(response.data.response));
    }
  },
}
</script>

<style scoped>

</style>