import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import { shallowMount } from '@vue/test-utils'
import CoreuiVue from '@coreui/vue'
import ListGroups from '@/views/base/ListGroups'

Vue.use(CoreuiVue)
Vue.use(regeneratorRuntime)

describe('ListGroups.vue', () => {
  it('has a name', () => {
    expect(ListGroups.name).toBe('ListGroups')
  })
  it('is Vue instance', () => {
    const wrapper = shallowMount(ListGroups)
    expect(wrapper.vm).toBeTruthy()
  })
  it('is ListGroups', () => {
    const wrapper = shallowMount(ListGroups)
    expect(wrapper.findComponent(ListGroups)).toBeTruthy()
  })
  test('renders correctly', () => {
    const wrapper = shallowMount(ListGroups)
    expect(wrapper.element).toMatchSnapshot()
  })
})
