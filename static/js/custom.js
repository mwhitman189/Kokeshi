const app = new Vue({
  el: "#app",
  delimiters: ['[[',']]'],
  data: function() {
    let item = "";
    let price = "200.00"
    let dob = "";
    let height = "";
    let weight = "";
    let message = "";
    return {
      item: item,
      price: price,
      dob: dob,
      height: height,
      weight: weight,
      message: message,
      myCart: [],
    }
  },
  mounted() {
    if (localStorage.item) {
      this.item = localStorage.item;
    }
    if (localStorage.price) {
      this.price = localStorage.price;
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
      localStorage.dob = this.dob;
      localStorage.height = this.height;
      localStorage.weight = this.weight;
      localStorage.message = this.message;
    },
    addToCart: function(product) {
      this.myCart.push(product);
    }
  }
})
