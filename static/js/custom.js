
const app = new Vue({
  el: "#app",
  delimiters: ['[[',']]'],
  data: function() {
    let item = "";
    let price = "200.00";
    let isMessage = "false";
    let messagePrice = "50.00";
    let name = "";
    let dob = "";
    let height = "";
    let weight = "";
    let message = "";
    showMenu = false;
    return {
      item: item,
      price: price,
      isMessage: isMessage,
      messagePrice: messagePrice,
      name: name,
      dob: dob,
      height: height,
      weight: weight,
      message: message,
      myCart: [
        {
          item: window.sessionStorage.item,
          price: window.sessionStorage.price,
          isMessage: window.sessionStorage.isMessage,
          name: window.sessionStorage.name,
          dob: window.sessionStorage.dob,
          height: window.sessionStorage.height,
          weight: window.sessionStorage.weight,
          message: window.sessionStorage.message
        }
      ]
    }
  },
  mounted() {
    if (window.sessionStorage.item) {
      this.item = window.sessionStorage.item;
    }
    if (window.sessionStorage.price) {
      this.price = window.sessionStorage.price;
    }
    if (window.sessionStorage.isMessage) {
      this.isMessage = window.sessionStorage.isMessage;
    }
    if (window.sessionStorage.name) {
      this.name = window.sessionStorage.name;
    }
    if (window.sessionStorage.dob) {
      this.dob = window.sessionStorage.dob;
    }
    if (window.sessionStorage.height) {
      this.height = window.sessionStorage.height;
    }
    if (window.sessionStorage.weight) {
      this.weight = window.sessionStorage.weight;
    }
    if (window.sessionStorage.message) {
      this.message = window.sessionStorage.message;
    }
  },
  methods: {
    persist() {
      window.sessionStorage.item = this.item;
      window.sessionStorage.price = this.price;
      window.sessionStorage.isMessage = this.isMessage;
      window.sessionStorage.messagePrice = this.messagePrice;
      window.sessionStorage.name = this.name;
      window.sessionStorage.dob = this.dob;
      window.sessionStorage.height = this.height;
      window.sessionStorage.weight = this.weight;
      window.sessionStorage.message = this.message;
    },
    toggleMenu: function() {
      const toggleBtn = document.querySelector('#menu-toggle');
      const menuEl = document.querySelector('#menu');
      const headerEl = document.querySelector('#header');
      const pageWrapEl = document.querySelector('#page-wrapper');
      const visualEl = document.querySelector('#keyvisual');
      const overlay = document.querySelector('#overlay');

      menuEl.classList.toggle('active');
      headerEl.classList.toggle('shifted-right');
      visualEl.classList.toggle('shifted-right');
      overlay.classList.toggle('overlay');

      if (pageWrapEl.style.width !== window.innerWidth + 'px') {
        pageWrapEl.style.width = window.innerWidth + 'px';
        headerEl.style.width = window.innerWidth + 'px';
      } else {
        pageWrapEl.style.width = '';
        headerEl.style.width = '';
      }
    },
    toggleCart: function() {
      const cart = document.querySelector('#cart');
      cart.classList.toggle('active');
      console.log('toggle-active')
    }
  },
  filters: {
    moment: function (date) {
      if ( date !== '')
        return moment(date).format('MMMM Do, YYYY');
    }
  }
})
