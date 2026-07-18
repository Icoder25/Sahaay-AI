/**
 * Backend API base URL (no trailing slash).
 * Local default: http://localhost:8000
 * Replit: https://<backend>.replit.app
 */
export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");
