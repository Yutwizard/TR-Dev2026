/** @type {import('next').NextConfig} */
const nextConfig = {
    // Enable React Strict Mode
    reactStrictMode: true,

    // API Configuration
    async rewrites() {
        return [
            {
                // Proxy API requests to backend in development
                source: '/api/:path*',
                destination: 'http://localhost:8000/api/:path*',
            },
        ];
    },

    // Environment variables available to the browser
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
        NEXT_PUBLIC_APP_NAME: 'Treasury Management System',
    },
};

module.exports = nextConfig;
