<template>
  <CContainer>
    <CRow>
      <CCol>
        <CCard>
          <CCardHeader>Пользователи</CCardHeader>
          <CCardBody>
            <CDataTable
                hover
                :items="users"
                :fields="tableFields"
                head-color="light"
                itemsPerPageSelect
                pagination
            >
            </CDataTable>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
import ServersAPI from "@/services/API.vue";

export default {
  name: "Users",
  data() {
    return {
      users: [],
      tableFields: [
        {key: 'username', label: 'Никнейм'},
        {key: 'name', label: 'Имя'},
        {key: 'email', label: 'Почта'},
      ]
    }
  },
  created() {
    ServersAPI.getUsers().then(response => {
      this.users = response.data.response;
    })
  }
}
</script>