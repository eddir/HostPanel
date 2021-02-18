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
            parent: null,
            name: "Server " + Math.floor(Math.random() * 1000),
            ip: "213.139.209.176",
            user_root: "root",
            password_root: "Ihor&Eddir1234",
            user_single: "msf",
            ssh_key: false,
            package: null,
            type: "master",
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
        prepareCreateForm: function (server) {
            this.server = server;
            let spawner = $('#create_spawner');
            spawner.collapse('toggle');
            spawner.on('shown.bs.collapse', function () {
                this.scrollIntoView();
            });
        },
        prepareCreateMasterForm: function (server) {
            let master = $('#create_master');
            master.collapse('toggle');
            master.on('shown.bs.collapse', function () {
                this.scrollIntoView();
            });
        },
        changePackage: function (isMaster) {
            if (isMaster) {
                this.form['config'] = "-mstStartMaster=true\n" +
                    "-mstStartClientConnection=true\n" +
                    "-mstMasterIp=127.0.0.1\n" +
                    "-mstMasterPort=5000"
            } else {
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
            axios.put('/api/server/' + location.pathname.split("/").slice(-2)[0] + '/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер запущен");
                    watchVM.getServer();
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data.message);
                })
        },
        stopServer: function () {
            axios.delete('/api/server/' + location.pathname.split("/").slice(-2)[0] + '/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер остановлен");
                    watchVM.getServer();
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data.message);
                })
        },
        createServer: function (type) {
            if (type === "spawner") {
                this.form.parent = this.server.id;
            }
            axios.post('/api/servers/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер добавлен");
                    watchVM.getServers();
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data.message);
                })
        },
        updateConfig: function () {
            axios.post('/api/server/' + this.server.server.id + "/config", {"config": this.server.server.config})
                .then(function (response) {
                    watchVM.alertSuccess("Конфиг обновлён");
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data.message);
                })
        },
        getServer: function () {
            axios.get('/api/server/' + location.pathname.split("/").slice(-2)[0] + '/')
                .then(function (response) {
                    watchVM.loaded = true;
                    watchVM.server = response.data;
                })
                .catch(function (error) {
                    watchVM.loaded = true;
                    watchVM.alertFailure(error.data.message)
                })
        },
        getServers: function () {
            axios.get('/api/servers/')
                .then(function (response) {
                    let servers = response.data.servers;
                    watchVM.m_packages = response.data.m_packages;
                    watchVM.sr_packages = response.data.sr_packages;

                    servers.forEach(function(server, server_id) {
                        let rooms = {};
                        let rooms_count = 0;

                        if (server['rooms']) {
                            let online = 0;
                            let max_online = 0;
                            server['rooms'].forEach(function (room, room_id) {
                                if (!rooms[room['server']]) {
                                    rooms[room['server']] = [];
                                    rooms_count++;
                                }
                                rooms[room['server']].push(room);
                                online += room['online'];
                                max_online += room['max_online'];
                            });
                            servers[server_id]['rooms'] = rooms;
                            servers[server_id]['online'] = online;
                            servers[server_id]['max_online'] = max_online;
                            servers[server_id]['spawners'] = rooms_count;
                        }
                    });


                    console.log(servers);
                    watchVM.servers = servers;
                })
                .catch(function (error) {
                    console.log(error)
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