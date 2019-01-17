
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
    }
  },
  filters: {
    moment: function (date) {
      if ( date !== '')
        return moment(date).format('MMMM Do, YYYY');
    }
  }
})
