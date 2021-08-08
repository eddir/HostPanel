<template>
  <CRow>
    <CCol md="12">
      <CCard>
        <CCardHeader>
          Dedicated
        </CCardHeader>
        <CCardBody>
          <CDataTable v-if="dedics.length > 0"
                      hover
                      :items="dedics"
                      :fields="tableFields"
                      head-color="light"
                      itemsPerPageSelect
                      pagination
          >
            <td slot="status" slot-scope="{item}">
              <CBadge :color="item.status.color">
                {{ item.status.message }}
              </CBadge>
            </td>
            <td slot="last_listen" slot-scope="{item}">
              <strong v-if="item.last_listen">
                <timeago :datetime="item.last_listen" locale="ru"></timeago>
              </strong>
              <strong v-else>Неизвестно</strong>
            </td>
            <td slot="log" slot-scope="{item}">
              <CButton v-if="item.log"
                       type="submit" size="sm" color="primary" variant="outline" @click="showLogsModal(item)">
                Log
              </CButton>
            </td>
            <td slot="control-reconnect" slot-scope="{item}" @click="reconnect(item.id)"
                class="text-right align-middle control-icon" style="width: 1%">
              <CIcon name="cil-reload" height="25" class="mx-2"></CIcon>
            </td>
            <td slot="control-reload" slot-scope="{item}" @click="showRebootModal(item)"
                class="text-right align-middle control-icon" style="width: 1%">
              <CIcon name="cil-loop" height="25" class="mx-2"></CIcon>
            </td>
            <td slot="control-remove" slot-scope="{item}" @click="showRemoveModal(item)"
                class="text-right align-middle control-icon" style="width: 1%">
              <CIcon name="cil-trash" height="25" class="mx-2"></CIcon>
            </td>
            <template slot="under-table">
              <router-link :to="'/dedics/create/'">
                <CButton class="mb-2" type="submit" size="sm" color="primary">
                  <CIcon name="cil-plus"/>
                  Создать
                </CButton>
              </router-link>
            </template>
          </CDataTable>
        </CCardBody>
      </CCard>
      <CModal title="Логи" color="primary" :show.sync="logModal">
        <CCard v-if="selectedDedic" class="bg-dark">
          <CCardBody>
            <pre v-html="selectedDedic.log" class="pre-scrollable" id="log"></pre>
          </CCardBody>
        </CCard>
      </CModal>
    </CCol>
    <CModal title="Ребут сервера" color="warning" :show.sync="rebootModal" @update:show="updateRebootModal">
      Во время ребута сервера будут недоступны в течении нескольких минут.
    </CModal>
    <CModal title="Удаление сервера" color="danger" :show.sync="removeModal" @update:show="updateRemoveModal"
            v-if="selectedDedic">
      Удалить дедик {{ selectedDedic.name }}? Будут удалены все данные о нём, в том числе файлы на VPS.
    </CModal>
  </CRow>
</template>

<script>
import ServersAPI from "@/services/API";
import Action from "@/services/Action";

export default {
  name: "Dedics",
  mixins: [ServersAPI],
  data() {
    return {
      tableItems: [],
      tableFields: [
        {key: 'name'},
        {key: 'ip', label: 'IP'},
        //{key: 'country', _classes: 'text-center'}, //todo: вычислять страну по IP адресу
        {key: 'user_root', label: 'Root'},
        {key: 'user_single', label: 'User'},
        {key: 'status'},
        {key: 'last_listen'},
        {key: 'log', label: '', sorter: false, filter: false},
        {key: 'control-reconnect', label: '', sorter: false, filter: false},
        {key: 'control-reload', label: '', sorter: false, filter: false},
        {key: 'control-remove', label: '', sorter: false, filter: false},
      ],
      dedics: [],
      logModal: false,
      selectedDedic: null,
      rebootModal: false,
      removeModal: false,
      loadInterval: null
    }
  },
  created() {
    this.loadDedics();
    this.loadInterval = setInterval(this.loadDedics, 10 * 1000);
  },
  destroyed() {
    clearInterval(this.loadInterval);
  },
  methods: {
    reboot(dedic) {
      Action.quickAction('reboot', dedic);
    },
    remove(dedic) {
      Action.quickAction('dedic_remove', dedic);
    },
    reconnect(dedic) {
      Action.quickAction('dedic_reconnect', dedic);
    },
    loadDedics() {
      ServersAPI.getDedics().then(dedics => {
        this.dedics = dedics.data.dedics;
        this.tableItems = this.dedics.map(item => {
          /**
           * @param item.last_listen последнее время ответа сервера
           */
          if (item.condition) {
            item.status = {
              'code': 'ON',
              'message': 'Подключен',
              'color': 'success'
            };
          } else {
            item.status = {
              'code': 'OF',
              'message': 'Недоступен',
              'color': 'danger'
            }
          }
          return item;
        });
      });
    },
    showLogsModal(dedic) {
      this.selectedDedic = dedic;
      this.logModal = true;
      if (this.selectedDedic.log !== null) {
        this.selectedDedic.log = ServersAPI.parseLog(this.selectedDedic.log);
      }
    },
    showRebootModal(dedic) {
      this.selectedDedic = dedic;
      this.rebootModal = true;
    },
    showRemoveModal(dedic) {
      this.selectedDedic = dedic;
      this.removeModal = true;
    },
    updateRebootModal(open, e, accept) {
      if (!open && accept) {
        Action.quickAction('reboot', this.selectedDedic.id);
      }
    },
    updateRemoveModal(open, e, accept) {
      if (!open && accept) {
        Action.quickAction('dedic_remove', this.selectedDedic.id);
      }
    }
  }
}
</script>

<style scoped>

</style>