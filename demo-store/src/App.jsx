import { useState } from "react"

const products = [
  {
    id: 1,
    name: "Wireless Headphones",
    price: 49.99,
    image:
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
  },
  {
    id: 2,
    name: "Smart Watch",
    price: 79.99,
    image:
      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
  },
  {
    id: 3,
    name: "Running Shoes",
    price: 64.99,
    image:
      "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
  },
  {
    id: 4,
    name: "Travel Backpack",
    price: 39.99,
    image:
      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600",
  },
]

function App() {
  const [cart, setCart] = useState([])

  const addToCart = (product) => {
    setCart((currentCart) => [...currentCart, product])
  }

  return (
    <div className="min-h-screen bg-gray-100">

      {/* HEADER */}
      <header className="bg-gray-900 text-white px-8 py-5 flex items-center justify-between">
        <h1 className="text-2xl font-bold">
          OmniShop
        </h1>

        <div className="text-lg">
          🛒 Cart ({cart.length})
        </div>
      </header>

      {/* HERO */}
      <section className="bg-white px-8 py-16 text-center">
        <h2 className="text-4xl font-bold mb-4">
          Everything You Need
        </h2>

        <p className="text-gray-500">
          Discover our latest products.
        </p>

        <button
          className="mt-6 bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700"
        >
          Shop Now
        </button>
      </section>

      {/* PRODUCTS */}
      <main className="max-w-7xl mx-auto px-8 py-12">

        <h2 className="text-3xl font-bold mb-8">
          Featured Products
        </h2>

        {/*
          =====================================================
          INTENTIONAL OMNISIGHT TEST BUG
          =====================================================

          The fixed 1200px width causes horizontal overflow
          on mobile and smaller tablet screens.

          DO NOT FIX THIS MANUALLY.

          OmniSight should automatically detect and replace it.
        */}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 w-full">

          {products.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-xl shadow-md overflow-hidden"
            >
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-56 object-cover"
              />

              <div className="p-5">

                <h3 className="product-title text-xl font-bold">
                  {product.name}
                </h3>

                <p className="text-blue-600 font-bold text-lg mt-3">
                  ${product.price.toFixed(2)}
                </p>

                <button
                  onClick={() => addToCart(product)}
                  className="add-to-cart bg-blue-600 text-white px-4 py-2 rounded-lg mt-4 hover:bg-blue-700"
                >
                  Add to Cart
                </button>

              </div>
            </div>
          ))}

        </div>
      </main>

      {/* CART SUMMARY */}
      {cart.length > 0 && (
        <section className="bg-white max-w-7xl mx-auto px-8 py-8 mb-10 rounded-xl shadow">

          <h2 className="text-2xl font-bold mb-4">
            Your Cart
          </h2>

          <p className="text-gray-600">
            You have {cart.length} item
            {cart.length !== 1 ? "s" : ""} in your cart.
          </p>

          <button
            className="mt-5 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            Proceed to Checkout
          </button>

        </section>
      )}

      {/* FOOTER */}
      <footer className="bg-gray-900 text-gray-400 px-8 py-10 mt-10">

        <div className="max-w-7xl mx-auto text-center">

          <h2 className="text-white text-2xl font-bold">
            OmniShop
          </h2>

          <p className="mt-3">
            Quality products for everyone.
          </p>

          <p className="mt-5 text-sm">
            © 2026 OmniShop. All rights reserved.
          </p>

        </div>

      </footer>

    </div>
  )
}

export default App