/** @type {import('next').NextConfig} */
const nextConfig = {
  // App configuration
  experimental: {
    appDir: true,
  },

  // Image optimization
  images: {
    domains: [
      'localhost',
      'samadhanx.gov.in',
      // Add other image domains as needed
    ],
    formats: ['image/webp', 'image/avif'],
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // Environment variables available to the browser
  env: {
    NEXT_PUBLIC_APP_NAME: 'SamadhanX',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },

  // Headers configuration
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(self)',
          },
        ],
      },
    ]
  },

  // Redirects configuration
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
      {
        source: '/dashboard',
        destination: '/app/dashboard',
        permanent: false,
      },
    ]
  },

  // Webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack configuration
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname,
    }

    // Bundle analyzer
    if (process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: true,
        })
      )
    }

    return config
  },

  // TypeScript configuration
  typescript: {
    // Type checking is handled by tsc in CI/CD
    ignoreBuildErrors: false,
  },

  // ESLint configuration
  eslint: {
    // ESLint is handled separately in CI/CD
    ignoreDuringBuilds: false,
    dirs: ['app', 'components', 'lib', 'types'],
  },

  // Compiler options
  compiler: {
    // Remove console logs in production
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Output configuration
  output: 'standalone',
  
  // Trailing slash
  trailingSlash: false,

  // React strict mode
  reactStrictMode: true,

  // SWC minification
  swcMinify: true,

  // PoweredByHeader
  poweredByHeader: false,

  // Compression
  compress: true,

  // Generate ETags
  generateEtags: true,

  // Page extensions
  pageExtensions: ['ts', 'tsx', 'js', 'jsx'],
}

module.exports = nextConfig