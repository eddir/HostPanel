import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import { shallowMount } from '@vue/test-utils'
import CoreuiVue from '@coreui/vue'
import Popovers from '@/views/base/Popovers'

Vue.use(CoreuiVue)
Vue.use(regeneratorRuntime)

describe('Popovers.vue', () => {
  it('has a name', () => {
    expect(Popovers.name).toBe('Popovers')
  })
  it('has a created hook', () => {
    expect(typeof Popovers.data).toMatch('function')
  })
  it('is Vue instance', () => {
    const wrapper = shallowMount(Popovers)
    expect(wrapper.vm).toBeTruthy()
  })
  it('is Popovers', () => {
    const wrapper = shallowMount(Popovers)
    expect(wrapper.findComponent(Popovers)).toBeTruthy()
  })
})

if (global.document) {
  document.createRange = () => ({
    setStart: () => {},
    setEnd: () => {},
    commonAncestorContainer: {
      nodeName: 'BODY',
      ownerDocument: document,
    },
  });
}
