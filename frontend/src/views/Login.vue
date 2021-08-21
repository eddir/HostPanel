<template>
  <div class="c-app flex-row align-items-center">
    <CContainer>
      <CRow class="justify-content-center">
        <CCol md="6">
          <CCard class="p-4">
            <CCardHeader><h1>Login</h1></CCardHeader>
            <CCardBody>
              <CAlert color="primary">Требуется авторизация - @{{ telegramBot }}.</CAlert>
              <vue-telegram-login
                  mode="callback"
                  :telegram-login="telegramBot"
                  @callback="telegramAuth"/>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </CContainer>
  </div>
</template>

<script>
import {vueTelegramLogin} from "vue-telegram-login";
import Auth from "@/services/Auth";

export default {
  name: "Login",
  components: {vueTelegramLogin},
  data() {
    return {
      telegramBot: Auth.AUTH_TELEGRAM_BOT
    }
  },
  methods: {
    telegramAuth(user) {
      Auth.telegramLogin(user);
    }
  }
}
</script>
