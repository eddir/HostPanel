<script>
import ServersAPI from "@/services/Server.vue"
import Vue from "vue";

export default {
  name: "Action",
  mixins: [ServersAPI],
  action(response, callback) {
    return response.then(function (response) {
      Vue.$toast.success(response.data.success);
      callback();
    }).catch(function (error) {
      let messages = error.response.data.message;
      if (typeof messages === 'string') {
        Vue.$toast.error(messages);
      } else {
        for (const [field, values] of Object.entries(messages)) {
          values.forEach(message => {
            Vue.$toast.error(field + ": " + message);
          });
        }
      }
    });
  },
  quickAction(action, server_id, callback = () => null) {
    try {
      switch (action) {
        case "start":
          this.action(ServersAPI.start(server_id), callback);
          break;
        case "stop":
          this.action(ServersAPI.stop(server_id), callback);
          break;
        case "reinstall":
          this.action(ServersAPI.reinstall(server_id), callback);
          break;
        case "remove":
          this.action(ServersAPI.remove(server_id), callback);
          break;
        case "forget":
          this.action(ServersAPI.forget(server_id), callback);
          break;
        case "dedic_reboot":
          this.action(ServersAPI.rebootDedic(server_id), callback);
          break;
        case "dedic_remove":
          this.action(ServersAPI.removeDedic(server_id), callback);
          break;
      }
    } catch (e) {
      Vue.$toast.error(e.message);
    }
  },
  formAction(action, formData, callback) {
    switch (action) {
      case "create_server":
        return this.action(ServersAPI.createServer(formData), callback);
    }
  }
}
</script>