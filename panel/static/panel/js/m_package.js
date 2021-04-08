axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";


let watchVM = new Vue({
    el: '#wrapper',
    data: {
        message: "",
        error: "",
        uploadPercentage: -1,
        packages: {},
        tasks: {},
        form: {
            name: "Сборка ###",
            master: "",
        }
    },
    mounted: function () {
        this.$nextTick(this.getPackages);
        this.$nextTick(this.getTasks);
        window.setInterval(() => {
            this.getTasks();
        }, 10000);
    },
    methods: {
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
        getPackages: function () {
            axios.get('/api/m_package/')
                .then(function (response) {
                    watchVM.packages = response.data.packages;
                })
                .catch(function (error) {
                    watchVM.alertFailure(error.data.message)
                })
        },
        uploadPackage() {
            let formData = new FormData();
            formData.append('name', this.form.name);
            formData.append('type', this.form.type);
            formData.append('master', this.form.master);
            axios.post('/api/m_package/',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    },
                    progress: function (progressEvent) {
                        this.uploadPercentage = Math.round((progressEvent.loaded / progressEvent.total) * 1000) / 10;
                    }.bind(this)
                }
            ).then(function () {
                watchVM.uploadPercentage = -1;
                watchVM.alertSuccess("Сборка загружена.");
                watchVM.getPackages();
            }).catch(function (e) {
                watchVM.alertFailure("Ошибка. " + e.response);
            });
        },
        installPackage(pid) {
            axios.post('/api/m_package/' + pid + '/install/').then(function () {
                watchVM.alertSuccess("Сборка установлена.");
            }).catch(function (e) {
                watchVM.alertFailure("Ошибка. " + e.response);
            });
        },
        handleFileUpload(event) {
            this.form.master = event.target.files[0];
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
        },
    },
})