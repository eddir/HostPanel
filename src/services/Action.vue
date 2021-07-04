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
  quickAction(action, server_id) {
    switch (action) {
      case "start":
        this.action(ServersAPI.start(server_id));
        break;
      case "stop":
        this.action(ServersAPI.stop(server_id));
        break;
      case "reinstall":
        this.action(ServersAPI.reinstall(server_id));
        break;
      case "remove":
        this.action(ServersAPI.remove(server_id));
        break;
      case "forget":
        this.action(ServersAPI.forget(server_id));
        break;
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