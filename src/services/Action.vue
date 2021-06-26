<script>
import ServersAPI from "@/services/Server.vue"
import Vue from "vue";

export default {
  name: "Action",
  mixins: [ServersAPI],
  action(response) {
    response.then(function (response) {
      Vue.$toast.success(response.data.success);
    }).catch(function (error) {
      Vue.$toast.error(error.response.data.message);
    });
  },
  serverAction(action, server_id) {
    switch (action) {
      case "start":
        this.action(ServersAPI.start(server_id));
        break;
      case "stop":
        this.action(ServersAPI.stop(server_id));
        break;
    }
    return true;
  }
}
</script>