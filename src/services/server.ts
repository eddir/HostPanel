import axios from "axios";

const REST_URL = "http://147.135.211.1:8000/api/";

//todo: рассмотреть готовые фреймворки вместо этого
async function getMasters() {
    let servers = [];
    const {data} = await axios.get(REST_URL + "servers/");

    data.servers.forEach(function (server) {
        let usage, activity_time, activity_format;

        if (server.status) {
            usage = server.status.cpu_usage
            activity_time = server.status.created_at + "+00:00";
            activity_format = true;
        } else {
            activity_format = false;
            activity_time = 'Недоступен'
        }

        let package_data = data.m_packages.find(function (p) {
            return p.id === server.package
        });
        let package_name = "Неизвестно";
        if (package_data) {
            package_name = package_data.name;
        }

        servers.push({
            host: {
                name: server.name,
                dedic: data.dedics.find(function (dedic) {
                    return dedic.id === server.dedic;
                }).name,
                package: package_name,
                new: false,
                registered: "ok"
            },
            country: {name: 'USA', flag: 'cib-server-fault'}, //todo: все страны
            usage: {value: usage},
            activity: {
                format: activity_format,
                time: activity_time
            }
        });

    });

    return servers;
}

export default {
    getMasters
}