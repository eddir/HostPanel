<template>
  <CDataTable
      hover
      :items="tableItems"
      :fields="tableFields"
      head-color="light"
      itemsPerPageSelect
      pagination
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
      <template v-if="item.status || item.status==='RN'">
        <div class="clearfix">
          <div class="float-left">
            <strong>{{ item.usage.value }}%</strong>
          </div>
        </div>
      </template>
      <CBadge v-if="item.status" :color="states[item.status].badge">
        {{ states[item.status].message }}
      </CBadge>
      <CBadge v-else color="danger">Отключен</CBadge>
      <CProgress
          class="progress-xs"
          v-model="item.usage.value"
          :color="color(item.usage.value)"
      />
    </td>
    <td slot="activity" slot-scope="{item}">
      <div class="small text-muted">Последний отклик</div>
      <strong v-if="item.activity.format">
        <timeago :datetime="item.activity.time" locale="ru"></timeago>
      </strong>
      <strong v-else>Недоступен</strong>
    </td>
    <td slot="control-danger" style="width: 1%">
      <CDropdown color="secondary" toggler-text="Actions">
        <CDropdownItem disabled>Reboot</CDropdownItem>
        <CDropdownItem disabled>Delete</CDropdownItem>
      </CDropdown>
    </td>
    <td slot="control" class="text-right align-middle control-icon" style="width: 1%"
        slot-scope="{item}" @click="start(item.host.id)">
      <CIcon v-if="item.status" name="cil-media-stop" height="25" role="stop" class="mx-2"></CIcon>
      <CIcon v-else name="cil-media-play" height="25" role="start" class="mx-2"></CIcon>
    </td>
    <router-link tag="td" :to="'/servers/' + item.host.id"
                 slot="control-details" class="align-middle control-icon" style="width: 1%"
                 slot-scope="{item}" @click="window.location.href='/server/'+item.host.id">
      <CIcon name="cil-input" height="25" role="details" href="/theme/typography"></CIcon>
    </router-link>

  </CDataTable>
</template>

<script>

import ServersAPI from "../../services/Server.vue"
import Action from "../../services/Action.vue"

export default {
  name: "Servers",
  mixins: [ServersAPI],
  data() {
    return {
      tableItems: [],
      tableFields: [
        {key: 'host', label: 'Hostname'},
        //{key: 'country', _classes: 'text-center'}, //todo: вычислять страну по IP адресу
        {key: 'usage'},
        {key: 'activity'},
        {key: 'control-danger', label: '', sorter: false, filter: false},
        {key: 'control', label: '', sorter: false, filter: false},
        {key: 'control-details', label: '', sorter: false, filter: false},
      ],
      states: {
        'IN': {'code': 'IN', 'message': 'Устанавливается', 'badge': 'primary'},
        'ST': {'code': 'ST', 'message': 'Запускается', 'badge': 'info'},
        'RN': {'code': 'RN', 'message': 'Запущен', 'badge': 'success'},
        'PS': {'code': 'PS', 'message': 'Останавливается', 'badge': 'info'},
        'SP': {'code': 'SP', 'message': 'Остановлен', 'badge': 'danger'},
        'TR': {'code': 'TR', 'message': 'Удаляется', 'badge': 'warning'},
        'DL': {'code': 'DL', 'message': 'Удалён', 'badge': 'danger'},
        'RB': {'code': 'RB', 'message': 'Ребут', 'badge': 'warning'},
      }
    }
  },
  created() {
    this.loadServers();
    setInterval(this.loadServers, 10 * 1000);
  },
  methods: {
    loadServers() {
      ServersAPI.getMasters().then((servers) => this.tableItems = ServersAPI.parseMasters(servers.data));
    },
    start(id) {
      Action.serverAction('start', id);
    },
    stop(id) {
      Action.serverAction('stop', id);
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

<style scoped>

</style>