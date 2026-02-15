import type React from "react"
import "./globals.css"
import { Inter } from "next/font/google"
import Header from "@/components/header"
import Footer from "@/components/footer"
import type { Metadata } from "next"
import Script from "next/script"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: {
    template: "%s | TopicalMD",
    default: "TopicalMD - Expert Topical Pain Relief Reviews & Guides",
  },
  description:
    "Evidence-based reviews, comparisons, and guides for topical pain relief creams, gels, and patches. Find the best treatment for arthritis, muscle pain, neuropathy, and more.",
  metadataBase: new URL("https://topicalmd.com"),
  openGraph: {
    type: "website",
    siteName: "TopicalMD",
    title: "TopicalMD - Expert Topical Pain Relief Reviews & Guides",
    description:
      "Evidence-based reviews, comparisons, and guides for topical pain relief creams, gels, and patches.",
  },
}

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "TopicalMD",
  url: "https://topicalmd.com",
  description:
    "Evidence-based reviews and guides for topical pain relief products.",
  sameAs: [],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
      </head>
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          <Header />
          <main className="flex-grow">{children}</main>
          <Footer />
        </div>
        {/* Google Analytics - replace G-XXXXXXXXXX with your actual ID */}
        {process.env.NEXT_PUBLIC_GA_ID && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
              strategy="afterInteractive"
            />
            <Script id="google-analytics" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
              `}
            </Script>
          </>
        )}
      </body>
    </html>
  )
}
