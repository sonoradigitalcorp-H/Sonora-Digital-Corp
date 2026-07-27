document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('navToggle')
  const menu = document.getElementById('navMenu')

  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('active')
      menu.classList.toggle('open')
    })

    document.querySelectorAll('.nav__menu a').forEach(link => {
      link.addEventListener('click', () => {
        toggle.classList.remove('active')
        menu.classList.remove('open')
      })
    })
  }

  const nav = document.getElementById('nav')
  let lastScroll = 0

  window.addEventListener('scroll', () => {
    const current = window.scrollY
    if (current > lastScroll && current > 100) {
      nav.style.transform = 'translateY(-100%)'
    } else {
      nav.style.transform = 'translateY(0)'
    }
    lastScroll = current
  })
})
