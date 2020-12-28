axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";


var watchVM = new Vue({
    el: '#wrapper',
    data: {
        message: "",
        error: "",
        packages: {},
        form: {
            name: "Сборка ###",
            spawner: "",
            room: "",
        }
    },
    mounted: function () {
        this.$nextTick(this.getPackages);
    },
    methods: {
        getPackages: function () {
            axios.get('/api/sr_package/')
                .then(function (response) {
                    watchVM.packages = response.data.packages;
                })
                .catch(function (error) {
                    watchVM.alertFailure(error)
                })
        },
        uploadPackage() {
            let formData = new FormData();
            formData.append('name', this.form.name);
            formData.append('spawner', this.form.spawner);
            formData.append('room', this.form.room);
            axios.post('/api/sr_package/',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            ).then(function () {
                watchVM.alertSuccess("Сборка загружена.");
                watchVM.getPackages();
            }).catch(function (e) {
                watchVM.alertFailure("Ошибка. " + e.response);
            });
        },
        handleFileUpload: function (event) {
            if (event.target.id === "spawner") {
                this.form.spawner = event.target.files[0];
            } else {
                this.form.room = event.target.files[0];
            }
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