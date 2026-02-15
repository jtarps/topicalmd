import Link from "next/link"
import { Heart } from "lucide-react"

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <Link href="/" className="flex items-center space-x-2">
              <Heart className="h-6 w-6 text-primary" fill="currentColor" strokeWidth={1.5} />
              <span className="font-bold text-xl">TopicalMD</span>
            </Link>
            <p className="text-gray-600">
              Your trusted medical resource for evidence-based information on topical treatments.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4">Content</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/reviews" className="text-gray-600 hover:text-primary">
                  Reviews
                </Link>
              </li>
              <li>
                <Link href="/best-for" className="text-gray-600 hover:text-primary">
                  Best For Guides
                </Link>
              </li>
              <li>
                <Link href="/compare" className="text-gray-600 hover:text-primary">
                  Comparisons
                </Link>
              </li>
              <li>
                <Link href="/ingredient" className="text-gray-600 hover:text-primary">
                  Ingredients
                </Link>
              </li>
              <li>
                <Link href="/faq" className="text-gray-600 hover:text-primary">
                  FAQs
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4">Medical Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/medical-advisory-board" className="text-gray-600 hover:text-primary">
                  Medical Advisory Board
                </Link>
              </li>
              <li>
                <Link href="/editorial-policy" className="text-gray-600 hover:text-primary">
                  Editorial Policy
                </Link>
              </li>
              <li>
                <Link href="/medical-disclaimer" className="text-gray-600 hover:text-primary">
                  Medical Disclaimer
                </Link>
              </li>
              <li>
                <Link href="/research-methodology" className="text-gray-600 hover:text-primary">
                  Research Methodology
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4">Company</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-gray-600 hover:text-primary">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-600 hover:text-primary">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-gray-600 hover:text-primary">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-gray-600 hover:text-primary">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-center text-gray-600 text-sm mb-4 md:mb-0">
              &copy; {new Date().getFullYear()} TopicalMD. All rights reserved.
            </p>
            <p className="text-center text-gray-600 text-sm">
              The content on this website is for informational purposes only. Always consult with a qualified healthcare
              provider.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
