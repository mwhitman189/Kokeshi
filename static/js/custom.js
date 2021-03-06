const app = new Vue({
    el: "#app",
    delimiters: ['[[', ']]'],
    data: function () {
        showMenu = false;
        return {
            item: "",
            price: "200.00",
            isMessage: "false",
            messagePrice: "50.00",
            name: "",
            dob: "",
            height: "",
            weight: "",
            message: ""
        }
    },
    mounted() {
        // Add kokeshi info to sessionStorage so it can be displayed on the
        // model kokeshi on the design page.
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
        toggleMenu: function () {
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
        toggleCartOn: function () {
            let cartEl = document.querySelector('#cart');
            let cartAttr = document.querySelector('#cart').attributes;
            cartEl.classList.add("active");

            cartEl.setAttribute("aria-hidden", "false");
        },
        toggleCartOff: function () {
            let cartEl = document.querySelector('#cart');
            let cartAttr = document.querySelector('#cart').attributes;
            cartEl.classList.remove("active");

            cartEl.setAttribute("aria-hidden", "true");
        },
        setCart: function () {
            let url = "/setCart";

            fetch(url, {
                    method: 'GET',
                    mode: 'no-cors',
                    dataType: 'json',
                }).then(
                    response => response.json()
                ).then(function (myJSON) {
                    this.myCart = myJSON;
                })
                .catch(err => console.log(err))
        },
        setBackground: function (event) {
            // Set the background image for the front and back view of the kokeshi
            // based on the selected kokeshi style.
            let front = document.querySelector('#kokeshi-model-front');
            let back = document.querySelector('#kokeshi-model-back');

            if (this.item == 'Zao Kokeshi') {
                front.className = "zao-front design__kokeshi-model-front design__kokeshi-model-back";
                back.className = "zao-back design__kokeshi-model-front design__kokeshi-model-back";
            } else if (this.item == 'Yonezawa Kokeshi') {
                front.className = "yonezawa-front design__kokeshi-model-front design__kokeshi-model-back";
                back.className = "yonezawa-back design__kokeshi-model-front design__kokeshi-model-back";
            } else if (this.item == 'Sagae Kokeshi') {
                front.className = "sagae-front design__kokeshi-model-front design__kokeshi-model-back";
                back.className = "sagae-back design__kokeshi-model-front design__kokeshi-model-back";
            } else if (this.item == 'Tendo Kokeshi') {
                front.className = "tendo-front design__kokeshi-model-front design__kokeshi-model-back";
                back.className = "tendo-back design__kokeshi-model-front design__kokeshi-model-back";
            } else {
                front.className = "zao-front design__kokeshi-model-front design__kokeshi-model-back";
                back.className = "zao-back design__kokeshi-model-front design__kokeshi-model-back";
            }
        },
        removeItem: function () {
            let url = document.querySelector('.delete-form').action;
            let form = document.querySelector('.delete-form');
            let data = new FormData(form);

            fetch(url, {
                method: "POST",
                body: data,
            });
        }
    },
    created() {
        window.addEventListener('load', () => {
            try {
                this.setBackground();
            } catch (e) {

            }
        });
        // Add event listener to window, except on the 'cart' element, enabling
        // off-cart clicks to close the cart.
        window.addEventListener('mouseup', function (event) {
            let cartEl = document.querySelector('#cart');
            let menuEl = document.querySelector('#menu');
            let menuBtn = document.querySelector('#menu-toggle');

            if (cartEl.classList.contains('active') && event.target.parentNode.parentNode != cartEl && event.target.parentNode.parentNode.parentNode.parentNode != cartEl && (event.target != cartEl)) {
                app.toggleCartOff();
            }

            if (menuEl.classList.contains('active') && event.target != menuEl && event.target.parentNode != menuEl && event.target.parentNode.parentNode.parentNode.parentNode != menuEl && event.target != menuBtn && event.target.parentNode != menuBtn) {
                app.toggleMenu();
            }
        });
    },
    filters: {
        // Format the date which shows up on the desing page
        moment: function (date) {
            if (date !== '')
                return moment(date).format('MMMM Do, YYYY');
        }
    },
})