<template>
  <div>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>
            Мастер сервера
          </CCardHeader>
          <CCardBody>
            <CDataTable
                class="mb-0 table-outline"
                hover
                :items="tableItems"
                :fields="tableFields"
                head-color="light"
                no-sorting
            >
              <td slot="host" slot-scope="{item}">
                <div>{{ item.host.name }}</div>
                <div class="small text-muted">
                  {{ item.host.dedic + ' | ' + item.host.package }}
                </div>
              </td>
              <td
                  slot="country"
                  slot-scope="{item}"
                  class="text-center"
              >
                <CIcon
                    :name="item.country.flag"
                    height="25"
                />
              </td>
              <td slot="usage" slot-scope="{item}">
                <div class="clearfix">
                  <div class="float-left">
                    <strong>{{ item.usage.value }}%</strong>
                  </div>
                </div>
                <CProgress
                    class="progress-xs"
                    v-model="item.usage.value"
                    :color="color(item.usage.value)"
                />
              </td>
              <td slot="activity" slot-scope="{item}">
                <div class="small text-muted">Последний отклик</div>
                <strong v-if="item.activity.format">
                  <vue-moments-ago prefix="" suffix="ago" :date="item.activity.time" lang="en"/>
                </strong>
                <strong v-else>
                  {{item.activity.time}}
                </strong>
              </td>
            </CDataTable>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </div>
</template>

<script>

import axios from "axios";
import VueMomentsAgo from 'vue-moments-ago'

export default {
  name: 'Dashboard',
  components: {
    VueMomentsAgo
  },
  data() {
    return {
      selected: 'Month',
      tableItems: [],
      tableFields: [
        {key: 'host', label: 'Hostname'},
        {key: 'country', _classes: 'text-center'},
        {key: 'usage'},
        {key: 'activity'},
      ]
    };
  },
  created() {
    this.loadServers();
    setInterval(this.loadServers, 10 * 1000);
  },
  mounted() {

  },
  methods: {
    loadServers() {
      let self = this;
      /**
       * @param response.data.servers массив игровых серверов
       * @param response.data.dedics массив виртуальных серверов
       * @param response.data.m_packages сборки мастер серверов
       */
      axios.get('http://147.135.211.1:8000/api/servers/').then(function (response) {
        self.tableItems = [];
        /**
         * @param server.status.cpu_usage использование CPU в процентах
         * @param server.status.created_at дата последнего отклика
         */
        response.data.servers.forEach(function (server) {
          let usage, activity_time, activity_format;

          if (server.status) {
            usage = server.status.cpu_usage
            activity_time = server.status.created_at + " UTC+0";
            activity_format = true;
          } else {
            activity_format = false;
            activity_time = 'Недоступен'
          }

          let package_data = response.data.m_packages.find(function (p) {
            return p.id === server.package
          });
          let package_name = "Неизвестно";
          if (package_data) {
            package_name = package_data.name;
          }

          self.tableItems.push({
            host: {
              name: server.name,
              dedic: response.data.dedics.find(function (dedic) {
                return dedic.id === server.dedic;
              }).name,
              package: package_name,
              new: false,
              registered: "ok"
            },
            country: {name: 'USA', flag: 'cib-server-fault'}, //todo: все страны
            usage: {value: usage},
            activity: {
              format: activity_format,
              time: activity_time
            }
          });
        });
      });
    },
    color(value) {
      let $color
      if (value <= 25) {
        $color = 'info'
      } else if (value > 25 && value <= 50) {
        $color = 'success'
      } else if (value > 50 && value <= 75) {
        $color = 'warning'
      } else if (value > 75 && value <= 100) {
        $color = 'danger'
      }
      return $color
    }
  }
}
</script>
