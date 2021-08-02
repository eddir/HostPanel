<script>
import Vue from "vue";
import API from "@/services/API";
import Utils from "@/services/Utils";

export default {
  name: "Auth",
  components: {API},
  AUTH_TELEGRAM_BOT: API.AUTH_TELEGRAM_BOT,
  telegramLogin(user, redirectUrl = "/") {
    API.post(`${API.SERVER_URL}auth/telegram/login/`, user).then(resp => {
      if (resp.data.success) {
        Utils.setCookie("XCSRF-TOKEN", resp.data.data.csrf, 14);
        Vue.$toast.success("Авторизация пройдена!");
        window.location.href = redirectUrl;
      } else {
        Vue.$toast.error("Не удалось авторизоваться");
      }
    }).catch(err => {
      console.log(err.response);
    })
  },
}
</script>