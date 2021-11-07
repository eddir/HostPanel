import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import CoreuiVue from '@coreui/vue'
import TheFooter from '@/containers/TheFooter'
import { shallowMount } from '@vue/test-utils';

Vue.use(CoreuiVue)
Vue.use(regeneratorRuntime);

describe('TheFooter.vue', () => {

  test('renders correctly', () => {
    const wrapper = shallowMount(TheFooter)
    expect(wrapper.element).toMatchSnapshot()
  })
})