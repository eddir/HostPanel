function displayConfigSettings() {
    let config = watchVM.config.split("\r\n").map(pair => pair.split("="));
    let element = $("#config");

    element.html("");

    config.forEach(function (row) {
        let property = row[0].slice(1);
        if (property.trim().length === 0) return;
        let div = "";
        switch (property) {
            case "mstStartMaster":
            case "mstStartClientConnection":
                let selectedTrue = row[1] === "true" ?  " selected" : "";
                let selectedFalse = row[1] === "false" ?  " selected" : "";
                div = "<div class=\"input-group\">" +
                    "<input class=\"form-control\" value='" + property + "' type=\"text\" class=\"form-control\" placeholder=\"Ключ\">" +
                    "<select class=\"form-select form-control\" aria-label=\"Select for boolean values\">\n" +
                    "  <option value=\"true\"" + selectedTrue + ">true</option>\n" +
                    "  <option value=\"false\"" + selectedFalse + ">false</option>\n" +
                    "</select>" +
                    "</div>";
                break;
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
        element.append(div);
    });
}

function increaseConfig() {
    $("#config").append("<div class=\"input-group\">" +
                    "<input value='' type=\"text\" class=\"form-control\" placeholder=\"Ключ\">" +
                    "<input value='' type=\"text\" class=\"form-control\" placeholder=\"Значение\">" +
                    "</div>");
}

function saveConfig() {
    let values = "";
    [...$("#config").find(".input-group")].forEach(function (elem) {
        let inputs = $(elem).find("input, select");
        if (inputs[0].value.length > 0) {
            values += "-" + inputs[0].value + "=" + inputs[1].value + "\r\n";
        }
    })
    watchVM.config = values;
    watchVM.updateConfig();
}