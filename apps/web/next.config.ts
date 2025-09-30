import type { NextConfig } from "next";
import withPWA from "@ducanh2912/next-pwa";

const nextConfig: NextConfig = {
  output: 'standalone',
  /* config options here */
};

const pwaConfig = withPWA({
  dest: "public",
  register: true,
  disable: process.env.NODE_ENV === "development",
});

export default pwaConfig(nextConfig);
