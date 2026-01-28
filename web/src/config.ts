/**
 * Application configuration
 *
 * To set the API URL for production (e.g., Vercel):
 * 1. Go to Vercel Dashboard → Project Settings → Environment Variables
 * 2. Add: NEXT_PUBLIC_API_URL = https://your-api-domain.com
 *
 * For local development, it defaults to http://localhost:8000
 */

export const config = {
  // API URL - set NEXT_PUBLIC_API_URL in Vercel environment variables
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
}
