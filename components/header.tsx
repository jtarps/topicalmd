import Link from "next/link"
import { Heart } from "lucide-react"
import MobileMenu from "./mobile-menu"
import SearchBar from "./search-bar"

export default function Header() {
  return (
    <header className="border-b shadow-sm">
      <div className="bg-primary text-white py-1 px-4 text-center text-sm">
        <p>Expert-reviewed information on topical treatments and pain relief</p>
      </div>
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-2">
            <Heart className="h-8 w-8 text-primary" fill="currentColor" strokeWidth={1.5} />
            <span className="font-bold text-2xl">TopicalMD</span>
          </Link>

          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/reviews" className="text-gray-700 hover:text-primary font-medium">
              Reviews
            </Link>
            <Link href="/best-for" className="text-gray-700 hover:text-primary font-medium">
              Best For
            </Link>
            <Link href="/compare" className="text-gray-700 hover:text-primary font-medium">
              Comparisons
            </Link>
            <Link href="/ingredient" className="text-gray-700 hover:text-primary font-medium">
              Ingredients
            </Link>
            <Link href="/faq" className="text-gray-700 hover:text-primary font-medium">
              FAQs
            </Link>
          </nav>

          <div className="flex items-center space-x-2">
            <SearchBar />
            <MobileMenu />
          </div>
        </div>
      </div>
      <div className="bg-gray-100 py-2 px-4 border-t border-b border-gray-200 hidden md:block">
        <div className="container mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex space-x-6 text-sm">
              <Link href="/condition/arthritis" className="text-gray-700 hover:text-primary">
                Arthritis
              </Link>
              <Link href="/condition/muscle-pain" className="text-gray-700 hover:text-primary">
                Muscle Pain
              </Link>
              <Link href="/condition/joint-pain" className="text-gray-700 hover:text-primary">
                Joint Pain
              </Link>
              <Link href="/condition/neuropathic-pain" className="text-gray-700 hover:text-primary">
                Neuropathic Pain
              </Link>
              <Link href="/condition/inflammation" className="text-gray-700 hover:text-primary">
                Inflammation
              </Link>
            </div>
            <div className="text-sm text-gray-600">
              <Link href="/medical-advisory-board" className="hover:text-primary">
                Medical Advisory Board
              </Link>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
