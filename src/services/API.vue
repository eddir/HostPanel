<script>
import Vue from "vue";
import axios from 'axios';

let debugMode = window.location.href.indexOf("localhost") >= 0;

const SERVER_URL = debugMode ? "https://p.rostkov.pro:8443/" : "https://hp.linksss.ru:8443/";
const REST_URL = `${SERVER_URL}api/`;

axios.defaults.withCredentials = true;
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";

let tokenRefreshing = false;

axios.interceptors.response.use(response => {
  return response;
}, error => {

  if (error.response.status === 401 && !tokenRefreshing) {

    tokenRefreshing = true;

    axios.post(`${SERVER_URL}auth/token/refresh/`).then(() => {
      tokenRefreshing = false;

      const config = error.config;
      return new Promise((resolve, reject) => {
        axios.request(config).then(response => {
          resolve(response);
        }).catch((error) => {
          reject(error);
        })
      });
    }).catch(e => {
      if (e.response.status === 401) {
        tokenRefreshing = false;
        window.location = "/#/login";
        Vue.$toast.warning("Срок действия сессии истёк.");
      } else {
        Promise.reject(error);
      }
    });
  }

  return Promise.reject(error);
});

export default {
  name: "ServersAPI",
  AUTH_TELEGRAM_BOT: debugMode ? "RostkovBot" : "HostPanelRobot",
  SERVER_URL,
  REST_URL,
  getServers() {
    return this.get(`${REST_URL}servers/`);
  },
  getDedics() {
    return this.get(`${REST_URL}dedics/`);
  },
  getServer(server_id) {
    return this.get(`${REST_URL}server/${server_id}/`);
  },
  start(server_id) {
    return this.post(`${REST_URL}server/${server_id}/start/`, {action: "start"});
  },
  stop(server_id) {
    return this.post(`${REST_URL}server/${server_id}/stop/`, {action: "stop"});
  },
  remove(server_id) {
    return this.post(`${REST_URL}server/${server_id}/remove/`);
  },
  forget(server_id) {
    return this.post(`${REST_URL}server/${server_id}/remove/force/`);
  },
  reinstall(server_id) {
    return this.post(`${REST_URL}server/${server_id}/`);
  },
  update(server_id, package_id) {
    return this.post(`${REST_URL}server/${server_id}/`, {package: package_id});
  },
  updateConfig(server_id, config) {
    return this.post(`${REST_URL}server/${server_id}/config/`, {config: config});
  },
  updateCaretaker(server_id) {
    return this.post(`${REST_URL}server/${server_id}/updateCaretaker/`);
  },
  createServer(server) {
    return this.post(`${REST_URL}servers/`, server);
  },
  createDedic(dedic) {
    return this.post(`${REST_URL}dedics/`, dedic);
  },
  reboot(dedic_id) {
    return this.post(`${REST_URL}server/${dedic_id}/reboot/`);
  },
  removeDedic(dedic_id) {
    return this.delete(`${REST_URL}dedic/${dedic_id}/`);
  },
  reconnectDedic(dedic_id) {
    return this.post(`${REST_URL}dedic/${dedic_id}/reconnect/`);
  },
  getTasks() {
    return this.get(`${REST_URL}task/`);
  },
  cancelTasks() {
    return this.delete(`${REST_URL}task/`);
  },
  getMasterPackages() {
    return this.get(`${REST_URL}m_package/`);
  },
  getSpawnerPackages() {
    return this.get(`${REST_URL}sr_package/`);
  },
  installMasterPackage(package_id) {
    return this.post(`${REST_URL}m_package/${package_id}/install/`);
  },
  installSpawnerPackage(package_id) {
    return this.post(`${REST_URL}sr_package/${package_id}/install/`);
  },
  removeMasterPackage(package_id) {
    return this.delete(`${REST_URL}m_package/${package_id}/`);
  },
  removeSpawnerPackage(package_id) {
    return this.delete(`${REST_URL}sr_package/${package_id}/`);
  },
  uploadMasterPackage(name, master, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("master", master);

    return this.uploadFiles(`${REST_URL}m_package/`, formData, progressCallback);
  },
  uploadSpawnerPackage(name, spawner, room, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("spawner", spawner);
    formData.append("room", room);

    return this.uploadFiles(`${REST_URL}sr_package/`, formData, progressCallback);
  },
  getVersion() {
    return this.get(`${REST_URL}version/`);
  },
  getUsers() {
    return this.get(`${REST_URL}users/`);
  },
  uploadFiles(url, formData, progressCallback) {
    return this.post(url, formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: progressCallback,
        },
    );
  },
  withAuth(error) {
    //todo: remove
  },
  login(user) {
    axios.post(`${SERVER_URL}auth/telegram/login/`, user).then().catch(err => {
      Vue.$toast.error(err.response);
    })
  },
  refresh() {//todo: remove
    return axios.post(`${SERVER_URL}auth/token/refresh/`).catch(() => {
      window.location = "/#/login";
      Vue.$toast.warning("Срок действия сессии истёк.");
    });
  },
  parseStatus(status) {
    return {
      'IN': {'code': 'IN', 'message': 'Устанавливается', 'badge': 'primary'},
      'ST': {'code': 'ST', 'message': 'Запускается', 'badge': 'info'},
      'RN': {'code': 'RN', 'message': 'Запущен', 'badge': 'success'},
      'PS': {'code': 'PS', 'message': 'Останавливается', 'badge': 'info'},
      'SP': {'code': 'SP', 'message': 'Остановлен', 'badge': 'danger'},
      'TR': {'code': 'TR', 'message': 'Удаляется', 'badge': 'warning'},
      'DL': {'code': 'DL', 'message': 'Удалён', 'badge': 'danger'},
      'RB': {'code': 'RB', 'message': 'Ребут', 'badge': 'warning'},
    }[status];
  },//todo: парсеры перенести в другой файл
  parseLog(log) {
    let codes = {
      "&0": "#607d8b",
      "&1": "#3f51b5",
      "&2": "#5cd760",
      "&3": "#00bcd4",
      "&4": "#f44336",
      "&5": "#9c27b0",
      "&6": "#ffc107",
      "&7": "#9e9e9e",
      "&8": "#757575",
      "&9": "#2196F3",
      "&a": "#03a9f4",
      "&b": "#E91E63",
      "&c": "#673ab7",
      "&d": "#ff903b",
      "&e": "#ffeb3b",
      "&f": "#fff",
    }

    log = log.split("<br>");
    for (let i = 0; i < log.length; i++) {
      for (const key in codes) {
        let pos = log[i].indexOf(key);
        if (pos !== -1) {
          log[i] = log[i].slice(0, pos) + "<span style='color: " + codes[key] + "'>" +
              log[i].slice(pos + 2) + "</span>";
        }
      }
    }
    return log.join('<br>');
  },
  parseMasters(data) {
    let servers = [];
    /**
     * @param response.data.servers массив игровых серверов
     * @param response.data.dedics массив виртуальных серверов
     * @param response.data.m_packages сборки мастер серверов
     * @param response.data.sr_packages сборки спавнер серверов
     */
    data.servers.forEach(server => {
      let usage, state, activity_time, activity_format;
      /**
       * @param server.status.cpu_usage использование CPU в процентах
       * @param server.status.created_at дата последнего отклика
       */
      if (server.status) {
        state = this.parseStatus(server.status.condition);
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
          registered: "ok",
        },
        country: {name: 'USA', flag: 'cib-server-fault'}, //todo: все страны
        usage: {value: usage},
        status: state,
        parent: server.parent,
        activity: {
          format: activity_format,
          time: activity_time,
        },
      });

    });

    return servers;
  },
  get(url) {
    return axios.get(url).catch(this.withAuth);
  },
  head(url) {
    return axios.head(url).catch(this.withAuth);
  },
  options(url) {
    return axios.options(url).catch(this.withAuth);
  },
  post(url, data) {
    return axios.post(url, data).catch(this.withAuth);
  },
  put(url, data) {
    return axios.put(url, data).catch(this.withAuth);
  },
  delete(url) {
    return axios.delete(url).catch(this.withAuth);
  },
  patch(url, data) {
    return axios.patch(url, data).catch(this.withAuth);
  },
}
</script>