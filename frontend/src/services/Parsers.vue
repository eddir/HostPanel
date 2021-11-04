<script>
export default {
  name: "Parsers",
  parseStatus(status) {
    return {
      'IN': {'code': 'IN', 'message': 'Устанавливается', 'badge': 'primary'},
      'ST': {'code': 'ST', 'message': 'Запускается', 'badge': 'info'},
      'RN': {'code': 'RN', 'message': 'Запущен', 'badge': 'success'},
      'PS': {'code': 'PS', 'message': 'Останавливается', 'badge': 'info'},
      'SP': {'code': 'SP', 'message': 'Остановлен', 'badge': 'danger'},
      'TR': {'code': 'TR', 'message': 'Удаляется', 'badge': 'warning'},
      'DL': {'code': 'DL', 'message': 'Удалён', 'badge': 'danger'},
      'RB': {'code': 'RB', 'message': 'Ребут', 'badge': 'warning'},
    }[status];
  },//todo: парсеры перенести в другой файл
  parseLog(log) {
    let codes = {
      "&0": "#607d8b",
      "&1": "#3f51b5",
      "&2": "#5cd760",
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

    log = log.split("<br>");
    for (let i = 0; i < log.length; i++) {
      for (const key in codes) {
        let pos = log[i].indexOf(key);
        if (pos !== -1) {
          log[i] = log[i].slice(0, pos) + "<span style='color: " + codes[key] + "'>" +
              log[i].slice(pos + 2) + "</span>";
        }
      }
    }
    return log.join('<br>');
  },
  parseMasters(data) {
    let servers = [];
    /**
     * @param response.data.servers массив игровых серверов
     * @param response.data.dedics массив виртуальных серверов
     * @param response.data.m_packages сборки мастер серверов
     * @param response.data.sr_packages сборки спавнер серверов
     */
    data.servers.forEach(server => {
      let usage, state, activity_time, activity_format;
      /**
       * @param server.status.cpu_usage использование CPU в процентах
       * @param server.status.mem_total объём всей оперативной памяти
       * @param server.status.mem_available количество свободной оперативной памяти
       * @param server.status.disk_total объём всего диска
       * @param server.status.disk_available количество свободного пространства на диске
       * @param server.status.created_at дата создания записи
       */
      if (server.status) {
        state = this.parseStatus(server.status.condition);
        usage = server.status.cpu_usage | 0;
        activity_time = server.status.created_at + "+00:00";
        activity_format = true;
      } else {
        activity_format = false;
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
          id: server.id,
          name: server.name,
          dedic: data.dedics.find(function (dedic) {
            return dedic.id === server.dedic;
          }).name,
          package: package_name,
          new: false,
          registered: "ok",
        },
        country: {name: 'USA', flag: 'cib-server-fault'}, //todo: все страны
        usage: {value: usage},
        status: state,
        parent: server.parent,
        custom: server.custom,
        activity: {
          format: activity_format,
          time: activity_time,
        },
      });

    });

    return servers;
  },
}
</script>

<style scoped>

</style>