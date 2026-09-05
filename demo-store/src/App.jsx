import { useState } from "react"

const products = [
  {
    id: 1,
    name: "Wireless Headphones",
    price: 49.99,
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"
  },
  {
    id: 2,
    name: "Smart Watch",
    price: 79.99,
    image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"
  },
  {
    id: 3,
    name: "Running Shoes",
    price: 64.99,
    image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600"
  },
  {
    id: 4,
    name: "Travel Backpack",
    price: 39.99,
    image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600"
  }
]

function App() {
  const [cart, setCart] = useState([])

  const addToCart = (product) => {
    setCart([...cart, product])
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-gray-900 text-white px-8 py-5 flex items-center justify-between">
        <h1 className="text-2xl font-bold">
          OmniShop
        </h1>

        <div className="text-lg">
          🛒 Cart ({cart.length})
        </div>
      </header>

      <section className="bg-white px-8 py-16 text-center">
        <h2 className="text-4xl font-bold mb-4">
          Everything You Need
        </h2>

        <p className="text-gray-500">
          Discover our latest products.
        </p>

        <button className="mt-6 bg-blue-600 text-white px-8 py-3 rounded-lg">
          Shop Now
        </button>
      </section>

      <main className="max-w-7xl mx-auto px-8 py-12">
        <h2 className="text-3xl font-bold mb-8">
          Featured Products
        </h2>

        <div className="grid grid-cols-4 gap-0 w-[1200px]">
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
                  ${product.price}
                </p>

                <button
                  onClick={() => addToCart(product)}
                  className="add-to-cart bg-blue-600 text-white px-4 py-2 rounded-lg mt-4"
                >
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>

      <section className="bg-gray-900 text-gray-500 px-8 py-10 mt-10">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-white text-2xl font-bold">
            OmniShop
          </h2>

          <p className="mt-3">
            Quality products for everyone.
          </p>
        </div>
      </section>
    </div>
  )
}

export default App