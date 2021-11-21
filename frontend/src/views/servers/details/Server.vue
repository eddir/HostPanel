<template>
  <CContainer>
    <CRow v-if="server && server.status">
      <CCol md="6">
        <CCard>
          <CCardHeader>
            {{ server.server.name }}

            <CBadge v-if="server.server.is_online" color="success">Онлайн</CBadge>
            <CBadge v-else color="danger">Не в сети</CBadge>
          </CCardHeader>
          <CCardBody>
            <ul class="list-unstyled">
              <li>
                <strong>Online: </strong>
                <timeago :datetime="server.status.created_at" locale="ru"></timeago>
              </li>
              <li><strong>IP: </strong> {{ server.server.dedic__ip }}</li>
              <li><strong>Dedic: </strong> {{ server.server.dedic__name }}</li>
              <li><strong>Root: </strong> {{ server.server.dedic__user_root }}</li>
              <li><strong>Root пароль: </strong> {{ server.server.dedic__password_root }}</li>
              <li><strong>User: </strong> {{ server.server.dedic__user_single }}</li>
              <li><strong>User пароль: </strong> {{ server.server.dedic__password_single }}</li>
              <li><strong>Сборка: </strong> {{ server.server.package.name }}</li>
              <li><strong>Состояние: </strong>
                <CBadge :color="server.status.condition.badge">{{ server.status.condition.message }}</CBadge>
              </li>
              <li><strong>Watchdog: </strong>
                <CBadge v-if="watchdog_status" color="success">Доступен</CBadge>
                <CBadge v-else color="danger">Нет связи</CBadge>
              </li>
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

        <CCard v-if="stat.cpu_usage !== null">
          <CRow class="text-center">
            <CCol md sm="12" class="m-sm-2 m-0">
              <div class="text-muted">CPU</div>
              <strong>{{ stat.cpu_usage }}%</strong>
              <CProgress
                  class="progress-xs mt-2"
                  :precision="1"
                  color="success"
                  :value="stat.cpu_usage"
              />
            </CCol>
          </CRow>
        </CCard>

        <CCard v-if="stat.mem_total">
          <CRow class="text-center">
            <CCol md sm="12" class="m-sm-2 m-0">
              <div class="text-muted">Memory</div>
              <strong>{{ stat.mem_usage }} MB
                ({{ stat.mem_percent }}%)</strong>
              <CProgress
                  class="progress-xs mt-2"
                  :precision="1"
                  :color="color(stat.mem_percent)"
                  :value="stat.mem_percent"
              />
            </CCol>
          </CRow>
        </CCard>

        <CCard v-if="stat.disk_total">
          <CRow class="text-center">
            <CCol md sm="12" class="m-sm-2 m-0">
              <div class="text-muted">Диск</div>
              <strong>{{ stat.disk_usage }} MB
                ({{ stat.disk_percent }}%)</strong>
              <CProgress
                  class="progress-xs mt-2"
                  :precision="1"
                  :color="color(stat.disk_percent)"
                  :value="stat.disk_percent"
              />
            </CCol>
          </CRow>
        </CCard>

        <CCard v-if="stat.processes">
          <CCardHeader>Процессы</CCardHeader>
          <CCardBody>
            <CDataTable
                :items="stat.processes"
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
              <template #cpu_percent="{item}">
                <td>{{ item.cpu_percent }}%</td>
              </template>
              <template #memory_percent="{item}">
                <td>{{ item.memory_percent }}%</td>
              </template>
              <template #memory_usage="{item}">
                <td>{{ item.memory_usage }} MB</td>
              </template>
            </CDataTable>
          </CCardBody>
        </CCard>

        <ServerLogs :server="server" @loaded="updateWatchdogStatus" ref="ServerLogs"></ServerLogs>

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
 * @param server.server.is_online запущен ли в данный момент сервер
 */
export default {
  name: "Server",
  mixins: [Utils, Parsers],
  data() {
    return {
      server: null,
      stat: {
        cpu_usage: null,
        mem_usage: null,
        mem_available: null,
        mem_total: null,
        disk_usage: null,
        disk_available: null,
        disk_total: null,
      },

      processesFields: [
        {key: 'pid', label: 'PID'},
        {key: 'name', label: 'Процесс'},
        {key: 'username'},
        {key: 'cpu_percent', label: 'CPU'},
        {key: 'memory_percent', label: 'Mem, %'},
        {key: 'memory_usage', label: 'Mem, MB'},
      ],
      watchdog_status: false,

      deleteModal: false,
      forgetModal: false,
      reinstallModal: false,
      loadInterval: null,

      username: undefined,

      updateInterval: 5, // сек, как часто обновлять данные о процессах и cpu/mem usage
      firstLoad: true, // флаг для начала отслеживания статистики
    }
  },
  components: {ServerConfig, ServerPackage, 'ServerLogs': ServerLogs},
  created() {
    this.load();
    this.loadStat();
    this.loadIntervals = [
        setInterval(this.load, 10 * 1000),
        setInterval(this.loadStat, this.updateInterval * 1000),
    ];
  },
  destroyed() {
    this.loadIntervals.forEach(interval => clearInterval(interval));
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
        }
        
        if (server_data.server.processes) {
          server_data.server.processes = JSON.parse(server_data.server.processes);
        }

        // Если поменялся статус сервера онлайн, то нужно обновить информацию в табличке с логами
        let is_changed = this.server && this.server.server.is_online !== server_data.server.is_online;

        this.server = server_data;

        if (is_changed) {
          this.$refs.ServerLogs.retry(this.server.server.is_online);
        }

        if (this.username === undefined) {
          this.username = this.server.server.dedic__user_single;
        }

        if (this.firstLoad && server_data.server.is_online) {
          this.firstLoad = false;
          this.loadStat(true);
        }
      });
    },
    loadStat(force = false) {
      if (force || (this.server && this.server.server.is_online)) {
        ServersAPI.getStat(this.$route.params.id).then(response => {
          // todo: переделать этот код. Очен спешил.
          this.stat.cpu_usage = response.data.response.cpu_usage;
          this.stat.mem_available = response.data.response.mem_available;
          this.stat.mem_total = response.data.response.mem_total;
          this.stat.mem_usage = response.data.response.mem_total - this.stat.mem_available;
          this.stat.mem_percent = Math.round(this.stat.mem_usage / this.stat.mem_total * 100);
          this.stat.disk_available = response.data.response.disk_available;
          this.stat.disk_total = response.data.response.disk_total;
          this.stat.disk_usage = this.stat.disk_total - this.stat.disk_available;
          this.stat.disk_percent = Math.round(this.stat.disk_usage / this.stat.disk_total * 100)
          this.stat.processes = JSON.parse(response.data.response.processes);
        });
      }
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
    updateWatchdogStatus(state) {
      this.watchdog_status = state;
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
    },
  },
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