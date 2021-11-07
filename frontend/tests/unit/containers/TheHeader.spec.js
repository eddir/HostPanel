import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import CoreuiVue from '@coreui/vue'
import TheHeader from '@/containers/TheHeader'
import { shallowMount } from '@vue/test-utils';

Vue.use(CoreuiVue)
Vue.use(regeneratorRuntime);

describe('TheHeader.vue', () => {
  test('renders correctly', () => {
    const wrapper = shallowMount(TheHeader)
    expect(wrapper.element).toMatchSnapshot()
  })
})