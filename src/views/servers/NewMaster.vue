<template>
  <CContainer>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>Создание мастера</CCardHeader>
          <CCardBody>
            <CRow>
              <CCol sm="6">
                <CInput :value.sync="input.name" label="Name" placeholder="Название сервера"/>
              </CCol>
              <CCol sm="6">
                <CSelect :value.sync="input.dedic" label="Дедик" :options="dedics"/>
              </CCol>
            </CRow>
            <CRow>
              <CCol sm="6">
                <CSelect :value.sync="input.package" label="Сборка" :options="packages.master"/>
              </CCol>
              <CCol sm="6">
                <div class="form-group">
                  <label>SSH ключ</label>
                  <div class="form-group">
                    <CSwitch :checked.sync="input.ssh_key" color="dark"/>
                  </div>
                </div>
              </CCol>
            </CRow>
            <CTextarea :value.sync="input.config" label="application.cfg"></CTextarea>
            <CButton key="send" color="success" class="m-2" @click="send">Создать</CButton>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
import ServersAPI from "@/services/Server";
import Action from "@/services/Action";

export default {
  name: "NewMaster",
  data() {
    return {
      input: {
        name: null,
        parent: null,
        dedic: null,
        package: null,
        ssh_key: false,
        config: null,
        type: "master",
      },
      dedics: [],
      packages: {
        master: [],
        spawner: []
      },
    }
  },
  created() {
    ServersAPI.getServers().then((response) => {
      this.dedics = [];
      this.packages = {
        master: [],
        spawner: []
      }

      response.data.dedics.forEach(dedic => this.dedics.push({
        value: dedic.id,
        label: dedic.name
      }));
      this.input.dedic = response.data.dedics[0].id;

      response.data.m_packages.forEach(pack => this.packages.master.push({
        value: pack.id,
        label: pack.name
      }));
      this.input.package = response.data.m_packages[0].id;

      response.data.sr_packages.forEach(pack => this.packages.spawner.push({
        value: pack.id,
        label: pack.name
      }));
    });
  },
  methods: {
    send() {
      Action.formAction("create_server", this.input, () => window.location.href = '/#/');
    }
  }
}
</script>

<style scoped>
</style>