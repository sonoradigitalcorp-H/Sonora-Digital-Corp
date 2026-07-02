export default function middleware(req) {
  return new Response(`hello from middleware`, {
    headers: { "content-type": "text/plain" },
  })
}

export const config = {
  matcher: "/(.*)",
}
