import {mount} from "@vue/test-utils";
import Status from "src/components/Status.vue";

test("updating and resetting status", async ()=>{
    expect(Status).toBeTruthy();
    const wrapper = mount(Status);
    
    expect(wrapper.text()).toContain("// Status");
    wrapper.vm.updateStatus("UpdatingStatus");
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain("UpdatingStatus");

    wrapper.vm.resetStatus();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).not.toContain("UpdatingStatus");
})
