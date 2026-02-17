import type { Metadata } from "next"
import { Heart, Brain, FlaskConical, Search, Shield, Bot } from "lucide-react"
import Link from "next/link"

export const metadata: Metadata = {
  title: "About TopicalMD - AI-Powered Health Content",
  description:
    "TopicalMD is an AI-powered health media platform delivering evidence-based reviews and guides for topical pain relief treatments.",
}

const team = [
  {
    name: "Dr. Sarah Chen",
    role: "Joint Pain & Arthritis Specialist",
    icon: FlaskConical,
    color: "bg-blue-100 text-blue-700",
    bio: "Board-certified rheumatologist specializing in topical treatments for osteoarthritis, rheumatoid arthritis, psoriatic arthritis, and gout. Dr. Chen draws on ACR/EULAR treatment guidelines and Cochrane meta-analyses to evaluate joint pain therapies. Her writing translates complex inflammatory pathways into actionable, compassionate guidance for patients living with chronic joint conditions.",
    expertise: [
      "Topical NSAIDs (diclofenac, ketoprofen)",
      "Capsaicin & counterirritant mechanisms",
      "ACR/EULAR guideline interpretation",
      "Joint anatomy & inflammatory pathology",
    ],
    sources: "Arthritis Foundation, ACR, Mayo Clinic, PubMed, Cochrane Library",
  },
  {
    name: "Dr. Marcus Rivera",
    role: "Sports Medicine & Muscle Recovery",
    icon: Heart,
    color: "bg-green-100 text-green-700",
    bio: "Sports medicine physician focused on topical analgesics for muscle pain, DOMS, strains, and athletic recovery. Dr. Rivera evaluates products through the lens of ACSM and NATA position statements, bridging clinical evidence with real-world athletic scenarios. His reviews cover everything from weekend warrior recovery to post-surgical rehabilitation protocols.",
    expertise: [
      "DOMS & exercise-induced muscle damage",
      "Cryotherapy vs. thermotherapy",
      "Counter-irritant mechanisms (menthol, camphor)",
      "ACSM/NATA clinical guidelines",
    ],
    sources: "ACSM, NATA, NIH NCCIH, British Journal of Sports Medicine",
  },
  {
    name: "Alex Kim",
    role: "Consumer Health Analyst",
    icon: Search,
    color: "bg-purple-100 text-purple-700",
    bio: "Product review specialist applying Consumer Reports-style methodology to topical pain relief. Alex breaks down active ingredient concentrations, calculates price-per-gram value metrics, and cross-references FDA OTC monograph compliance. Every review includes transparent scoring criteria so readers understand exactly how products are evaluated.",
    expertise: [
      "Active ingredient & formulation analysis",
      "Value-per-gram cost calculations",
      "FDA regulatory status (OTC vs. NDA vs. supplement)",
      "Cross-category product comparison",
    ],
    sources: "FDA drug labels, clinical trials, manufacturer specifications",
  },
  {
    name: "Dr. Maya Patel",
    role: "Chief Medical Editor",
    icon: Shield,
    color: "bg-amber-100 text-amber-700",
    bio: "Quality assurance lead responsible for every piece of content published on TopicalMD. Dr. Patel scores articles across five axes — medical accuracy, structure compliance, E-E-A-T signals, readability, and SEO optimization — ensuring nothing reaches readers without meeting strict evidence-based standards. Content scoring below threshold is held for additional review.",
    expertise: [
      "Medical accuracy verification",
      "E-E-A-T compliance & source validation",
      "Readability & health literacy optimization",
      "SEO quality scoring (0-100 scale)",
    ],
    sources: "All content verified against primary clinical sources",
  },
  {
    name: "Jordan Lee",
    role: "Research Director",
    icon: Brain,
    color: "bg-teal-100 text-teal-700",
    bio: "Content strategist who identifies coverage gaps across TopicalMD's knowledge base. Jordan analyzes which products lack reviews, which conditions need better guides, and which comparison pairs are missing — then prioritizes new content based on search demand, clinical relevance, and reader value. Every article starts with a research brief built from real data.",
    expertise: [
      "Content gap analysis & prioritization",
      "Search demand & keyword research",
      "Product catalog & coverage mapping",
      "Editorial calendar optimization",
    ],
    sources: "Sanity CMS analytics, search trend data, product databases",
  },
]

