import React, { useState, useMemo } from "react";
import products, { categories } from "./data/products";

/* ───────── Star Rating ───────── */
function Stars({ rating }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.3;
  return (
    <span className="inline-flex items-center gap-0.5 text-amber-400 text-sm">
      {[...Array(5)].map((_, i) => (
        <span key={i}>{i < full ? "★" : i === full && half ? "★" : "☆"}</span>
      ))}
      <span className="ml-1 text-gray-400 text-xs">({rating})</span>
    </span>
  );
}

/* ───────── Product Card ───────── */
function ProductCard({ product, index }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className="group relative bg-gradient-to-br from-[#16213e] to-[#1a1a2e] rounded-2xl border border-gray-700/50 hover:border-[#e94560]/60 transition-all duration-500 hover:shadow-[0_0_40px_rgba(233,69,96,0.15)] hover:-translate-y-1 overflow-hidden"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {/* Badge */}
      <div className="absolute top-3 right-3 z-10">
        <span
          className={`bg-gradient-to-r ${product.badgeColor} text-white text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider shadow-lg`}
        >
          {product.badge}
        </span>
      </div>

      {/* Emoji Icon */}
      <div className="flex items-center justify-center pt-8 pb-4">
        <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-[#0f3460]/60 to-[#16213e] flex items-center justify-center text-5xl shadow-inner border border-gray-700/30 group-hover:scale-110 transition-transform duration-500">
          {product.image}
        </div>
      </div>

      {/* Content */}
      <div className="px-5 pb-5">
        <h3 className="text-white font-bold text-lg leading-tight mb-1 group-hover:text-[#e94560] transition-colors">
          {product.name}
        </h3>

        <Stars rating={product.rating} />
        <span className="text-gray-500 text-xs ml-2">
          {product.reviews.toLocaleString()} reviews
        </span>

        {/* Price */}
        <div className="mt-3 mb-3">
          <span className="text-2xl font-extrabold bg-gradient-to-r from-[#e94560] to-[#ff6b6b] bg-clip-text text-transparent">
            {product.price}
          </span>
        </div>

        {/* Description */}
        <p className="text-gray-400 text-sm leading-relaxed mb-3">
          {expanded
            ? product.description
            : product.description.slice(0, 100) + "..."}
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-[#e94560] ml-1 hover:underline text-xs font-medium"
          >
            {expanded ? "Less" : "More"}
          </button>
        </p>

        {/* Features */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {product.features.slice(0, expanded ? 10 : 3).map((f, i) => (
            <span
              key={i}
              className="bg-[#0f3460]/50 text-cyan-300 text-[10px] font-medium px-2 py-0.5 rounded-full border border-cyan-800/30"
            >
              {f}
            </span>
          ))}
          {!expanded && product.features.length > 3 && (
            <span className="text-gray-500 text-[10px] px-2 py-0.5">
              +{product.features.length - 3} more
            </span>
          )}
        </div>

        {/* CTA */}
        <a
          href={product.temuLink}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full text-center bg-gradient-to-r from-[#e94560] to-[#ff6b6b] hover:from-[#ff6b6b] hover:to-[#e94560] text-white font-bold py-2.5 rounded-xl transition-all duration-300 shadow-lg hover:shadow-[0_0_20px_rgba(233,69,96,0.4)] text-sm"
        >
          View on Temu
        </a>
        <p className="text-center text-gray-600 text-[10px] mt-1.5">
          Search: "{product.temuSearch}"
        </p>
      </div>
    </div>
  );
}

/* ───────── Hero Section ───────── */
function Hero() {
  return (
    <section className="relative overflow-hidden py-16 md:py-24">
      {/* Animated bg blobs */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-[#e94560]/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-[#0f3460]/30 rounded-full blur-3xl animate-pulse" />

      <div className="relative max-w-5xl mx-auto text-center px-4">
        <div className="inline-block mb-4">
          <span className="bg-gradient-to-r from-[#e94560]/20 to-[#0f3460]/20 border border-[#e94560]/30 text-[#e94560] text-xs font-bold px-4 py-1.5 rounded-full uppercase tracking-widest">
            Temu AI Collection 2025-2026
          </span>
        </div>
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-black text-white leading-tight mb-6">
          Best{" "}
          <span className="bg-gradient-to-r from-[#e94560] to-[#ff6b6b] bg-clip-text text-transparent">
            AI Robots
          </span>
          <br />
          <span className="text-2xl md:text-4xl lg:text-5xl font-bold text-gray-300">
            Programmable, Zaku, ChatGPT & More
          </span>
        </h1>
        <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-8 leading-relaxed">
          Curated collection of the best AI robots, Gundam Zaku models,
          smart devices & ChatGPT-powered gadgets — all available on Temu
          at unbeatable prices.
        </p>
        <div className="flex flex-wrap justify-center gap-4 text-sm">
          <span className="bg-[#16213e] border border-gray-700 text-gray-300 px-4 py-2 rounded-full">
            🤖 16 Products
          </span>
          <span className="bg-[#16213e] border border-gray-700 text-gray-300 px-4 py-2 rounded-full">
            💰 From $8
          </span>
          <span className="bg-[#16213e] border border-gray-700 text-gray-300 px-4 py-2 rounded-full">
            ⭐ 4.0+ Rated
          </span>
          <span className="bg-[#16213e] border border-gray-700 text-gray-300 px-4 py-2 rounded-full">
            🚀 Free Shipping
          </span>
        </div>
      </div>
    </section>
  );
}

/* ───────── Sort Options ───────── */
const SORT_OPTIONS = [
  { value: "default", label: "Default" },
  { value: "price-low", label: "Price: Low → High" },
  { value: "price-high", label: "Price: High → Low" },
  { value: "rating", label: "Top Rated" },
  { value: "reviews", label: "Most Reviewed" },
];

function getMinPrice(priceStr) {
  const match = priceStr.match(/\$(\d+(?:\.\d+)?)/);
  return match ? parseFloat(match[1]) : 0;
}

/* ───────── Main App ───────── */
export default function App() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("default");

  const filtered = useMemo(() => {
    let result = products;

    if (activeCategory !== "all") {
      result = result.filter((p) => p.category === activeCategory);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.description.toLowerCase().includes(q) ||
          p.features.some((f) => f.toLowerCase().includes(q))
      );
    }

    switch (sortBy) {
      case "price-low":
        result = [...result].sort(
          (a, b) => getMinPrice(a.price) - getMinPrice(b.price)
        );
        break;
      case "price-high":
        result = [...result].sort(
          (a, b) => getMinPrice(b.price) - getMinPrice(a.price)
        );
        break;
      case "rating":
        result = [...result].sort((a, b) => b.rating - a.rating);
        break;
      case "reviews":
        result = [...result].sort((a, b) => b.reviews - a.reviews);
        break;
      default:
        break;
    }

    return result;
  }, [activeCategory, searchQuery, sortBy]);

  return (
    <div className="min-h-screen bg-[#1a1a2e] text-white">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-[#1a1a2e]/90 backdrop-blur-xl border-b border-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🤖</span>
            <span className="font-black text-lg bg-gradient-to-r from-[#e94560] to-[#ff6b6b] bg-clip-text text-transparent">
              TemuAI
            </span>
            <span className="text-gray-500 text-xs font-medium hidden sm:inline">
              Robot Finder
            </span>
          </div>
          <a
            href="https://www.temu.com"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-gradient-to-r from-[#e94560] to-[#ff6b6b] text-white text-xs font-bold px-4 py-2 rounded-full hover:shadow-[0_0_15px_rgba(233,69,96,0.4)] transition-all"
          >
            Open Temu
          </a>
        </div>
      </nav>

      {/* Hero */}
      <Hero />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 pb-20">
        {/* Search + Sort Bar */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
              🔍
            </span>
            <input
              type="text"
              placeholder="Search robots, features, brands..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#16213e] border border-gray-700 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#e94560] focus:ring-1 focus:ring-[#e94560]/30 transition-all"
            />
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-[#16213e] border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-[#e94560] cursor-pointer"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2 mb-8">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                activeCategory === cat.id
                  ? "bg-gradient-to-r from-[#e94560] to-[#ff6b6b] text-white shadow-lg shadow-[#e94560]/20"
                  : "bg-[#16213e] text-gray-400 border border-gray-700 hover:border-[#e94560]/40 hover:text-white"
              }`}
            >
              <span>{cat.emoji}</span>
              <span>{cat.name}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                  activeCategory === cat.id
                    ? "bg-white/20"
                    : "bg-gray-700/50"
                }`}
              >
                {cat.count}
              </span>
            </button>
          ))}
        </div>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-gray-400 text-sm">
            Showing{" "}
            <span className="text-white font-bold">{filtered.length}</span>{" "}
            product{filtered.length !== 1 ? "s" : ""}
            {activeCategory !== "all" && (
              <span>
                {" "}
                in{" "}
                <span className="text-[#e94560]">
                  {categories.find((c) => c.id === activeCategory)?.name}
                </span>
              </span>
            )}
          </p>
        </div>

        {/* Product Grid */}
        {filtered.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {filtered.map((product, index) => (
              <ProductCard key={product.id} product={product} index={index} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-5xl mb-4">🔍</p>
            <p className="text-gray-400 text-lg">
              No products found. Try a different search or category.
            </p>
          </div>
        )}

        {/* Pro Tips Section */}
        <section className="mt-16 bg-gradient-to-br from-[#16213e] to-[#0f3460] rounded-2xl border border-gray-700/50 p-8">
          <h2 className="text-2xl font-bold text-white mb-6">
            💡 Pro Tips for Buying AI Robots on Temu
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <h3 className="text-white font-semibold text-sm">
                    Check Ratings
                  </h3>
                  <p className="text-gray-400 text-xs">
                    Always aim for 4+ stars with 100+ reviews. Read recent
                    reviews for battery life and app compatibility.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <h3 className="text-white font-semibold text-sm">
                    Look for Bluetooth/WiFi
                  </h3>
                  <p className="text-gray-400 text-xs">
                    Robots with Bluetooth or WiFi connectivity offer app-based
                    coding and better AI features.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <h3 className="text-white font-semibold text-sm">
                    Use Coupons
                  </h3>
                  <p className="text-gray-400 text-xs">
                    Temu offers 20-30% off coupons frequently. Check flash
                    sales for even bigger discounts.
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <h3 className="text-white font-semibold text-sm">
                    Avoid Ultra-Cheap "AI"
                  </h3>
                  <p className="text-gray-400 text-xs">
                    Skip $5-10 "AI robots" without sensors — they're just
                    remote-control toys with no real programming.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <h3 className="text-white font-semibold text-sm">
                    Real ChatGPT = Premium
                  </h3>
                  <p className="text-gray-400 text-xs">
                    True ChatGPT integration (like Loona) costs $200+. Budget
                    "AI chat" is usually pre-recorded phrases.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <h3 className="text-white font-semibold text-sm">
                    Free Shipping Over $20
                  </h3>
                  <p className="text-gray-400 text-xs">
                    Most Temu orders over $20 ship free. Bundle items to save
                    on shipping costs.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-gray-500 text-xs">
            🤖 TemuAI Robot Finder — Curated AI robot recommendations. Prices
            are approximate and may vary. Not affiliated with Temu.
          </p>
          <p className="text-gray-600 text-[10px] mt-2">
            Last updated: February 2026
          </p>
        </div>
      </footer>
    </div>
  );
}
