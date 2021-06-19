<template>
  <div>
    <CRow>
      <CCol md="12">
        <CCard>
          <CCardHeader>
            Мастер сервера
          </CCardHeader>
          <CCardBody>
            <servers></servers>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </div>
</template>

<script>

import Servers from "@/views/servers/Servers";

export default {
  name: 'Dashboard',
  components: {Servers},
}
</script>
