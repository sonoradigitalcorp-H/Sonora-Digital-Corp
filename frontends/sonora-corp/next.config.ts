import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://abe.sonoradigitalcorp.com/api/:path*",
      },
      {
        source: "/ws",
        destination: "https://abe.sonoradigitalcorp.com/ws",
      },
    ];
  },
};

export default nextConfig;
