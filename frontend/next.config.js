/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'oss.talesofai.cn',
                pathname: '**',
            },
        ],
    },
    async headers() {
        return [
            {
                // 匹配所有API路由
                source: '/api/:path*',
                headers: [
                    { key: 'Access-Control-Allow-Origin', value: '*' },
                    { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH' },
                    { key: 'Access-Control-Allow-Headers', value: '*' },
                    { key: 'Access-Control-Allow-Credentials', value: 'true' },
                    { key: 'Access-Control-Max-Age', value: '86400' },
                ],
            },
            {
                // 匹配所有路由
                source: '/:path*',
                headers: [
                    { key: 'Access-Control-Allow-Origin', value: '*' },
                    { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH' },
                    { key: 'Access-Control-Allow-Headers', value: '*' },
                    { key: 'Access-Control-Allow-Credentials', value: 'true' },
                    { key: 'Access-Control-Max-Age', value: '86400' },
                ],
            },
        ];
    },
};

module.exports = nextConfig;
