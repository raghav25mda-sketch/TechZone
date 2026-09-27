// ========================================
// TECHZONE GOOGLE ANALYTICS EVENTS
// ========================================


function trackCategory(category) {

    if (typeof gtag === "function") {

        gtag("event", "select_category", {

            category_name: category

        });

    }

}



function trackSearch(searchTerm) {

    if (typeof gtag === "function") {

        gtag("event", "search", {

            search_term: searchTerm

        });

    }

}



function trackViewItem(id, name, category, price) {

    if (typeof gtag === "function") {

        gtag("event", "view_item", {

            currency: "INR",

            value: price,

            items: [

                {

                    item_id: String(id),

                    item_name: name,

                    item_category: category,

                    price: price

                }

            ]

        });

    }

}



function trackAddToCart(id, name, category, price) {

    if (typeof gtag === "function") {

        gtag("event", "add_to_cart", {

            currency: "INR",

            value: price,

            items: [

                {

                    item_id: String(id),

                    item_name: name,

                    item_category: category,

                    price: price,

                    quantity: 1

                }

            ]

        });

    }

}



function trackRemoveFromCart(id, name) {

    if (typeof gtag === "function") {

        gtag("event", "remove_from_cart", {

            item_id: String(id),

            item_name: name

        });

    }

}



function trackViewCart() {

    if (typeof gtag === "function") {

        gtag("event", "view_cart");

    }

}



function trackLogin() {

    if (typeof gtag === "function") {

        gtag("event", "login", {

            method: "email"

        });

    }

}



function trackSignUp() {

    if (typeof gtag === "function") {

        gtag("event", "sign_up", {

            method: "email"

        });

    }

}



function trackBeginCheckout(value) {

    if (typeof gtag === "function") {

        gtag("event", "begin_checkout", {

            currency: "INR",

            value: value

        });

    }

}



function trackPurchaseStart(value) {

    if (typeof gtag === "function") {

        gtag("event", "checkout_submit", {

            currency: "INR",

            value: value

        });

    }

}



// ========================================
// FLASH MESSAGE AUTO-HIDE
// ========================================

setTimeout(function () {

    document
        .querySelectorAll(".flash")
        .forEach(function (element) {

            element.style.transition = "opacity 0.5s";

            element.style.opacity = "0";

            setTimeout(function () {

                element.remove();

            }, 500);

        });

}, 3500);