<template>
  <CContainer v-if="server">
    <CRow>
      <CCol md="6">
        <CCard>
          <CCardHeader>{{ server.server.name }}</CCardHeader>
          <CCardBody>
            <ul class="list-unstyled">
              <li><strong>Статус: </strong>
                <CBadge :color="server.status.condition.badge">{{ server.status.condition.message }}</CBadge>
              </li>
              <li><strong>IP:</strong> {{ server.server.dedic__ip }}</li>
              <li><strong>Root:</strong> {{ server.server.dedic__user_root }}</li>
              <li><strong>Root пароль:</strong> {{ server.server.dedic__password_root }}</li>
              <li><strong>User:</strong> {{ server.server.dedic__user_single }}</li>
              <li><strong>User пароль:</strong> {{ server.server.dedic__password_single }}</li>
            </ul>
          </CCardBody>
        </CCard>
      </CCol>
      <CCol md="6">
        <CCard>
          <CCardBody>
            <div class="buttons-panel">
              <ul>
                <li v-if="server.status.condition.code === 'SP' || true">
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
        <CCard class="bg-dark">
          <CCardBody>
            <pre v-html="server.server.log" class="pre-scrollable"></pre>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
    <CModal title="Удаление сервера" color="danger" :show.sync="deleteModal" @update:show="updateRemoveModal">
      Удалить сервер {{ server.server.name }}? Будут удалены все данные о нём, в том числе файлы на сервере.
    </CModal>
    <CModal title="Убирание сервера" color="danger" :show.sync="forgetModal" @update:show="updateForgetModal">
      Сервер {{ server.server.name }} будет удалён из панели, но файлы останутся на сервере. Продолжить?
    </CModal>
    <CModal title="Переустановка сервера" color="warning" :show.sync="reinstallModal" @update:show="updateReinstallModal">
      Сервер {{ server.server.name }} будет удалён вместе с файлами и установлен вновь. Продолжить?
    </CModal>
  </CContainer>
</template>

<script>
import ServersAPI from "../../services/Server.vue";
import Action from "@/services/Action";
import Vue from "vue";

/**
 * @param server.server.dedic__ip IP адрес сервера
 * @param server.server.dedic__user_root Root пользователь
 * @param server.server.dedic__user_single Пользователь из под которого запущен сервер
 * @param server.server.dedic__password_root Пароль от рут пользователя
 * @param server.server.dedic__password_single Пароль от простого пользователя
 */
export default {
  name: "Server",
  data() {
    return {
      server: null,
      deleteModal: false,
      forgetModal: false,
      reinstallModal: false
    }
  },
  created() {
    this.load();
    setInterval(this.load, 10 * 1000);
  },
  methods: {
    load() {
      ServersAPI.getServer(this.$route.params.id).then((server) => {
        let server_data = server.data;
        server_data.status.condition = ServersAPI.parseStatus(server_data.status.condition);
        server_data.server.log = ServersAPI.parseLog(server_data.server.log);
        this.server = server_data;
      });
    },
    updateRemoveModal(open, e, accept) {
      if (!open && accept) {
        //Action.serverAction('remove', this.server.server.id);
        Vue.$toast.warning("Фича временно недоступна");//todo
      }
    },
    updateForgetModal(open, e, accept) {
      if (!open && accept) {
        Action.serverAction('forget', this.server.server.id);
      }
    },
    updateReinstallModal(open, e, accept) {
      if (!open && accept) {
        Action.serverAction('reinstall', this.server.server.id);
      }
    },
    start() {
      Action.serverAction('start', this.server.server.id);
    },
    stop() {
      Action.serverAction('stop', this.server.server.id);
    }
  }
}
</script>

<style scoped>

.pre-scrollable {
  background-color: #636f83;
  color: #fff;
}

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