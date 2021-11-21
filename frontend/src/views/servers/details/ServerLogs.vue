<template>
  <CCard>
    <CCardHeader>Логи</CCardHeader>
    <CCardBody>
      <CDataTable
          hover
          :items="logs"
          :fields="tableFields"
          head-color="light"
          itemsPerPageSelect
          pagination
      >
        <template slot="download" slot-scope="{item}">
          <td class="text-right align-middle control-icon" style="width: 1%" @click="showDownloadModal(item)">
            <CIcon name="cil-save" height="25" class="mx-2"></CIcon>
          </td>
        </template>

        <template slot="remove" slot-scope="{item}">
          <td class="text-right align-middle control-icon" style="width: 1%" @click="remove(item.name)">
            <CIcon name="cil-trash" height="25" class="mx-2"></CIcon>
          </td>
        </template>
      </CDataTable>
      <CLink color="link" @click="load">Обновить</CLink>
      <CLink :href="'http://' + server.server.dedic__ip + ':' + server.server.watchdog_port"
             target="_blank"
             class="float-right">
        REST
      </CLink>
    </CCardBody>
    <CModal title="Скачивание логов" color="primary" :show.sync="downloadModal" v-if="selected">
      <CInput :value.sync="requested_size" label="Размер" placeholder="Размер в МБ" append="MB"/>
      <CButton v-for="chunk in Math.ceil(selected.size / (requested_size * 2**20))" :key="chunk"
               color="link" @click="download(chunk)">Часть {{ chunk }}
      </CButton>
    </CModal>
  </CCard>
</template>

<script>
import ServersAPI from "@/services/API";
import Utils from "@/services/Utils";
import Action from "@/services/Action";

export default {
  name: "ServerLogs",
  mixins: [Action, ServersAPI, Utils],
  props: {
    server: Object
  },
  data() {
    return {
      logs: [],
      tableFields: [
        {key: 'name', label: 'Название'},
        {key: 'size_formatted', label: 'Размер'},
        {key: 'download', label: ''},
        {key: 'remove', label: ''},
      ],
      selected: null,
      downloadModal: false,

      requested_size: 100,
      requested_chunk: 1,

      download_url: null,
    }
  },
  created() {
    this.load();
  },
  methods: {
    load() {
      this.retry(this.server.server.is_online);
    },
    retry(is_online) {
      if (is_online) {
        ServersAPI.getLogs(this.server.server.id).then(logs => {
          this.$emit('loaded', true);
          this.logs = logs.data.response.map(log => {
            log['size_formatted'] = this.humanFileSize(log['size'], true);
            return log;
          });
        }).catch(() => this.$emit('loaded', false));
      } else {
        this.$emit('loaded', false);
      }
    },
    showDownloadModal(log_file) {
      this.selected = log_file;
      this.downloadModal = true;
    },
    remove(log_file) {
      Action.serverAction("remove_log", this.server.server.id, {"log_file": log_file}, this.load);
    },
    download(part) {
      console.log(part);
      ServersAPI.downloadLog(this.server.server.id, this.selected.name, this.requested_size, part);
    },
  },
}
</script>

<style scoped>

</style>