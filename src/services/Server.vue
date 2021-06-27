<script>
import axios from 'axios'

const REST_URL = "http://147.135.211.1:8000/api/";

//todo: рассмотреть готовые фреймворки вместо этого
export default {
  name: "ServersAPI",
  getMasters() {
    return axios.get(`${REST_URL}servers/`);
  },
  start(server_id) {
    return axios.put(`${REST_URL}server/${server_id}/`);
  },
  stop(server_id) {
    return axios.delete(`${REST_URL}server/${server_id}/`);
  },
  parseMasters(data) {
    let servers = [];
    /**
     * @param response.data.servers массив игровых серверов
     * @param response.data.dedics массив виртуальных серверов
     * @param response.data.m_packages сборки мастер серверов
     */
    data.servers.forEach(function (server) {
      let usage, state, activity_time, activity_format;
      /**
       * @param server.status.cpu_usage использование CPU в процентах
       * @param server.status.created_at дата последнего отклика
       */
      if (server.status) {
        state = server.status.condition;
        usage = server.status.cpu_usage | 0;
        activity_time = server.status.created_at + "+00:00";
        activity_format = true;
      } else {
        activity_format = false;
      }

      let package_data = data.m_packages.find(function (p) {
        return p.id === server.package
      });
      let package_name = "Неизвестно";
      if (package_data) {
        package_name = package_data.name;
      }

      servers.push({
        host: {
          id: server.id,
          name: server.name,
          dedic: data.dedics.find(function (dedic) {
            return dedic.id === server.dedic;
          }).name,
          package: package_name,
          new: false,
          registered: "ok"
        },
        country: {name: 'USA', flag: 'cib-server-fault'}, //todo: все страны
        usage: {value: usage},
        status: state,
        activity: {
          format: activity_format,
          time: activity_time
        }
      });

    });

    return servers;
  }
}
</script>