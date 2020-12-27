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
            type: "1",
            file: ""
        }
    },
    mounted: function () {
        this.$nextTick(this.getPackages);
    },
    methods: {
        getPackages: function () {
            axios.get('/api/package/')
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
            formData.append('type', this.form.type);
            formData.append('file', this.form.file);
            formData.append('size', "0");
            axios.post('/api/package/',
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
        handleFileUpload() {
            this.form.file = this.$refs.file.files[0];
        },
        getType(type_id) {
            return {
                0: "Master",
                1: "Spawner",
                2: "Room",
            }[type_id];
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