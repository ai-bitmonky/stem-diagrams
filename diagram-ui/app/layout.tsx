import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'STEM Diagram Generator',
  description: 'Generate diagrams from physics problem descriptions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
