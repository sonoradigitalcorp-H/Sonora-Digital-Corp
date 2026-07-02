export default function middleware(req) {
  const url = new URL(req.url)
  return new Response(`hostname: ${url.hostname}, pathname: ${url.pathname}, href: ${url.href}`, {
    headers: { "content-type": "text/plain" },
  })
}

export const config = {
  matcher: ["/"],
}
