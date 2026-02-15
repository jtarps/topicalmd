"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Menu, X, Search } from "lucide-react"
import { useRouter } from "next/navigation"

export default function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [showSearch, setShowSearch] = useState(false)
  const router = useRouter()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
      setIsOpen(false)
      setShowSearch(false)
    }
  }

  return (
    <div className="md:hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="text-gray-600 hover:text-gray-900 focus:outline-none"
        aria-label={isOpen ? "Close menu" : "Open menu"}
      >
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 bg-white">
          <div className="flex justify-end p-4">
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none"
              aria-label="Close menu"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {showSearch ? (
            <div className="px-6 py-4">
              <form onSubmit={handleSearch} className="flex items-center">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search..."
                  className="w-full h-10 px-4 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  autoFocus
                />
                <button
                  type="submit"
                  className="ml-2 flex items-center justify-center w-10 h-10 rounded-md bg-blue-600 text-white"
                >
                  <Search className="h-5 w-5" />
                </button>
              </form>
              <button onClick={() => setShowSearch(false)} className="mt-2 text-sm text-gray-600">
                Cancel
              </button>
            </div>
          ) : (
            <div className="px-6 py-4">
              <button
                onClick={() => setShowSearch(true)}
                className="flex items-center w-full py-3 text-left text-xl font-medium text-gray-900"
              >
                <Search className="h-5 w-5 mr-2" />
                Search
              </button>
            </div>
          )}

          <nav className="flex flex-col items-center space-y-8 p-8">
            <Link href="/reviews" className="text-xl font-medium text-gray-900" onClick={() => setIsOpen(false)}>
              Reviews
            </Link>
            <Link href="/best-for" className="text-xl font-medium text-gray-900" onClick={() => setIsOpen(false)}>
              Best For
            </Link>
            <Link href="/compare" className="text-xl font-medium text-gray-900" onClick={() => setIsOpen(false)}>
              Comparisons
            </Link>
            <Link href="/ingredient" className="text-xl font-medium text-gray-900" onClick={() => setIsOpen(false)}>
              Ingredients
            </Link>
            <Link href="/faq" className="text-xl font-medium text-gray-900" onClick={() => setIsOpen(false)}>
              FAQs
            </Link>
          </nav>
        </div>
      )}
    </div>
  )
}
