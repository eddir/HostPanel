import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import { shallowMount } from '@vue/test-utils'
import CoreuiVue from '@coreui/vue'
import Dashboard from '@/views/Dashboard'


Vue.use(regeneratorRuntime)
Vue.use(CoreuiVue)

describe('Dashboard.vue', () => {
  it('has a name', () => {
    expect(Dashboard.name).toBe('Dashboard')
  })
  it('is Vue instance', () => {
    const wrapper = shallowMount(Dashboard)
    expect(wrapper.vm).toBeTruthy()
  })
  it('is Dashboard', () => {
    const wrapper = shallowMount(Dashboard)
    expect(wrapper.findComponent(Dashboard)).toBeTruthy()
  })
  test('renders correctly', () => {
    const wrapper = shallowMount(Dashboard)
    expect(wrapper.element).toMatchSnapshot()
  })
})