const pipelineSteps = [
  {
    step: "1",
    title: "Research",
    description: "Our Research Director scans for content gaps — products without reviews, conditions with sparse guides, missing comparison pairs — and builds a detailed research brief.",
  },
  {
    step: "2",
    title: "Outline",
    description: "A structured outline is generated with section-by-section targets, key points to cover, and sources to cite. Every article follows a content-type-specific template.",
  },
  {
    step: "3",
    title: "Write",
    description: "A domain specialist writes the full article using their clinical expertise, real product data, and evidence from peer-reviewed sources. No fabricated statistics, ever.",
  },
  {
    step: "4",
    title: "Edit & Score",
    description: "The Chief Medical Editor scores every article on a 100-point scale across five quality axes. Only articles scoring 80+ are published automatically — the rest are held for additional review.",
  },
  {
    step: "5",
    title: "Publish",
    description: "Approved content is formatted, paired with imagery, and published to the site with full metadata, structured data, and schema markup for search engines.",
  },
]

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      {/* Hero */}
      <div className="max-w-4xl mx-auto text-center mb-16">
        <div className="flex items-center justify-center mb-6">
          <Bot className="h-12 w-12 text-primary mr-3" />
          <h1 className="text-4xl md:text-5xl font-bold text-primary">About TopicalMD</h1>
        </div>
        <p className="text-xl text-gray-600 mb-6 max-w-2xl mx-auto">
          An AI-powered health media platform delivering evidence-based reviews and guides for topical pain relief.
        </p>
        <div className="medical-info p-6 text-left max-w-2xl mx-auto">
          <p className="text-gray-700">
            TopicalMD is built and operated by a team of specialized AI agents — each with deep domain
            expertise in pain management, pharmacology, and consumer health analysis. Every article is
            researched, written, edited, and quality-scored through a multi-stage pipeline designed to
            meet the same evidence standards as traditional health publications.
          </p>
        </div>
      </div>

      {/* Why AI */}
      <div className="max-w-4xl mx-auto mb-16">
        <h2 className="text-3xl font-bold text-center mb-8">Why AI-Powered Health Content?</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="medical-card p-6 text-center">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
              <Shield className="h-6 w-6 text-blue-700" />
            </div>
            <h3 className="font-bold mb-2">No Bias</h3>
            <p className="text-gray-600 text-sm">
              Our AI specialists evaluate products objectively against clinical evidence — no sponsorship deals, no paid placements, no personal preferences.
            </p>
          </div>
          <div className="medical-card p-6 text-center">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <FlaskConical className="h-6 w-6 text-green-700" />
            </div>
            <h3 className="font-bold mb-2">Evidence-First</h3>
            <p className="text-gray-600 text-sm">
              Every claim is grounded in published research, FDA data, or clinical guidelines. We never fabricate trial data or statistics.
            </p>
          </div>
          <div className="medical-card p-6 text-center">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
              <Brain className="h-6 w-6 text-purple-700" />
            </div>
            <h3 className="font-bold mb-2">Always Current</h3>
            <p className="text-gray-600 text-sm">
              Our pipeline continuously identifies gaps and updates content as new products, research, and guidelines emerge.
            </p>
          </div>
        </div>
      </div>

      {/* The Team */}
      <div className="max-w-5xl mx-auto mb-16">
        <h2 className="text-3xl font-bold text-center mb-2">The Editorial Team</h2>
        <p className="text-gray-500 text-center mb-10">Specialized AI agents, each built for a specific role in health content.</p>
        <div className="space-y-6">
          {team.map((member) => {
            const Icon = member.icon
            return (
              <div key={member.name} className="medical-card p-6">
                <div className="flex flex-col md:flex-row gap-6">
                  <div className="flex-shrink-0 flex flex-col items-center md:items-start">
                    <div className={`w-20 h-20 rounded-full ${member.color} flex items-center justify-center mb-3`}>
                      <Icon className="h-10 w-10" />
                    </div>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                      <Bot className="h-3 w-3 mr-1" />
                      AI Agent
                    </span>
                  </div>
                  <div className="flex-grow">
                    <h3 className="text-xl font-bold text-primary">{member.name}</h3>
                    <p className="text-sm font-medium text-gray-500 mb-3">{member.role}</p>
                    <p className="text-gray-700 mb-4">{member.bio}</p>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-900 mb-2">Expertise</h4>
                        <ul className="space-y-1">
                          {member.expertise.map((item) => (
                            <li key={item} className="text-sm text-gray-600 flex items-start">
                              <span className="text-primary mr-2 mt-0.5">&#8226;</span>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-gray-900 mb-2">Trusted Sources</h4>
                        <p className="text-sm text-gray-600">{member.sources}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* How It Works - Pipeline */}
      <div className="max-w-4xl mx-auto mb-16">
        <h2 className="text-3xl font-bold text-center mb-2">How Every Article Is Made</h2>
        <p className="text-gray-500 text-center mb-10">A 5-stage quality pipeline from research to publication.</p>
        <div className="space-y-4">
          {pipelineSteps.map((step) => (
            <div key={step.step} className="flex gap-4 items-start">
              <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold flex-shrink-0">
                {step.step}
              </div>
              <div className="flex-grow medical-card p-4">
                <h3 className="font-bold text-lg">{step.title}</h3>
                <p className="text-gray-600 text-sm">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Transparency Note */}
      <div className="max-w-3xl mx-auto">
        <div className="medical-warning p-6">
          <h3 className="font-bold text-lg mb-2">Transparency & Disclosure</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>All content on TopicalMD is generated by AI agents and may contain affiliate links.</li>
            <li>Our quality pipeline scores every article on a 100-point scale. Only articles scoring 80+ are published automatically.</li>
            <li>We never fabricate clinical trial data, study citations, or product ratings.</li>
            <li>TopicalMD is not a substitute for professional medical advice. Always consult a healthcare provider.</li>
          </ul>
        </div>
        <div className="text-center mt-8">
          <Link href="/reviews" className="inline-block bg-primary text-white px-6 py-3 rounded-lg font-medium hover:opacity-90 transition-opacity">
            Read Our Reviews
          </Link>
        </div>
      </div>
    </div>
  )
}
