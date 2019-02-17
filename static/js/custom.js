
const app = new Vue({
  el: "#app",
  delimiters: ['[[',']]'],
  data: function() {
    showMenu = false;
    return {
      item: "",
      price: "200.00",
      isMessage: "false",
      messagePrice: "50.00",
      name: "",
      dob: "",
      height: "height",
      weight: "",
      message: ""
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
      let cartEl = document.querySelector('#cart');
      cartEl.classList.toggle('active');
    },
    setCart: function() {
      let url = "/setCart";

      fetch(url, {
        method: 'GET',
        mode: 'no-cors',
        dataType: 'json',
      }).then(
        response => response.json()
      ).then(function(myJSON) {
        this.myCart = myJSON;
        console.log(this.myCart)
      })
      .catch(err => console.log(err))
    },
    removeItem: function() {
      let url = document.querySelector('.delete-form').action;
      let form = document.querySelector('.delete-form');
      let data = new FormData(form);

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
  },
})
