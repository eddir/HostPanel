<script>
import ServersAPI from "@/services/API.vue"
import Vue from "vue";

export default {
  name: "Action",
  mixins: [ServersAPI],
  /**
   * Действие не требующее особой обработки. Выполняется по общему алгоритму.
   * @param response http запрос
   * @param callback действие после выполнения
   * @returns {*}
   */
  action(response, callback) {
    return response
        .then(function (response) {
          Vue.$toast.success(response.data.response);
          try {
            callback();
          } catch (e) {
            Vue.$toast.error(e);
          }
        })
        .catch(function (error) {
          if (error.response.status === 500) {
            let messages = error.response.data.response;
            if (typeof messages === 'string') {
              Vue.$toast.error(messages);
            } else {
              for (const [field, values] of Object.entries(messages)) {
                if (typeof values === 'string') {
                  Vue.$toast.error(values);
                } else {
                  values.forEach(message => {
                    Vue.$toast.error(field + ": " + message);
                  });
                }
              }
            }

          }
        });
  },
  quickAction(action, unit_id, callback = () => null) {
    try {
      switch (action) {
        case "start":
          this.action(ServersAPI.start(unit_id), callback);
          break;
        case "stop":
          this.action(ServersAPI.stop(unit_id), callback);
          break;
        case "reinstall":
          this.action(ServersAPI.reinstall(unit_id), callback);
          break;
        case "remove":
          this.action(ServersAPI.remove(unit_id), callback);
          break;
        case "forget":
          this.action(ServersAPI.forget(unit_id), callback);
          break;
        case "reboot":
          this.action(ServersAPI.reboot(unit_id), callback);
          break;
        case "updateCaretaker":
          this.action(ServersAPI.updateCaretaker(unit_id), callback);
          break;
        case "dedic_remove":
          this.action(ServersAPI.removeDedic(unit_id), callback);
          break;
        case "dedic_reconnect":
          this.action(ServersAPI.reconnectDedic(unit_id), callback);
          break;
        case "install_master_package":
          this.action(ServersAPI.installMasterPackage(unit_id), callback);
          break;
        case "install_spawner_package":
          this.action(ServersAPI.installSpawnerPackage(unit_id), callback);
          break;
        case "remove_master_package":
          this.action(ServersAPI.removeMasterPackage(unit_id), callback);
          break;
        case "remove_spawner_package":
          this.action(ServersAPI.removeSpawnerPackage(unit_id), callback);
          break;
        case "version":
          this.action(ServersAPI.getVersion(), callback);
          break;
        case "cancelTasks":
          this.action(ServersAPI.cancelTasks(), callback);
          break;
      }
    } catch (e) {
      Vue.$toast.error(e.message);
    }
  },
  serverAction(action, server_id, formData, callback = () => null) {
    switch (action) {
      case "update_config":
        return this.action(ServersAPI.updateConfig(server_id, formData), callback);
      case "update":
        return this.action(ServersAPI.update(server_id, formData['package']), callback);
        case "set_status":
          return this.action(ServersAPI.setStatus(server_id, formData['condition']), callback);
    }
  },
  formAction(action, formData, callback) {
    switch (action) {
      case "create_server":
        return this.action(ServersAPI.createServer(formData), callback);
      case "create_dedic":
        return this.action(ServersAPI.createDedic(formData), callback);
    }
  },
  fileAction(action, formData, progressCallback, successCallback) {
    switch (action) {
      case "upload_master_package":
        return this.action(ServersAPI.uploadMasterPackage(
            formData.name, formData.master, progressCallback,
        ), successCallback);
      case "upload_spawner_package":
        return this.action(ServersAPI.uploadSpawnerPackage(
            formData.name, formData.spawner, formData.room, progressCallback,
        ), successCallback);
    }
  },
}
</script>