<template>
  <div>
    <div v-for="(value, key) in config" v-bind:key="key" class="input-table">
      <template v-if="['mstStartMaster', 'mstStartClientConnection'].includes(key)">
        <CInput :value.sync="key"/>
        <CSelect :value.sync="input[key].value" :options="[true, false]"/>
      </template>
      <template v-if="['mstMasterPort', 'mstMaxProcesses'].includes(key)">
        <CInput :value.sync="key"/>
        <CInput :value.sync="input[key].value" type="number"/>
      </template>
    </div>

    <div id="config" class="input-table mb-2" v-html="htmlConfig"></div>
    <button type="button" class="btn btn-outline-success mr-2" @click="increaseConfig">+ поле</button>
    <button type="button" class="btn btn-outline-success" @click="saveConfig">Сохранить</button>
  </div>
</template>

<script>
export default {
  name: "ServerConfig",
  props: {
    rawConfig: String,
    serverId: Number,
  },
  data() {
    return {
      htmlConfig: ""
    }
  },
  computed: {
    config() {
      //todo: переписать всё под vue way
      //return Object.fromEntries(this.rawConfig.split(/\r?\n/).map(pair => pair.substring(1).split("=")));
      return [];
    }
  },
  created() {
    this.input = this.config;
    this.displayConfigSettings();
  },
  methods: {
    displayConfigSettings() {
      let config = this.rawConfig.split(/\r?\n/).map(pair => pair.split("="));
      this.htmlConfig = "";

      config.forEach(row => {
        let property = row[0].slice(1);
        if (property.trim().length === 0) return;
        let div = "";
        switch (property) {
          case "mstStartMaster":
          case "mstStartClientConnection": {
            let selectedTrue = row[1] === "true" ? " selected" : "";
            let selectedFalse = row[1] === "false" ? " selected" : "";
            div = "<div class=\"input-group\">" +
                "<input class=\"form-control\" value='" + property + "' type=\"text\" class=\"form-control\" placeholder=\"Ключ\">" +
                "<select class=\"form-select form-control\" aria-label=\"Select for boolean values\">\n" +
                "  <option value=\"true\"" + selectedTrue + ">true</option>\n" +
                "  <option value=\"false\"" + selectedFalse + ">false</option>\n" +
                "</select>" +
                "</div>";
            break;
          }
          case "mstMasterPort":
          case "mstMaxProcesses":
            div = "<div class=\"input-group\">" +
                "<input value='" + property + "' type=\"text\" class=\"form-control\" placeholder=\"Ключ\">" +
                "<input value='" + row[1] + "' type=\"number\" class=\"form-control\" placeholder=\"Значение\">" +
                "</div>";
            break;
          default:
            div = "<div class=\"input-group\">" +
                "<input value='" + property + "' type=\"text\" class=\"form-control\" placeholder=\"Ключ\">" +
                "<input value='" + row[1] + "' type=\"text\" class=\"form-control\" placeholder=\"Значение\">" +
                "</div>";
        }
        this.htmlConfig += div;
      });
    },
    increaseConfig() {
      this.htmlConfig += "<div class=\"input-group\">" +
          "<input value='' type=\"text\" class=\"form-control\" placeholder=\"Ключ\">" +
          "<input value='' type=\"text\" class=\"form-control\" placeholder=\"Значение\">" +
          "</div>";
    },
    saveConfig() {
      let values = "";
      Array.from(document.getElementById("config").getElementsByClassName("input-group")).forEach(e => {
        let inputs = e.querySelectorAll("input,select");
        if (inputs[0].value.length > 0) {
          values += "-" + inputs[0].value + "=" + inputs[1].value + "\r\n";
        }
      });
      this.$emit('update:config', values);
    }
  }
}
</script>

<style scoped>

</style>