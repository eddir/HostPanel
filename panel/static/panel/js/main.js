axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";

let watchVM = new Vue({
    el: '#wrapper',
    delimiters: ['${', '}'],
    data: {
        message: "",
        error: "",
        servers: {},
        server: {},
        m_packages: {},
        sr_packages: {},
        loaded: false,
        form: {
            name: "Server " + Math.floor(Math.random() * 1000),
            ip: "213.139.209.176",
            user_root: "root",
            password_root: "Ihor&Eddir1234",
            user_single: "msf",
            ssh_key: false,
            m_package: null,
            sr_package: null,
            config: "",
        }
    },
    mounted: function () {
        let path = location.pathname.split("/")

        if (path[1] === "") {
            this.$nextTick(this.getServers);
        } else if (path[1] === "server" && path.length === 4) {
            this.$nextTick(this.getServer);
        }
    },
    methods: {
        changePackage: function (isMaster) {
            if (isMaster) {
                this.form['sr_package'] = null
                this.form['config'] = "-mstStartMaster=true\n" +
                    "-mstStartClientConnection=true\n" +
                    "-mstMasterIp=127.0.0.1\n" +
                    "-mstMasterPort=5000"
            } else {
                this.form['m_package'] = null
                this.form['config'] = "-mstStartSpawner=true\n" +
                    "-mstStartClientConnection=true\n" +
                    "-mstMasterIp=213.139.209.176\n" +
                    "-mstMasterPort=5000\n" +
                    "-mstRoomIp=213.139.209.176\n" +
                    "-mstMaxProcesses=1\n" +
                    "-mstRoomExe=~\\Pack\\Room\\Room.x86_64"
            }
        },
        startServer: function () {
            axios.put('/api/server/'+location.pathname.split("/").slice(-2)[0]+'/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер запущен");
                    watchVM.getServer();
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data);
                })
        },
        stopServer: function () {
            axios.delete('/api/server/'+location.pathname.split("/").slice(-2)[0]+'/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер остановлен");
                    watchVM.getServer();
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data);
                })
        },
        createServer: function () {
            axios.post('/api/servers/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер добавлен");
                    watchVM.getServers();
                })
                .catch(function (error) {
                    watchVM.alertFailure(Object.entries(error.data).map(entry => entry[1]).join("\n"));
                })
        },
        updateConfig: function () {
            axios.post('/api/server/' + this.server.server.id + "/config", {"config": this.server.server.config})
                .then(function (response) {
                    watchVM.alertSuccess("Конфиг обновлён");
                })
                .catch(function (error) {
                    watchVM.alertFailure(Object.entries(error.data).map(entry => entry[1]).join("\n"));
                })
        },
        getServer: function () {
            axios.get('/api/server/'+location.pathname.split("/").slice(-2)[0]+'/')
                .then(function (response) {
                    watchVM.loaded = true;
                    watchVM.server = response.data;
                })
                .catch(function (error) {
                    watchVM.loaded = true;
                    watchVM.alertFailure(error)
                })
        },
        getServers: function () {
            axios.get('/api/servers/')
                .then(function (response) {
                    watchVM.servers = response.data.servers;
                    watchVM.m_packages = response.data.m_packages;
                    watchVM.sr_packages = response.data.sr_packages;
                })
                .catch(function (error) {
                    watchVM.alertFailure(error)
                })
        },
        alertSuccess: function (message) {
            this.message = message;
            let toasts = $('#alert-success');
            toasts.toast({delay: 5000});
            toasts.toast('show');
        },
        alertFailure: function (message) {
            this.error = message;
            let toasts = $('#alert-fail');
            toasts.toast({delay: 5000});
            toasts.toast('show');
        },
        notImplemented: function () {
            this.alertFailure("Фича не реализована")
        }
    }
})