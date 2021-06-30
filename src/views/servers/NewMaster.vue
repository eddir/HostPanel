<template>
  <CContainer>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>Создание мастера</CCardHeader>
          <CCardBody>
            <CRow>
              <CCol sm="6">
                <CInput label="Name" placeholder="Название сервера"/>
              </CCol>
              <CCol sm="6">
                <CSelect label="Дедик" :options="[1,2,3,4,5,6,7,8,9,10,11,12]"/>
              </CCol>
            </CRow>
            <CRow>
              <CCol sm="6">
                <CSelect label="Сборка" :options="[1,2,3,4,5,6,7,8,9,10,11,12]"/>
              </CCol>
              <CCol sm="6">
                <div class="form-group">
                  <label>SSH ключ</label>
                  <div class="form-group">
                  <CSwitch
                      key="ssh_key"
                      color="dark"
                      checked
                      :value="false"
                  />
                    </div>
                </div>
              </CCol>
            </CRow>
            <CTextarea label="application.cfg" size="9"></CTextarea>
            <CButton key="send" color="success" class="m-2" @click="send">Создать</CButton>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
export default {
  name: "NewMaster",
  created() {
    console.log('created');
  },
  methods: {
    send() {
      //todo: создаёт сервер. Отправляет данные о сервере, введённые пользователем.
    }
  }
}
</script>

<style scoped>
.textarea-config {
  height: 400px !important;
  background-color: red;
}
</style>