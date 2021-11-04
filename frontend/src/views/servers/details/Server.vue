<template>
  <CContainer>
    <CRow v-if="server && server.status">
      <CCol md="6">
        <CCard>
          <CCardHeader>{{ server.server.name }}</CCardHeader>
          <CCardBody>
            <ul class="list-unstyled">
              <li>
                <strong>Статус: </strong>
                <CBadge :color="server.status.condition.badge">{{ server.status.condition.message }}</CBadge>
              </li>
              <li><strong>IP:</strong> {{ server.server.dedic__ip }}</li>
              <li><strong>Dedic:</strong> {{ server.server.dedic__name }}</li>
              <li><strong>Root:</strong> {{ server.server.dedic__user_root }}</li>
              <li><strong>Root пароль:</strong> {{ server.server.dedic__password_root }}</li>
              <li><strong>User:</strong> {{ server.server.dedic__user_single }}</li>
              <li><strong>User пароль:</strong> {{ server.server.dedic__password_single }}</li>
              <li><strong>Сборка:</strong> {{ server.server.package.name }}</li>
              <li><strong><a :href="'http://' + server.server.dedic__ip + ':' + server.server.watchdog_port">Watchdog</a></strong></li>
            </ul>
          </CCardBody>
        </CCard>
        <CCard>
          <CCardHeader>Конфиг</CCardHeader>
          <CCardBody>
            <ServerConfig :rawConfig="server.server.config" :serverId="server.server.id"
                          @update:config="updateConfig"></ServerConfig>
          </CCardBody>
        </CCard>
        <CCard>
          <CCardHeader>Сборка</CCardHeader>
          <CCardBody>
            <ServerPackage :server="server.server"></ServerPackage>
          </CCardBody>
        </CCard>

        <CCard class="bg-dark">
          <CCardBody>
            <pre v-html="server.server.log" class="pre-scrollable" id="console"></pre>
          </CCardBody>
        </CCard>
      </CCol>
      <CCol md="6">
        <CCard>
          <CCardBody>
            <div class="buttons-panel">
              <ul>
                <li v-if="server.status.condition.code === 'SP'">
                  <i @click="start()">
                    <CIcon name="cil-media-play" class="text-success" height="30"></CIcon>
                  </i>
                  <span>Старт</span>
                </li>
                <li v-if="server.status.condition.code === 'RN'">
                  <i @click="stop()">
                    <CIcon name="cil-media-stop" class="text-danger" height="30"></CIcon>
                  </i>
                  <span>Стоп</span>
                </li>
                <li>
                  <i @click="reinstallModal = true">
                    <CIcon name="cil-loop" class="text-warning" height="30"></CIcon>
                  </i>
                  <span>Переуст.</span>
                </li>
                <li v-if="server.children === false && (server.status == null ||
                    (server.status.condition.code !== 'RN' && server.status.condition.code !== 'SP'))">
                  <i @click="deleteModal = true">
                    <CIcon name="cil-trash" class="text-danger" height="30"></CIcon>
                  </i>
                  <span>Удалить</span>
                </li>
                <li>
                  <i @click="forgetModal = true">
                    <CIcon name="cil-x-circle" class="text-danger" height="30"></CIcon>
                  </i>
                  <span>Убрать</span>
                </li>
              </ul>
            </div>
          </CCardBody>
        </CCard>

        <CCard v-if="server.status.cpu_usage !== null">
          <CRow class="text-center">
            <CCol md sm="12" class="m-sm-2 m-0">
              <div class="text-muted">CPU</div>
              <strong>{{ server.status.cpu_usage }}%</strong>
              <CProgress
                  class="progress-xs mt-2"
                  :precision="1"
                  color="success"
                  :value="server.status.cpu_usage"
              />
            </CCol>
          </CRow>
        </CCard>

        <CCard v-if="server.status.mem_total">
          <CRow class="text-center">
            <CCol md sm="12" class="m-sm-2 m-0">
              <div class="text-muted">Memory</div>
              <strong>{{ server.status.mem_usage }} MB
                ({{ server.status.mem_percent }}%)</strong>
              <CProgress
                  class="progress-xs mt-2"
                  :precision="1"
                  :color="color(server.status.mem_percent)"
                  :value="server.status.mem_percent"
              />
            </CCol>
          </CRow>
        </CCard>

        <CCard v-if="server.status.disk_total">
          <CRow class="text-center">
            <CCol md sm="12" class="m-sm-2 m-0">
              <div class="text-muted">Диск</div>
              <strong>{{ server.status.disk_usage }} MB
                ({{ server.status.disk_percent }}%)</strong>
              <CProgress
                  class="progress-xs mt-2"
                  :precision="1"
                  :color="color(server.status.disk_percent)"
                  :value="server.status.disk_percent"
              />
            </CCol>
          </CRow>
        </CCard>

        <CCard v-if="server.server.processes">
          <CCardHeader>Процессы</CCardHeader>
          <CCardBody>
            <CDataTable
                :items="server.server.processes"
                :fields="processesFields"
                column-filter
                table-filter
                items-per-page-select
                hover
                sorter
                :sorterValue="{column: 'memory_percent', asc: false}"
                :columnFilterValue="{username: username}"
                cleaner
                pagination
                @update:column-filter-value="saveFilterValue"
            >
              <template #cpu_percent="{item}"><td>{{item.cpu_percent}}%</td></template>
              <template #memory_percent="{item}"><td>{{item.memory_percent}}%</td></template>
              <template #memory_usage="{item}"><td>{{item.memory_usage}} MB</td></template>
            </CDataTable>
          </CCardBody>
        </CCard>

        <ServerLogs :server="server"></ServerLogs>

      </CCol>
      <CModal title="Удаление сервера" color="danger" :show.sync="deleteModal" @update:show="updateRemoveModal">
        Удалить сервер {{ server.server.name }}? Будут удалены все данные о нём, в том числе файлы на VPS.
      </CModal>
      <CModal title="Убирание сервера" color="danger" :show.sync="forgetModal" @update:show="updateForgetModal">
        Сервер {{ server.server.name }} будет удалён из панели, но файлы останутся на VPS. Продолжить?
      </CModal>
      <CModal title="Переустановка сервера" color="warning" :show.sync="reinstallModal"
              @update:show="updateReinstallModal">
        Сервер {{ server.server.name }} будет удалён вместе с файлами и установлен вновь. Продолжить?
      </CModal>
    </CRow>
  </CContainer>
