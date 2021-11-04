<script>
import Vue from "vue";
import axios from 'axios';

let debugMode = window.location.href.indexOf("localhost") >= 0;

const SERVER_URL = debugMode ? "https://p.rostkov.pro:8443/" : "https://hp.linksss.ru/";
const REST_URL = `${SERVER_URL}api/`;

axios.defaults.withCredentials = true;
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";

let tokenRefreshing = false;

axios.interceptors.response.use(response => {
  if (response.data.code === 0) {
    return response;
  } else if (response.data.code === 100 && !tokenRefreshing) {
    tokenRefreshing = true;

    axios.post(`${SERVER_URL}auth/token/refresh/`).then(() => {
      tokenRefreshing = false;

      const config = response.config;
      return new Promise((resolve, reject) => {
        axios.request(config).then(response => {
          resolve(response);
        }).catch((error) => {
          reject(error);
        })
      });
    }).catch(e => {
      if (e.response.data.response === 100) {
        tokenRefreshing = false;
        window.location = "/#/login";
        Vue.$toast.warning("Срок действия сессии истёк.");
      } else {
        Promise.reject(response);
      }
    });

  } else {
    return handleErrors(response)
  }
}, error => {

  if (error.response) {
    return handleErrors(error.response);
  }

  return Promise.reject(error);
});

function handleErrors(response) {
  if (response.data.code === 2) {
    Vue.$toast.error("Ошибка авторизации #2.");
    window.location = "/#/login";
  } else {
    if (response.data.response) {
      response.data.response.forEach(m => Vue.$toast.warning(m));
    } else {
      Vue.$toast.warning("Не удалось выполнить запрос. Подробнее в консоли.");
    }
    console.log(response.data);
  }
  return null;
}

export default {
  name: "ServersAPI",
  AUTH_TELEGRAM_BOT: debugMode ? "RostkovBot" : "HostPanelRobot",
  SERVER_URL,
  REST_URL,
  getServers() {
    return axios.get(`${REST_URL}servers/`);
  },
  getDedics() {
    return axios.get(`${REST_URL}dedics/`);
  },
  getServer(server_id) {
    return axios.get(`${REST_URL}server/${server_id}/`);
  },
  start(server_id) {
    return axios.post(`${REST_URL}server/${server_id}/start/`, {action: "start"});
  },
  stop(server_id) {
    return axios.post(`${REST_URL}server/${server_id}/stop/`, {action: "stop"});
  },
  remove(server_id) {
    return axios.post(`${REST_URL}server/${server_id}/remove/`);
  },
  forget(server_id) {
    return axios.post(`${REST_URL}server/${server_id}/remove/force/`);
  },
  reinstall(server_id) {
    return axios.post(`${REST_URL}server/${server_id}/`);
  },
  update(server_id, package_id) {
    return axios.post(`${REST_URL}server/${server_id}/`, {package: package_id});
  },
  updateConfig(server_id, config) {
    return axios.post(`${REST_URL}server/${server_id}/config/`, {config: config});
  },
  updateCaretaker(server_id) {
    return axios.post(`${REST_URL}server/${server_id}/updateCaretaker/`);
  },
  setStatus(server_id, condition) {
    return axios.post(`${REST_URL}server/${server_id}/setStatus/`, {condition: condition});
  },
  createServer(server) {
    return axios.post(`${REST_URL}servers/`, server);
  },
  createDedic(dedic) {
    return axios.post(`${REST_URL}dedics/`, dedic);
  },
  reboot(dedic_id) {
    return axios.post(`${REST_URL}server/${dedic_id}/reboot/`);
  },
  removeDedic(dedic_id) {
    return axios.delete(`${REST_URL}dedic/${dedic_id}/`);
  },
  reconnectDedic(dedic_id) {
    return axios.post(`${REST_URL}dedic/${dedic_id}/reconnect/`);
  },
  getTasks() {
    return axios.get(`${REST_URL}task/`);
  },
  cancelTasks() {
    return axios.delete(`${REST_URL}task/`);
  },
  getMasterPackages() {
    return axios.get(`${REST_URL}m_package/`);
  },
  getSpawnerPackages() {
    return axios.get(`${REST_URL}sr_package/`);
  },
  getCustomPackages() {
    return axios.get(`${REST_URL}c_package/`);
  },
  installMasterPackage(package_id) {
    return axios.post(`${REST_URL}m_package/${package_id}/install/`);
  },
  installSpawnerPackage(package_id) {
    return axios.post(`${REST_URL}sr_package/${package_id}/install/`);
  },
  installCustomPackage(package_id) {
    return axios.post(`${REST_URL}c_package/${package_id}/install/`);
  },
  removeMasterPackage(package_id) {
    return axios.delete(`${REST_URL}m_package/${package_id}/`);
  },
  removeSpawnerPackage(package_id) {
    return axios.delete(`${REST_URL}sr_package/${package_id}/`);
  },
  removeCustomPackage(package_id) {
    return axios.delete(`${REST_URL}c_package/${package_id}/`);
  },
  uploadMasterPackage(name, master, bin_path, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("master", master);
    formData.append("bin_path", bin_path);

    return this.uploadFiles(`${REST_URL}m_package/`, formData, progressCallback);
  },
  uploadSpawnerPackage(name, spawner, room, bin_path, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("spawner", spawner);
    formData.append("room", room);
    formData.append("bin_path", bin_path);

    return this.uploadFiles(`${REST_URL}sr_package/`, formData, progressCallback);
  },
  uploadCustomPackage(name, archive, bin_path, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("archive", archive);
    formData.append("bin_path", bin_path);

    return this.uploadFiles(`${REST_URL}c_package/`, formData, progressCallback);
  },
  getVersion() {
    return axios.get(`${REST_URL}version/`);
  },
  getUsers() {
    return axios.get(`${REST_URL}users/`);
  },
  uploadFiles(url, formData, progressCallback) {
    return axios.post(url, formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: progressCallback,
        },
    );
  },
  login(user) {
    axios.post(`${SERVER_URL}auth/telegram/login/`, user).then().catch(err => {
      Vue.$toast.error(err.response);
    })
  },
  getLogs(server_id) {
    return axios.get(`${REST_URL}watchdog/logs/${server_id}/`);
  },
  downloadLog(server_id, log_file, size, part) {
    window.open(`${REST_URL}watchdog/logs/${server_id}/download/${log_file}?size=${size}&number=${part}`);
  },
  removeLog(server_id, log_file) {
    return axios.post(`${REST_URL}watchdog/logs/${server_id}/remove/${log_file}/`);
  },
  ping() {
    return axios.get(`${REST_URL}ping/`);
  },
}
</script>