axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";

var watchVM = new Vue({
    el: '#wrapper',
    delimiters: ['${', '}'],
    data: {
        message: "",
        error: "",
        servers: {},
        form: {
            name: "Server ###",
            ip: "54.198.195.121",
            user_root: "ubuntu",
            password_root: "7#dJ^Y7Qe",
            user_single: "msf",
            password_single: "7#dJ^Y7Qe",
        } // create an object to hold all form values
    },
    mounted: function () {
        this.$nextTick(this.getServers)
    },
    methods: {
        createServer: function () {
            axios.post('/api/servers/', this.form)
                .then(function (response) {
                    watchVM.alertSuccess("Сервер добавлен")
                    watchVM.getServers();
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
        notImplemented: function() {
            this.alertFailure("Фича не реализована")
        }
    }
})