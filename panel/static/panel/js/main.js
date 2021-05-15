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
        dedics: {},
        loaded: false,
        tasks: {},
        form: {
            parent: null,
            name: "Unit " + Math.floor(Math.random() * 1000),
            ip: "5.180.138.187",
            user_root: "root",
            password_root: "CHBE644Q7x82",
            user_single: "msf2",
            ssh_key: false,
            package: null,
            dedic: null,
            type: "master",
            config: "",
        }
    },
    mounted: function () {
        let path = location.pathname.split("/")

        if (path[1] === "") {
            this.$nextTick(this.getServers);
            window.setInterval(() => {
                this.getServers();
            }, 10000);

        } else if (path[1] === "server" && path.length === 4) {
            this.$nextTick(this.getServer);
            window.setInterval(() => {
                this.getServer();
            }, 5000);
        } else if (path[1] === "dedicated") {
            this.$nextTick(this.getDedics);
            window.setInterval(() => {
                this.getDedics();
            }, 10000);
        }
        this.$nextTick(this.getTasks);
        window.setInterval(() => {
            this.getTasks();
        }, 10000);
    },
    updated: function () {
        if (location.pathname.split("/")[1] === "server") {
            let server_log = document.getElementById('server_log');
            if (server_log) {
                server_log.scrollTop = server_log.scrollHeight;
            }
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
        changeConfig: function (isSpawner) {
            if (isSpawner) {
                let dedic = watchVM.dedics.find(function (d) {
                    return d.id === watchVM.form.dedic;
                });

                this.form['config'] =
                    "-mstStartSpawner=true\n" +
                    "-mstStartClientConnection=true\n" +
                    "-mstMasterIp=" + watchVM.server.dedic_data.ip + "\n" +
                    "-mstMasterPort=5000\n" +
                    "-mstRoomIp=" + dedic.ip + "\n" +
                    "-mstRoomExe=\\home\\" + dedic.user_single + "\\HostPanel\\Pack\\Room\\Room.x86_64\n" +
                    "-mstMaxProcesses=1"
            } else {
                this.form['config'] = "-mstStartMaster=true\n" +
                    "-mstStartClientConnection=true\n" +
                    "-mstMasterIp=127.0.0.1\n" +
                    "-mstMasterPort=5000"
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
        removeServer: function (type) {
            if (confirm("Удалить сервер безвозвратно?")) {
                axios.delete('/server/' + watchVM.server.server.id + '/delete/confirm/')
                    .then(function (response) {
                        window.location = '/';
                    })
                    .catch(function (error) {
                        watchVM.alertFailure(error.data.message);
                    });
            }
        },
        reinstallServer: function () {
            if (confirm("Переустановка может привести к потере данных. Будут переустановлены все сервера " +
                "под данным пользователем. Продолжить?")) {
                axios.post('/api/server/' + watchVM.server.server.id + '/')
                    .then(watchVM.getServer)
                    .catch(function (error) {
                        watchVM.alertFailure(error.data.message);
                    });
            }
        },
        createDedic: function (type) {
            axios.post('/api/dedics/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер добавлен");
                    watchVM.getDedics();
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data.message);
                })
        },
        deleteDedic: function (dedic) {
            if (!dedic['has_child']) {
                if (confirm("Удалить дедик " + dedic.name + " вместе со всеми данными на нём?")) {
                    axios.post("/dedic/" + dedic.id + "/delete/confirm/")
                        .then(function (response) {
                            watchVM.alertSuccess("Удаление запущено.");
                        })
                        .catch(function (error) {
                            watchVM.alertFailure(error.data.message);
                        })
                }
            } else {
                watchVM.alertFailure("Нельзя удалить дедик с серверами на нём.");
            }
        },
        reboot: function (server_id) {
            if (confirm("Начать ребут вдс?")) {
                axios.patch('/api/server/' + server_id + '/')
                    .then(function (response) {
                        watchVM.alertSuccess("Ребут запущен");
                    })
                    .catch(function (error) {
                        watchVM.alertFailure(error.data.message);
                    })
            }
        },
        updateConfig: function () {
            axios.post('/api/server/' + this.server.server.id + "/config/", {"config": this.server.server.config})
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

                    if (watchVM.server.status) {
                        let conditions = {
                            'IN': {'code': 'IN', 'message': 'Устанавливается', 'badge': 'badge badge-primary'},
                            'ST': {'code': 'ST', 'message': 'Запускается', 'badge': 'badge badge-info'},
                            'RN': {'code': 'RN', 'message': 'Запущен', 'badge': 'badge badge-success'},
                            'PS': {'code': 'PS', 'message': 'Останавливается', 'badge': 'badge badge-info'},
                            'SP': {'code': 'SP', 'message': 'Остановлен', 'badge': 'badge badge-danger'},
                            'TR': {'code': 'TR', 'message': 'Удаляется', 'badge': 'badge badge-warning'},
                            'DL': {'code': 'DL', 'message': 'Удалён', 'badge': 'badge badge-danger'},
                            'RB': {'code': 'RB', 'message': 'Ребут', 'badge': 'badge badge-warning'},
                        }

                        watchVM.server.status['condition'] = conditions[watchVM.server.status['condition']];
                    }

                    let data = [];
                    response.data['history']['status'].forEach(function (status) {
                        data.push({
                            'x': status['created_at'],
                            'y': status['cpu_usage']
                        });
                    });

                    draw_charts(data);

                    if (response.data.server.log) {
                        let codes = {
                            "&0": "#607d8b",
                            "&1": "#3f51b5",
                            "&2": "#4caf50",
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

                        let log = response.data.server.log.split("<br>");
                        for (let i = 0; i < log.length; i++) {
                            for (const key in codes) {
                                let pos = log[i].indexOf(key);
                                if (pos !== -1) {
                                    console.log()
                                    log[i] = log[i].slice(0, pos) + "<span style='color: " + codes[key] + "'>" +
                                        log[i].slice(pos + 2) + "</span>";
                                }
                            }
                        }
                        watchVM.server.server.log = log.join('<br>');
                    }
                })
                .catch(function (error) {
                    watchVM.loaded = true;
                    watchVM.alertFailure(error)
                })
        },
        getDedics: function () {
            axios.get('/api/dedics/')
                .then(function (response) {
                    let dedics = response.data.dedics;
                    for (let i = 0; i < dedics.length; i++) {
                        if (dedics[i]['condition']) {
                            dedics[i]['condition'] = {
                                'code': 'ON',
                                'message': 'Подключен',
                                'badge': 'badge badge-success'
                            }
                        } else {
                            dedics[i]['condition'] = {
                                'code': 'OF',
                                'message': 'Недоступен',
                                'badge': 'badge badge-danger'
                            }
                        }
                    }
                    watchVM.servers = dedics;
                })
                .catch(function (error) {
                    console.log(error);
                    watchVM.alertFailure(error);
                })
        },
        showDedicLogs: function (dedic_id) {
            $('#log').html(watchVM.servers.find(el => el.id === dedic_id).log)
        },
        getServers: function () {
            axios.get('/api/servers/')
                .then(function (response) {
                    let servers = response.data.servers;
                    watchVM.m_packages = response.data.m_packages;
                    watchVM.sr_packages = response.data.sr_packages;
                    watchVM.dedics = response.data.dedics;

                    servers.forEach(function (server, server_id) {
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
                        servers[server_id]['dedic_data'] = watchVM.dedics.find(
                            el => el.id === servers[server_id]['dedic'])
                    });

                    watchVM.servers = servers;
                })
                .catch(function (error) {
                    console.log(error)
                    watchVM.alertFailure(error)
                })
        },
        getTasks: function () {
            axios.get('/api/task/')
                .then(function (response) {
                    watchVM.tasks = response.data.tasks;
                    let actions = {
                        "init": "Установка",
                        "start": "Запуск",
                        "update": "Обновление",
                        "reboot": "Ребут",
                        "update_config": "Обновление конфига",
                        "stop": "Остановка",
                        "delete": "Удаление",
                        "install_package": "Установка сборки",
                        "reconnect": "Переподключение",
                        "update_caretaker_legacy": "Обновление скрипта",
                        "update_caretaker": "Обновление скрипта",
                        "reinstall": "Переустановка",
                    }
                    watchVM.tasks.forEach(function (task, task_id) {
                        let params = JSON.parse(task['task_params']);
                        watchVM.tasks[task_id]['params'] = params;
                        watchVM.tasks[task_id]['action'] = actions[params[0][1]];
                    });
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