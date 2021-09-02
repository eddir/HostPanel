<template>
  <div>
    <CCard>
      <CCardHeader>Vuetable test</CCardHeader>
      <CCardBody>
        <vuetable ref="vuetable"
                  :api-mode="false"
                  :fields="fields"
                  :data="masterSpawnerServers"
        ></vuetable>
      </CCardBody>
    </CCard>
<!--    <CCard>
      <CCardHeader>
        Master/Spawner сервера
      </CCardHeader>
      <CCardBody>
        <CDataTable
            hover
            :items="masterSpawnerServers"
            :fields="tableFields"
            head-color="light"
            itemsPerPageSelect
            pagination
            :clickableRows=true
            @row-clicked="onRowClicked"
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
          <template #usage="{item}">
            <td>
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
          </template>
          <template #activity="{item}">
            <td>
              <div class="small text-muted">Последний отклик</div>
              <strong v-if="item.activity.format">
                <timeago :datetime="item.activity.time" locale="ru"></timeago>
              </strong>
              <strong v-else>Недоступен</strong>
            </td>
          </template>
          <template #control-danger="{item}">
            <td style="width: 1%">
              <CDropdown color="secondary" toggler-text="Actions">
                <CDropdownItem @click="showRebootModal(item)">Reboot</CDropdownItem>
                <CDropdownItem @click="update(item.host.id)">Update</CDropdownItem>
                <CDropdownItem @click="showRemoveModal(item)">Delete</CDropdownItem>
              </CDropdown>
            </td>
          </template>
          <template #control="{item}">
            <td class="text-right align-middle control-icon" style="width: 1%"
                @click="item.status ? stop(item.host.id) : start(item.host.id)">
              <CIcon v-if="item.status" name="cil-media-stop" height="25" role="stop" class="mx-2"></CIcon>
              <CIcon v-else name="cil-media-play" height="25" role="start" class="mx-2"></CIcon>
            </td>
          </template>
          <template #control-details="{item}">
            <router-link tag="td" :to="'/servers/' + item.host.id" class="align-middle control-icon" style="width: 1%"
                         @click="window.location.href='/server/'+item.host.id">
              <CIcon name="cil-input" height="25" role="details" href="/theme/typography"></CIcon>
            </router-link>
          </template>

          <template #details="{item}" hidden>
            <CCollapse :show="Boolean(item._toggled)" :duration="collapseDuration">
              <CCardBody>

                <CDataTable
                    v-if="item.childs.length > 0"
                    hover
                    :items="item.childs"
                    :fields="tableFields"
                    head-color="light"
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
                  <template #usage="{item}">
                    <td>
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
                  </template>
                  <template #activity="{item}">
                    <td>
                      <div class="small text-muted">Последний отклик</div>
                      <strong v-if="item.activity.format">
                        <timeago :datetime="item.activity.time" locale="ru"></timeago>
                      </strong>
                      <strong v-else>Недоступен</strong>
                    </td>
                  </template>
                  <template #control-danger="{item}">
                    <td style="width: 1%">
                      <CDropdown color="secondary" toggler-text="Actions">
                        <CDropdownItem @click="showRebootModal(item)">Reboot</CDropdownItem>
                        <CDropdownItem @click="update(item.host.id)">Update</CDropdownItem>
                        <CDropdownItem @click="showRemoveModal(item)">Delete</CDropdownItem>
                      </CDropdown>
                    </td>
                  </template>
                  <template #control="{item}">
                    <td class="text-right align-middle control-icon" style="width: 1%" @click="start(item.host.id)">
                      <CIcon v-if="item.status" name="cil-media-stop" height="25" role="stop" class="mx-2"></CIcon>
                      <CIcon v-else name="cil-media-play" height="25" role="start" class="mx-2"></CIcon>
                    </td>
                  </template>
                  <template #control-details="{item}">
                    <router-link tag="td" :to="'/servers/' + item.host.id" class="align-middle control-icon"
                                 style="width: 1%" @click="window.location.href='/server/'+item.host.id">
                      <CIcon name="cil-input" height="25" role="details" href="/theme/typography"></CIcon>
                    </router-link>
                  </template>
                </CDataTable>
                <router-link :to="'/servers/create/' + item.host.id">
                  <CButton type="submit" size="sm" color="primary">
                    <CIcon name="cil-plus"/>
                    Создать
                  </CButton>
                </router-link>

              </CCardBody>
            </CCollapse>
          </template>
          <template slot="under-table">
            <router-link :to="'/servers/create/'">
              <CButton type="submit" size="sm" color="primary">
                <CIcon name="cil-plus"/>
                Создать
              </CButton>

            </router-link>
          </template>
        </CDataTable>
        <CModal title="Ребут сервера" color="warning" :show.sync="rebootModal" @update:show="updateRebootModal">
          Во время ребута сервера будут недоступны в течении нескольких минут.
        </CModal>
        <CModal title="Удаление сервера" color="danger" :show.sync="removeModal" @update:show="updateRemoveModal"
                v-if="selected !== null">
          Удалить сервер? Будут удалены все данные о нём, в том числе файлы на VPS.
        </CModal>


      </CCardBody>
    </CCard>

    <CCard>
      <CCardHeader>Custom сервера</CCardHeader>
      <CCardBody>
        <CDataTable
            hover
            :items="customServers"
            :fields="tableFields"
            head-color="light"
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
          <template #usage="{item}">
            <td>
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
          </template>
          <template #activity="{item}">
            <td>
              <div class="small text-muted">Последний отклик</div>
              <strong v-if="item.activity.format">
                <timeago :datetime="item.activity.time" locale="ru"></timeago>
              </strong>
              <strong v-else>Недоступен</strong>
            </td>
          </template>
          <template #control-danger="{item}">
            <td style="width: 1%">
              <CDropdown color="secondary" toggler-text="Actions">
                <CDropdownItem @click="showRebootModal(item)">Reboot</CDropdownItem>
                <CDropdownItem @click="update(item.host.id)">Update</CDropdownItem>
                <CDropdownItem @click="showRemoveModal(item)">Delete</CDropdownItem>
              </CDropdown>
            </td>
          </template>
          <template #control="{item}">
            <td class="text-right align-middle control-icon" style="width: 1%" @click="start(item.host.id)">
              <CIcon v-if="item.status" name="cil-media-stop" height="25" role="stop" class="mx-2"></CIcon>
              <CIcon v-else name="cil-media-play" height="25" role="start" class="mx-2"></CIcon>
            </td>
          </template>
          <template #control-details="{item}">
            <router-link tag="td" :to="'/servers/' + item.host.id" class="align-middle control-icon"
                         style="width: 1%" @click="window.location.href='/server/'+item.host.id">
              <CIcon name="cil-input" height="25" role="details" href="/theme/typography"></CIcon>
            </router-link>
          </template>
          <template slot="under-table">
            <router-link :to="'/servers/create/custom/'">
              <CButton type="submit" size="sm" color="primary">
                <CIcon name="cil-plus"/>
                Создать
              </CButton>

            </router-link>
          </template>
        </CDataTable>
      </CCardBody>
    </CCard>-->
  </div>
