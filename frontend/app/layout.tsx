import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/lib/auth/AuthContext'
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
        <AuthProvider>
          <div className="min-h-screen">
            {children}
          </div>
          
          {/* Toast notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#fff',
                color: '#333',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </AuthProvider>
        
        {/* TODO: Add analytics scripts */}
      </body>
    </html>
  )
}