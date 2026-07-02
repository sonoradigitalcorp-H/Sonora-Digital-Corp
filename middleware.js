export default function middleware(req) {
  const url = new URL(req.url)

  if (url.hostname === "abe.sonoradigitalcorp.com") {
    url.pathname = "/abe/index.html"
    return new Response(null, {
      headers: { "x-middleware-rewrite": url.toString() },
    })
  }

  if (url.hostname === "sonoradigitalcorp.com" || url.hostname === "www.sonoradigitalcorp.com") {
    url.pathname = "/landing/index.html"
    return new Response(null, {
      headers: { "x-middleware-rewrite": url.toString() },
    })
  }
}

export const config = {
  matcher: ["/"],
}
