<template>

</template>

<script>
export default {
  name: "parentAccess",
  methods: {
    getParent(name){
      let p = this.$parent;
      while(typeof p !== 'undefined'){
        if(p.$options.name === name) {
          return p;
        }else {
          p = p.$parent;
        }
      }
      return false;
    }
  }
}
</script>

<style scoped>

</style>