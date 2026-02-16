import { PortableText, type PortableTextComponents } from "@portabletext/react"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import Link from "next/link"

/**
 * Detects pipe-separated table lines in a text block and returns parsed rows,
 * or null if the text is not a table.
 *
 * Expected format:
 *   | Header1 | Header2 |
 *   | --- | --- |
 *   | Cell1 | Cell2 |
 */
function parseTableFromText(text: string): string[][] | null {
  const lines = text.split("\n").filter((l) => l.trim().length > 0)
  if (lines.length < 2) return null

  const isTableLine = (line: string) => {
    const trimmed = line.trim()
    return trimmed.startsWith("|") && trimmed.endsWith("|")
  }

  if (!lines.every(isTableLine)) return null

  const rows = lines
    .filter((line) => {
      // Filter out separator rows like | --- | --- |
      const cells = line
        .trim()
        .slice(1, -1)
        .split("|")
        .map((c) => c.trim())
      return !cells.every((c) => /^-+$/.test(c))
    })
    .map((line) =>
      line
        .trim()
        .slice(1, -1)
        .split("|")
        .map((c) => c.trim())
    )

  if (rows.length < 2 || rows[0].length < 2) return null
  return rows
}

const components: PortableTextComponents = {
  types: {
    image: ({ value }) => {
      if (!value?.asset) return null
      return (
        <div className="relative w-full h-[300px] md:h-[400px] my-6">
          <Image
            src={urlForImage(value).url()}
            alt={value.alt || ""}
            fill
            className="object-cover rounded-lg"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
          {value.caption && (
            <p className="text-sm text-gray-500 text-center mt-2">{value.caption}</p>
          )}
        </div>
      )
    },
  },
  block: {
    h1: ({ children }) => (
      <h1 className="text-3xl md:text-4xl font-bold mt-10 mb-4 text-primary">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-2xl md:text-3xl font-bold mt-8 mb-4 text-primary">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-xl md:text-2xl font-bold mt-6 mb-3 text-primary">{children}</h3>
    ),
    h4: ({ children }) => (
      <h4 className="text-lg font-bold mt-5 mb-2 text-primary">{children}</h4>
    ),
    normal: ({ children, value }) => {
      // Check if this block contains pipe-separated table text
      const textContent =
        value?.children
          ?.filter((c: any) => c._type === "span")
          .map((c: any) => c.text)
          .join("") || ""

      const tableRows = parseTableFromText(textContent)
      if (tableRows) {
        const [header, ...body] = tableRows
        return (
          <div className="portable-table-wrapper my-6">
            <table className="portable-table">
              <thead>
                <tr>
                  {header.map((cell, i) => (
                    <th key={i}>{cell}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {body.map((row, ri) => (
                  <tr key={ri}>
                    {row.map((cell, ci) => (
                      <td key={ci}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      }

      return <p className="mb-4 leading-relaxed">{children}</p>
    },
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-primary/30 pl-4 italic my-4 text-gray-700">
        {children}
      </blockquote>
    ),
  },
  marks: {
    strong: ({ children }) => <strong className="font-bold">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
    underline: ({ children }) => <span className="underline">{children}</span>,
    code: ({ children }) => (
      <code className="bg-gray-100 rounded px-1.5 py-0.5 text-sm font-mono">{children}</code>
    ),
    link: ({ value, children }) => {
      const href = value?.href || "#"
      const isExternal = href.startsWith("http")
      if (isExternal) {
        return (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            {children}
          </a>
        )
      }
      return (
        <Link href={href} className="text-primary hover:underline">
          {children}
        </Link>
      )
    },
  },
  list: {
    bullet: ({ children }) => (
      <ul className="list-disc pl-6 mb-4 space-y-1.5 marker:text-primary/60">{children}</ul>
    ),
    number: ({ children }) => (
      <ol className="list-decimal pl-6 mb-4 space-y-1.5 marker:text-primary/60">{children}</ol>
    ),
  },
  listItem: {
    bullet: ({ children }) => <li className="leading-relaxed">{children}</li>,
    number: ({ children }) => <li className="leading-relaxed">{children}</li>,
  },
}

type PortableTextRendererProps = {
  value: any
  className?: string
}

export default function PortableTextRenderer({ value, className }: PortableTextRendererProps) {
  if (!value) return null

  return (
    <div className={className || "prose max-w-none"}>
      <PortableText value={value} components={components} />
    </div>
  )
}
