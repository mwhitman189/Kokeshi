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
    if (localStorage.item) {
      this.item = localStorage.item;
    }
    if (localStorage.price) {
      this.price = localStorage.price;
    }
    if (localStorage.isMessage) {
      this.isMessage = localStorage.isMessage;
    }
    if (localStorage.name) {
      this.name = localStorage.name;
    }
    if (localStorage.dob) {
      this.dob = localStorage.dob;
    }
    if (localStorage.height) {
      this.height = localStorage.height;
    }
    if (localStorage.weight) {
      this.weight = localStorage.weight;
    }
    if (localStorage.message) {
      this.message = localStorage.message;
    }
  },
  methods: {
    persist() {
      localStorage.item = this.item;
      localStorage.price = this.price;
      localStorage.isMessage = this.isMessage;
      localStorage.messagePrice = this.messagePrice;
      localStorage.name = this.name;
      localStorage.dob = this.dob;
      localStorage.height = this.height;
      localStorage.weight = this.weight;
      localStorage.message = this.message;
    }
  }
})
