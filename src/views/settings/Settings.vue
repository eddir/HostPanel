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
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
import ServersAPI from "@/services/API";
import Action from "@/services/Action";

export default {
  name: "Settings",
  data() {
    return {
      version: {
        panel: null,
        caretaker: null,
        mysql: null
      }
    }
  },
  created() {
    ServersAPI.getVersion().then(response => {
      this.version = response.data.response;
    })
  },
  methods: {
    cancelTasks() {
      Action.quickAction("cancelTasks");
    }
  }
}
</script>

<style scoped>

</style>