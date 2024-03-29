import 'core-js/stable'
import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import App from './App'
import router from './router'
import CoreuiVue from '@coreui/vue'
import { iconsSet as icons } from './assets/icons/icons.js'
import store from './store'

import VueTimeago from 'vue-timeago'

import VueToast from 'vue-toast-notification';
// Import one of the available themes
//import 'vue-toast-notification/dist/theme-default.css';
import 'vue-toast-notification/dist/theme-sugar.css';


Vue.config.performance = true

Vue.use(regeneratorRuntime);


Vue.use(regeneratorRuntime)
Vue.use(CoreuiVue)
Vue.use(VueToast, {position: 'top-right', duration: 5000});
Vue.use(VueTimeago, {
  name: 'Timeago', // Component name, `Timeago` by default
  locale: 'en', // Default locale
  // We use `date-fns` under the hood
  // So you can use all locales from it
  locales: {
    ru: require('date-fns/locale/ru'),
  }
})

Vue.prototype.$log = console.log.bind(console);

Vue.config.errorHandler = (err) => {
  // err: error trace
  // vm: component in which error occured
  // info: Vue specific error information such as lifecycle hooks, events etc.

  Vue.$toast.error(err.message);
  console.error(err);
};

new Vue({
  el: '#app',
  router,
  store,
  icons,
  template: '<App/>',
  components: {
    App
  }
})
