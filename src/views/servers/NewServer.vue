<template>
  <CContainer>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>Создание {{ input.type === "master" ? 'мастера' : 'спавнера для ' + parentName }}</CCardHeader>
          <CCardBody>
            <CRow>
              <CCol sm="6">
                <CInput :value.sync="input.name" label="Name" placeholder="Название сервера"/>
              </CCol>
              <CCol sm="6">
                <CSelect @change="prepareConfig" :value.sync="input.dedic" label="Дедик" :options="dedics"/>
              </CCol>
            </CRow>
            <CRow>
              <CCol sm="6">
                <CSelect :value.sync="input.package" label="Сборка" :options="packages"/>
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
import ServersAPI from "@/services/API";
import Action from "@/services/Action";
import Vue from "vue";

export default {
  name: "NewServer",
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
      parentName: "",
      dedics: [],
      packages: [],
      dedics_data: [],
    }
  },
  created() {
    if (this.$route.params.id) {
      this.input.type = "spawner"
      this.input.parent = parseInt(this.$route.params.id);
    }
    ServersAPI.getServers().then((response) => {
      this.dedics = [];
      this.packages = [];
      this.dedics_data = response.data.dedics;

      this.dedics_data.forEach(dedic => this.dedics.push({
        value: dedic.id,
        label: dedic.name
      }));
      this.input.dedic = this.dedics_data[0].id;

      if (this.input.type === "master") {
        this.input.package = response.data.m_packages[0].id;

        response.data.m_packages.forEach(pack => this.packages.push({
          value: pack.id,
          label: pack.name
        }));

      } else {
        let parent = response.data.servers.find(s => s.id === this.input.parent);

        if (parent) {
          this.parentName = parent.name;
        } else {
          Vue.$toast.error("Неизвестный мастер");
        }

        this.input.package = response.data.sr_packages[0].id;
        response.data.sr_packages.forEach(pack => this.packages.push({
          value: pack.id,
          label: pack.name
        }));
      }
      this.prepareConfig();
    });
  },
  methods: {
    prepareConfig() {
      if (this.input.type === "spawner") {
        let dedic = this.dedics_data.find((d) => d.id === this.input.dedic);
        this.input.config =
            "-mstStartSpawner=true\n" +
            "-mstStartClientConnection=true\n" +
            "-mstMasterIp=" + dedic.ip + "\n" +
            "-mstMasterPort=5000\n" +
            "-mstRoomIp=" + dedic.ip + "\n" +
            "-mstRoomExe=\\home\\" + dedic.user_single + "\\HostPanel\\Pack\\Room\\Room.x86_64\n" +
            "-mstMaxProcesses=1";
      } else {
        this.input.config = "-mstStartMaster=true\n" +
            "-mstStartClientConnection=true\n" +
            "-mstMasterIp=127.0.0.1\n" +
            "-mstMasterPort=5000";
      }
    },
    send() {
      Action.formAction("create_server", this.input, () => window.location.href = '/#/');
    }
  }
}
</script>

<style scoped>
textarea {
  height: 100px;
}
</style>