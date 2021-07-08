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
        <td slot="control-install" slot-scope="{item}" style="width: 1%">
          <CButton type="submit" color="primary" variant="outline" @click="install(item.id)">
            Установить
          </CButton>
        </td>
        <td slot="control-danger" slot-scope="{item}" style="width: 1%">
          <CDropdown color="secondary" toggler-text="Actions">
            <CDropdownItem disabled>Edit</CDropdownItem>
            <CDropdownItem @click="remove(item.id)">Delete</CDropdownItem>
          </CDropdown>
        </td>
      </CDataTable>
    </CCardBody>
  </CCard>
</template>

<script>
import ServersAPI from "../../services/Server.vue"
import Action from "@/services/Action";

export default {
  name: "Packages",
  mixins: [ServersAPI],
  data() {
    return {
      type: "",
      packages: [],
      tableItems: [],
      tableFields: [],
    }
  },
  created() {
    this.type = this.$route.params.type;

    this.tableFields = [
      {key: 'name', label: 'Name'},
      {key: 'created_at'},
    ];

    if (this.type === "master") {
      this.tableFields.push({
        key: 'master_size'
      });
    } else {
      this.tableFields.push(...[
        {key: 'spawner_size'},
        {key: 'room_size'},
      ]);
    }

    this.tableFields.push(...[
      {key: 'control-install', label: '', sorter: false, filter: false},
      {key: 'control-danger', label: '', sorter: false, filter: false},
    ]);

    this.load();
  },
  methods: {
    load() {
      this.tableItems = [];
      let response = this.type === "master" ? ServersAPI.getMasterPackages() : ServersAPI.getSpawnerPackages();
      response.then(packages => {
        this.packages = packages.data.packages;
        this.tableItems = packages.data.packages;
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
      if (this.type === "master") {
        Action.quickAction('remove_master_package', package_id, () => {
          this.load();
        });
      } else {
        Action.quickAction('remove_spawner_package', package_id, () => {
          this.load();
        });
      }
    }
  }
}
</script>

<style scoped>

</style>