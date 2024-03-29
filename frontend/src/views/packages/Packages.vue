<template>
  <CCard>
    <CCardHeader>Сборки {{ type }}</CCardHeader>
    <CCardBody>
      <CDataTable
          hover
          :items="tableItems"
          :fields="tableFields"
          head-color="light"
          itemsPerPageSelect
          pagination
      >
        <td slot="control-install" slot-scope="{item}" class="buttons-group">
          <InstallPackage :pack="item" :type="type" :servers="servers"></InstallPackage>
        </td>
        <td slot="control-danger" slot-scope="{item}" class="buttons-group">
          <CDropdown color="secondary" toggler-text="Actions">
            <CDropdownItem disabled>Edit</CDropdownItem>
            <CDropdownItem @click="showRemoveModal(item)">Delete</CDropdownItem>
          </CDropdown>
        </td>
        <template slot="under-table">
          <router-link :to="'/packages/' + type + '/create/'">
            <CButton class="mb-2" type="submit" size="sm" color="primary">
              <CIcon name="cil-plus"/>
              Создать
            </CButton>
          </router-link>
        </template>
      </CDataTable>
    </CCardBody>
    <CModal title="Удаление сервера" color="danger" :show.sync="removeModal" @update:show="updateRemoveModal"
            v-if="selected">
      Удалить сборку {{ selected.name }}? Архив будет удалён безвозвратно.
    </CModal>
  </CCard>
</template>

<script>
import ServersAPI from "../../services/API.vue"
import Action from "@/services/Action";
import InstallPackage from "@/views/packages/InstallPackage";

export default {
  name: "Packages",
  mixins: [ServersAPI],
  components: {InstallPackage},
  data() {
    return {
      type: "",
      packages: [],
      tableItems: [],
      tableFields: [],
      removeModal: false,
      selected: null,
      servers: [],
    }
  },
  created() {
    this.type = this.$route.params.type;

    this.tableFields = [
      {key: 'name', label: 'Name'},
      {key: 'created_at'},
    ];

    switch (this.type) {
      case "master":
        this.tableFields.push({
          key: 'master_size',
        });
        break;
      case "spawner":
        this.tableFields.push(...[
          {key: 'spawner_size'},
          {key: 'room_size'},
        ]);
        break;
      case "custom":
        this.tableFields.push({
          key: 'archive_size',
        });
        break;
      default:
        throw new Error("Неизвестный тип сборок - " + this.type);
    }

    this.tableFields.push(...[
      {key: 'control-install', label: '', sorter: false, filter: false},
      {key: 'control-danger', label: '', sorter: false, filter: false},
    ]);

    ServersAPI.getServers().then(response => {
      this.servers = response.data.response.servers.filter(server => {
        if (this.type === "custom") return server.custom;
        return (server.parent === null) === (this.type === "master")
      });
    });

    this.load();
  },
  methods: {
    load() {
      this.tableItems = [];
      let response;
      switch (this.type) {
        case "master":
          response = ServersAPI.getMasterPackages();
          break;
        case "spawner":
          response = ServersAPI.getSpawnerPackages();
          break;
        case "custom":
          response = ServersAPI.getCustomPackages();
          break;
      }
      response.then(packages => {
        this.packages = packages.data.response;
        this.tableItems = packages.data.response;
      });
    },
    install(package_id) {
      if (this.type === "master") {
        Action.quickAction('install_master_package', package_id);
      } else {
        Action.quickAction('install_spawner_package', package_id);
      }
    },
    remove(package_id) {
      Action.quickAction('remove_' + this.type + '_package', package_id, () => {
        this.load();
      });
    },
    showRemoveModal(pack) {
      this.selected = pack;
      this.removeModal = true;
    },
    updateRemoveModal(open, e, accept) {
      if (!open && accept) {
        this.remove(this.selected.id);
      }
    },
  },
}
</script>

<style scoped>
.buttons-group {
  width: 1%;
  white-space: nowrap;
}
</style>