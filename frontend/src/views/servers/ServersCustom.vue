<template>
  <CCard>
    <CCardHeader>Custom сервера</CCardHeader>
    <CCardBody>
      <CDataTable
          hover
          :items="servers"
          :fields="tableFields"
          head-color="light"
          pagination
      >
        <tr slot="select-header">
          <input type="checkbox" :value="true" @click="select($event, true)" ref="customCheckbox">
        </tr>
        <td slot="select" slot-scope="{item}">
          <input type="checkbox" v-model="selected" :value="item" @click="select($event, false)">
        </td>
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
          <CBadge v-if="item.status" :color="item.status.badge">
            {{ item.status.message }}
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
        <router-link slot="control-details" slot-scope="{item}"
                     tag="td" :to="'/servers/' + item.host.id" class="align-middle control-icon"
                     style="width: 1%" @click="window.location.href='/server/'+item.host.id">
          <CButton variant="outline" color="primary" size="sm">Перейти</CButton>
        </router-link>
        <template slot="under-table">

          <router-link :to="'/servers/create/custom/'">
            <CButton type="submit" size="sm" color="primary">
              <CIcon name="cil-plus"/>
              Создать
            </CButton>
          </router-link>

          <div class="float-right">
            <ServersActions :selected="selected"></ServersActions>
          </div>

        </template>
      </CDataTable>
    </CCardBody>
  </CCard>
</template>

<script>
import Utils from "@/services/Utils";
import ServersActions from "@/views/servers/ServersActions";

export default {
  name: "ServersCustom",
  components: {ServersActions},
  mixins: [Utils],
  props: {
    servers: {
      require: true,
      type: Array,
    },
  },
  data() {
    return {
      tableFields: [
        {key: 'host', label: 'Хост'},
        //{key: 'country', _classes: 'text-center'}, //todo: вычислять страну по IP адресу
        {key: 'usage', label: 'Нагрузка'},
        {key: 'activity', label: 'Доступность'},
        {key: 'control-details', label: '', sorter: false, filter: false},
        {key: 'select'},
      ],
      selected: [],
    }
  },
  methods: {
    select(ev, all, parent = null) {

      let cur;
      ev.target.checked ? cur = 1 : cur = -1;

      let checkbox = this.$refs.customCheckbox;

      if (parent === null) {
        if (all) {

          //Отмечаем все сервера
          checkbox.checked ? this.selected = this.servers : this.selected = [];

          this.servers.forEach(server => {
            let index = this.selected.indexOf(server);
            if (checkbox.checked) {
              if (index === -1) {
                this.selected.push(server);
              }
            } else {
              if (server.parent === null) {
                this.selected.splice(index, 1);
              }
            }
          });

        } else if (checkbox.checked && this.selected.length + cur !== this.servers.length) {
          //пользователь снял выделение с одной позиции, когда было выделено всё
          checkbox.checked = false;

        } else if (!checkbox.checked && this.selected.length + cur === this.servers.length) {
          //пользователь сам всё выделил по одному
          checkbox.checked = true;
        }
      }

      this.$emit("user-interact");
    },
  },
}
</script>

<style scoped>

</style>