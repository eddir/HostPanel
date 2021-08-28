<template>
  <div>
    <CRow>
      <CCol md="12">
        <servers></servers>
      </CCol>
    </CRow>
  </div>
</template>

<script>
import Servers from "@/views/servers/Servers"

export default {
  name: 'Dashboard',
  components: {Servers},
}
</script>
