export const icon = {
  mounted(el, binding, vnode) {
    el.innerHTML = `<svg class="bi" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16">
    <use xlink:href="#${binding.value}"/>
  </svg>`
  }
};
