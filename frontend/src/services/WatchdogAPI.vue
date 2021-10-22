<script>

import axios from "axios";

export default {
  name: "WatchdogAPI",
  getLogs(ip, port) {
    return axios.get(`http://${ip}:${port}/logs/`);
  }
}
</script>