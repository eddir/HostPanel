import Vue from 'vue'
import regeneratorRuntime from "regenerator-runtime";
import CoreuiVue from '@coreui/vue'
import TheHeaderDropdownAccnt from '@/containers/TheHeaderDropdownAccnt'
import { shallowMount } from '@vue/test-utils';

Vue.use(CoreuiVue)
Vue.use(regeneratorRuntime);

describe('TheHeaderDropdownAccnt.vue', () => {
  it('has a name', () => {
    expect(TheHeaderDropdownAccnt.name).toBe('TheHeaderDropdownAccnt')
  })
  it('has a created hook', () => {
    expect(typeof TheHeaderDropdownAccnt.data).toMatch('function')
  })
  it('sets the correct default data', () => {
    expect(typeof TheHeaderDropdownAccnt.data).toMatch('function')
    const defaultData = TheHeaderDropdownAccnt.data()
    expect(defaultData.itemsCount).toBe(42)
  })
  test('renders correctly', () => {
    const wrapper = shallowMount(TheHeaderDropdownAccnt)
    expect(wrapper.element).toMatchSnapshot()
  })
})
