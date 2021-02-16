axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";


let watchVM = new Vue({
    el: '#wrapper',
    data: {
        message: "",
        error: "",
        uploadPercentage: -1,
        packages: {},
        form: {
            name: "Сборка ###",
            master: "",
        }
    },
    mounted: function () {
        this.$nextTick(this.getPackages);
    },
    methods: {
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