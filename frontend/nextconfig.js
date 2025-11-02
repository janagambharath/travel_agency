/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',  // Enable static export
  distDir: 'out',     // Output directory
  images: {
    unoptimized: true // Required for static export
  },
  // No need for basePath or assetPrefix since backend serves from root
}

module.exports = nextConfig
