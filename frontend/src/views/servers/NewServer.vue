<template>
  <CContainer>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>
            <template v-if="input.type === 'master'">Создание мастера</template>
            <template v-if="input.type === 'spawner'">Создание спавнера для {{ parentName }}</template>
            <template v-if="input.type === 'custom'">Создание custom</template>
          </CCardHeader>
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
        custom: false
      },
      parentName: "",
      dedics: [],
      packages: [],
      dedics_data: [],
    }
  },
  created() {
    if (this.$route.params.id) {
      if (this.$route.params.id === "custom") {
        this.input.type = "custom"
        this.input.custom = true;
      } else {
        this.input.parent = parseInt(this.$route.params.id);
        this.input.type = "spawner"
      }
    }
    ServersAPI.getServers().then((response) => {
      let data = response.data.response;
      this.dedics = [];
      this.packages = [];
      this.dedics_data = data.dedics;

      this.dedics_data.forEach(dedic => this.dedics.push({
        value: dedic.id,
        label: dedic.name,
      }));
      this.input.dedic = this.dedics_data[0].id;

      if (this.input.type === "master" || this.input.type === "custom") {
        let packages = this.input.type === "master" ? data.m_packages : data.c_packages;

        this.input.package = packages[0].id;

        packages.forEach(pack => this.packages.push({
          value: pack.id,
          label: pack.name,
        }));

      } else {
        let parent = data.servers.find(s => s.id === this.input.parent);

        if (parent) {
          this.parentName = parent.name;
        } else {
          throw new Error("Неизвестный мастер");
        }

        this.input.package = data.sr_packages[0].id;
        data.sr_packages.forEach(pack => this.packages.push({
          value: pack.id,
          label: pack.name,
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
            "-mstMasterIp=0.0.0.0\n" +
            "-mstMasterPort=5000";
      }
    },
    send() {
      Action.formAction("create_server", this.input, () => window.location.href = '/#/');
    },
  },
}
</script>

<style scoped>
textarea {
  height: 100px;
}
</style>