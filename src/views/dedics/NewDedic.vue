<template>
  <CContainer>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>Создание дедика</CCardHeader>
          <CCardBody>
            <CRow>
              <CCol sm="6">
                <CInput :value.sync="input.name" label="Name" placeholder="Название"/>
              </CCol>
              <CCol sm="6">
                <CInput :value.sync="input.ip" label="IP" placeholder="IP адрес"/>
              </CCol>
            </CRow>
            <CRow>
              <CCol sm="6">
                <CInput :value.sync="input.user_root" label="Root" placeholder="Root пользователь"/>
              </CCol>
              <CCol sm="6">
                <CInput :value.sync="input.password_root" label="Root password" placeholder="Root пароль"/>
              </CCol>
            </CRow>
            <CRow>
              <CCol sm="6">
                <CInput :value.sync="input.user_single" label="User" placeholder="Рабочий пользователь"/>
              </CCol>
              <CCol sm="6">
                <div class="form-group">
                  <label>SSH ключ</label>
                  <div class="form-group">
                    <CSwitch :checked.sync="input.ssh_key" color="dark"/>
                  </div>
                </div>
              </CCol>
            </CRow>
            <CButton key="send" color="success" class="m-2" @click="send">Создать</CButton>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
import Action from "@/services/Action";

export default {
  name: "NewDedic",
  data() {
    return {
      input: {
        name: "",
        ip: "",
        user_root: "root",
        user_single: "",
        password_root: "",
        password_single: "",
        ssh_key: false
      }
    }
  },
  methods: {
    send() {
      Action.formAction("create_dedic", this.input, () => window.location.href = '/#/dedics/');
    }
  }
}
</script>

<style scoped>

</style>