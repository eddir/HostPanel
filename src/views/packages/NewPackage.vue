<template>
  <CContainer>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>Загрузка сборки {{ type }}</CCardHeader>
          <CCardBody>
            <CRow>
              <CCol sm="6">
                <CInput :value.sync="input.name" label="Name" placeholder="Название"/>
              </CCol>
            </CRow>
            <CRow>
              <CCol sm="6">
                <CInputFile v-if="type==='master'" :placeholder="input.master.name" @change="handleMaster" horizontal
                            custom label="Master"/>
                <CInputFile v-else :placeholder="input.spawner.name" @change="handleSpawner" horizontal custom
                            label="Spawner"/>
              </CCol>
              <CCol sm="6" v-if="type==='spawner'">
                <div class="ml-1">
                  <CInputFile :placeholder="input.room.name" @change="handleRoom" horizontal custom label="Room"/>
                </div>
              </CCol>
            </CRow>
            <CProgress v-if="uploadPercentage !== -1" :value="uploadPercentage" color="success" animated class="my-3"/>
            <CButton key="send" color="success" class="m-2" @click="send">Загрузить</CButton>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
import Action from "@/services/Action";

export default {
  name: "NewPackage",
  data() {
    return {
      type: "",
      input: {
        name: "",
        master: "",
        spawner: "",
        room: "",
      },
      uploadPercentage: -1
    }
  },
  created() {
    this.type = this.$route.params.type;
  },
  methods: {
    send() {
      Action.fileAction(
          this.type === "master" ? "upload_master_package" : "upload_spawner_package",
          this.input,
          progressEvent => {
            this.uploadPercentage = Math.round((progressEvent.loaded / progressEvent.total) * 1000) / 10;
          },
          () => window.location.href = `/#/packages/${this.type}/`
      );
    },
    handleMaster(files) {
      this.input.master = files[0];
    },
    handleSpawner(files) {
      this.input.spawner = files[0];
    },
    handleRoom(files) {
      this.input.room = files[0];
    },
  }
}
</script>

<style scoped>

</style>