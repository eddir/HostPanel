<template>
  <div>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>
            Сервера
          </CCardHeader>
          <CCardBody>
            <servers></servers>
          </CCardBody>
        </CCard>
        <CCard>
          <CCardBody>
            <CCardHeader>Вход через телеграм ({{telegramBot}})</CCardHeader>
            <CCardBody>
              <vue-telegram-login
                  mode="callback"
                  :telegram-login="telegramBot"
                  @callback="telegramAuth" />
            </CCardBody>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </div>
</template>

<script>
import {vueTelegramLogin} from 'vue-telegram-login'

import Servers from "@/views/servers/Servers";
import api from "@/services/API"

export default {
  name: 'Dashboard',
  components: {Servers, vueTelegramLogin},
  data() {
    return {
      telegramBot: api.AUTH_TELEGRAM_BOT
    }
  },
  methods: {
    telegramAuth(user) {
      api.login(user);
    }
  }
}
</script>