</template>

<script>
import ServersAPI from "@/services/API.vue";
import Action from "@/services/Action";
import ServerConfig from "@/views/servers/details/ServerConfig";
import ServerPackage from "@/views/servers/details/ServerPackage";
import Utils from "@/services/Utils";
import ServerLogs from "@/views/servers/details/ServerLogs";
import Parsers from "@/services/Parsers";

/**
 * @param server.server.dedic__ip IP адрес сервера
 * @param server.server.dedic__user_root Root пользователь
 * @param server.server.dedic__user_single Пользователь из под которого запущен сервер
 * @param server.server.dedic__password_root Пароль от рут пользователя
 * @param server.server.dedic__password_single Пароль от простого пользователя
 * @param server.server.watchdog_port Порт веб интерфейса скрипта Watchdog
 * @param server.server.processes Список запущенных программ на вдс
 */
export default {
  name: "Server",
  mixins: [Utils, Parsers],
  data() {
    return {
      server: null,
      processesFields: [
        {key: 'pid', label: 'PID'},
        {key: 'name', label: 'Процесс'},
        {key: 'username'},
        {key: 'cpu_percent', label: 'CPU'},
        {key: 'memory_percent', label: 'Mem, %'},
        {key: 'memory_usage', label: 'Mem, MB'},
      ],
      deleteModal: false,
      forgetModal: false,
      reinstallModal: false,
      loadInterval: null,

      username: undefined
    }
  },
  components: {ServerConfig, ServerPackage, ServerLogs},
  created() {
    this.load();
    this.loadInterval = setInterval(this.load, 10 * 1000);
  },
  destroyed() {
    clearInterval(this.loadInterval);
  },
  updated() {
    if (this.server && this.server.status) {
      let console_element = document.getElementById('console');
      console_element.scrollTop = console_element.scrollHeight;
    }
  },
  methods: {
    load() {
      ServersAPI.getServer(this.$route.params.id).then((server) => {
        let server_data = server.data.response;
        server_data.server.log = server_data.server.log ? Parsers.parseLog(server_data.server.log) : "Нет данных";
        if (server_data.status) {
          server_data.status.condition = Parsers.parseStatus(server_data.status.condition);
          server_data.status.mem_usage = server_data.status.mem_total - server_data.status.mem_available;
          server_data.status.mem_percent = Math.round(server_data.status.mem_usage / server_data.status.mem_total * 100)
          server_data.status.disk_usage = server_data.status.disk_total - server_data.status.disk_available;
          server_data.status.disk_percent = Math.round(server_data.status.disk_usage / server_data.status.disk_total * 100)
        }
        if (server_data.server.processes) {
          server_data.server.processes = JSON.parse(server_data.server.processes);
        }
        this.server = server_data;

        if (this.username === undefined) {
          this.username = this.server.server.dedic__user_single;
        }
      });
    },
    updateConfig(config) {
      Action.serverAction("update_config", this.server.server.id, config);
    },
    updateRemoveModal(open, e, accept) {
      if (!open && accept) {
        Action.quickAction('remove', this.server.server.id);
      }
    },
    updateForgetModal(open, e, accept) {
      if (!open && accept) {
        Action.quickAction('forget', this.server.server.id, () => window.location.href = '/#/');
      }
    },
    updateReinstallModal(open, e, accept) {
      if (!open && accept) {
        Action.quickAction('reinstall', this.server.server.id);
      }
    },
    saveFilterValue(value) {
      if ('username' in value) {
        this.username = value.username;
      }
    },
    start() {
      Action.quickAction('start', this.server.server.id);
    },
    stop() {
      Action.quickAction('stop', this.server.server.id);
    }
  }
}
</script>

<style scoped>

.buttons-panel i {
  background: #fafafa;
  width: 60px;
  height: 60px;
  line-height: 57px;
  border-radius: 50%;
  text-align: center;
  cursor: pointer;
}

.buttons-panel li {
  height: 120px;
  width: 33%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0;
}

.buttons-panel span {
  font-weight: 500;
  text-transform: uppercase;
  font-size: 15px;
  padding-top: 16px;
  color: #616161;
}

.buttons-panel ul {
  padding: 0 4px;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
}
</style>