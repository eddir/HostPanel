import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import { shallowMount } from '@vue/test-utils'
import CoreuiVue from '@coreui/vue'
import Page500 from '@/views/Page500'


Vue.use(regeneratorRuntime)
Vue.use(CoreuiVue)

describe('Page500.vue', () => {
  it('has a name', () => {
    expect(Page500.name).toBe('Page500')
  })
  it('is Vue instance', () => {
    const wrapper = shallowMount(Page500)
    expect(wrapper.vm).toBeTruthy()
  })
  it('is Page500', () => {
    const wrapper = shallowMount(Page500)
    expect(wrapper.findComponent(Page500)).toBeTruthy()
  })
  it('should render correct content', () => {
    const wrapper = shallowMount(Page500)
    expect(wrapper.find('h1').text()).toMatch('500')
  })
  test('renders correctly', () => {
    const wrapper = shallowMount(Page500)
    expect(wrapper.element).toMatchSnapshot()
  })
})
