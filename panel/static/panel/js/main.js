axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";

var watchVM = new Vue({
    el: '#wrapper',
    delimiters: ['${', '}'],
    data: {
        message: "",
        error: "",
        servers: {},
        server: {},
        form: {
            name: "Server ###",
            ip: "18.209.176.200",
            user_root: "ubuntu",
            password_root: "7#dJ^Y7Qe",
            user_single: "msf",
            password_single: "7#dJ^Y7Qe",
            ssh_key: false,
        }
    },
    mounted: function () {
        path = location.pathname.split("/")

        if (path[1] === "") {
            this.$nextTick(this.getServers);
        } else if (path[1] === "server") {
            this.$nextTick(this.getServer);
        }
    },
    methods: {
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
        getServer: function () {
            axios.get('/api/server/'+location.pathname.split("/").slice(-2)[0]+'/')
                .then(function (response) {
                    watchVM.server = response.data;
                    console.log(watchVM.server);
                })
                .catch(function (error) {
                    watchVM.alertFailure(error)
                })
        },
        getServers: function () {
            axios.get('/api/servers/')
                .then(function (response) {
                    watchVM.servers = response.data.servers;
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