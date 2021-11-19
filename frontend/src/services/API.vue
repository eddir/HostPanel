<script>
import Vue from "vue";
import axios from 'axios';
import './AuthInterceptor';

let debugMode = window.location.href.indexOf("localhost") >= 0;

const SERVER_URL = debugMode ? "https://p.rostkov.pro:8443/" : "https://hp.linksss.ru/";
const REST_URL = `${SERVER_URL}api/`;

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
    return axios.get(`${REST_URL}package/master/`);
  },
  getSpawnerPackages() {
    return axios.get(`${REST_URL}package/spawner/`);
  },
  getCustomPackages() {
    return axios.get(`${REST_URL}package/custom/`);
  },
  installMasterPackage(package_id) {
    return axios.post(`${REST_URL}package/master/${package_id}/install/`);
  },
  installSpawnerPackage(package_id) {
    return axios.post(`${REST_URL}package/spawner/${package_id}/install/`);
  },
  installCustomPackage(package_id) {
    return axios.post(`${REST_URL}package/custom/${package_id}/install/`);
  },
  removeMasterPackage(package_id) {
    return axios.delete(`${REST_URL}package/master/${package_id}/`);
  },
  removeSpawnerPackage(package_id) {
    return axios.delete(`${REST_URL}package/spawner/${package_id}/`);
  },
  removeCustomPackage(package_id) {
    return axios.delete(`${REST_URL}package/custom/${package_id}/`);
  },
  uploadMasterPackage(name, master, bin_path, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("master", master);
    formData.append("bin_path", bin_path);

    return this.uploadFiles(`${REST_URL}package/master/`, formData, progressCallback);
  },
  uploadSpawnerPackage(name, spawner, room, bin_path, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("spawner", spawner);
    formData.append("room", room);
    formData.append("bin_path", bin_path);

    return this.uploadFiles(`${REST_URL}package/spawner/`, formData, progressCallback);
  },
  uploadCustomPackage(name, archive, bin_path, progressCallback) {
    let formData = new FormData();

    formData.append("name", name);
    formData.append("archive", archive);
    formData.append("bin_path", bin_path);

    return this.uploadFiles(`${REST_URL}package/custom/`, formData, progressCallback);
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
  getSubs() {
    return axios.get(`${REST_URL}subscribers/`);
  },
  addSub(sub_data) {
    return axios.post(`${REST_URL}subscribers/`, sub_data);
  },
  removeSub(sub) {
    return axios.delete(`${REST_URL}subscribers/${sub['id']}/`);
  }
}
</script>