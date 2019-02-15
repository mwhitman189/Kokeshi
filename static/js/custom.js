
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
    let cart = [];
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
      cart: cart
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
    if (window.sessionStorage.cart) {
      this.cart = window.sessionStorage.cart;
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
      window.sessionStorage.cart = this.cart;
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
      let cart = document.querySelector('#cart');
      cart.classList.toggle('active');
      console.log('toggle-active')
    },
    setCart: function() {
      let url = "/setCart";

      fetch(url, {
        method: 'GET',
        mode: 'no-cors',
        dataType: 'json',
      }).then(
        response => response.json()
      ).then(
        response => {
          this.cart.push(response)
      })
      .catch(err => console.log(err))
    },
    itemCount: function() {
      itemCount = cart.length
      return itemCount
    },
    beforeUpdate() {
      setCart()
    },
    removeItem: function() {
      let url = document.querySelector('.delete-form').action;
      let form = document.querySelector('.delete-form');
      let data = new FormData(form);
      console.log(url);

      fetch(url, {
        method: "POST",
        body: data,
      });
    }
  },
  filters: {
    moment: function (date) {
      if ( date !== '')
        return moment(date).format('MMMM Do, YYYY');
    }
  }
})
