import type { NextConfig } from "next";
import path from "node:path";

const SERVER_URL = process.env.TESSIO_SERVER_URL ?? "http://localhost:3202";

const nextConfig: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: process.cwd(),
  sassOptions: {
    loadPaths: [path.join(process.cwd(), "src")],
  },
  rewrites: async () => {
    return [
      { source: "/api/:path*", destination: `${SERVER_URL}/api/:path*` },
      { source: "/mcp", destination: `${SERVER_URL}/mcp` },
    ];
  },
};

export default nextConfig;
