import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SamadhanX - Jharkhand Societal Innovation Exchange',
  description: 'Converting real societal problems into university-led innovation projects supported by industry and monitored by government.',
  keywords: [
    'societal innovation',
    'jharkhand',
    'university collaboration',
    'government solutions',
    'citizen challenges',
    'industry partnership'
  ],
  authors: [{ name: 'SamadhanX Team' }],
  openGraph: {
    title: 'SamadhanX - Societal Innovation Platform',
    description: 'Bridging citizens, universities, and industry for societal impact',
    type: 'website',
    locale: 'en_IN',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} antialiased bg-gray-50 text-gray-900`}>
        <div className="min-h-screen">
          {children}
        </div>
        
        {/* TODO: Add toast notifications container */}
        {/* TODO: Add loading spinner overlay */}
        {/* TODO: Add analytics scripts */}
      </body>
    </html>
  )
}