</template>

<script>
import Vuetable from 'vuetable-2/src/components/Vuetable'

import ServersAPI from "../../services/API.vue"
import Action from "../../services/Action.vue"
import fieldDefs from './ServerFieldDefs'

export default {
  name: "Servers",
  mixins: [ServersAPI],
  components: {Vuetable},
  data() {
    return {
      fields: fieldDefs,

      servers: [],
      masterSpawnerServers: [],
      customServers: [],
      tableFields: [
        {key: 'host', label: 'Хост'},
        //{key: 'country', _classes: 'text-center'}, //todo: вычислять страну по IP адресу
        {key: 'usage', label: 'Нагрузка'},
        {key: 'activity', label: 'Доступность'},
        {key: 'control-danger', label: '', sorter: false, filter: false},
        {key: 'control', label: '', sorter: false, filter: false},
        {key: 'control-details', label: '', sorter: false, filter: false},
      ],
      collapseDuration: 0,
      selected: null,
      rebootModal: false,
      removeModal: false,
      loadInterval: null,
    }
  },
  created() {
    this.loadServers();
    this.loadInterval = setInterval(this.loadServers, 10 * 1000);
  },
  destroyed() {
    clearInterval(this.loadInterval);
  },
  methods: {
    loadServers() {
      // Сохраняем предыдущие данные, чтобы знать их и предостеречь закрытия collapse.
      let oldTableItems = this.masterSpawnerServers;

      // Обращение к данным и их обработка
      ServersAPI.getServers().then(servers => {

        let servers = [];

        servers.forEach(server => {
          
        })



        this.servers = ServersAPI.parseMasters(servers.data.response);

        // Для отображения необходима построение древовидной структуры, где во главе мастер сервера, а их потомки
        // спавнеры.
        let mss = this.servers.filter(server => server.parent === null && !server.custom).map(item => {

          // Для этого нужна узнать была ли строчка расскрыта пользователем до этого
          let old = oldTableItems.find(s => s.host.id === item.host.id);

          // Если это совершенно новая строчка, то её нужно отобразить без collapse.
          item._toggled = old ? old._toggled : false;
          item.childs = this.servers.filter(server => server.parent === item.host.id);

          return item;
        });

        this.masterSpawnerServers = {data: mss};
        console.log(this.masterSpawnerServers)
        this.customServers = this.servers.filter(server => server.custom);
      });
    },
    start(id) {
      Action.quickAction('start', id);
    },
    stop(id) {
      Action.quickAction('stop', id);
    },
    update(id) {
      Action.quickAction('updateCaretaker', id);
    },
    refresh() {
      ServersAPI.refresh();
    },
    onRowClicked(item, index, column, event) {
      if (['BUTTON', 'A'].indexOf(event.target.tagName) !== -1) {
        return;
      }

      this.masterSpawnerServers[index]._toggled = !this.masterSpawnerServers[index]._toggled;
      this.collapseDuration = 300;
      this.$nextTick(() => {
        this.collapseDuration = 0;
      });
    },
    showRebootModal(server) {
      this.selected = server;
      this.rebootModal = true;
    },
    showRemoveModal(server) {
      this.selected = server;
      this.removeModal = true;
    },
    updateRebootModal(open, e, accept) {
      if (!open && accept) {
        Action.quickAction('reboot', this.selected.host.id);
      }
    },
    updateRemoveModal(open, e, accept) {
      if (!open && accept) {
        Action.quickAction('remove', this.selected.host.id);
      }
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
    },
  },
}
</script>