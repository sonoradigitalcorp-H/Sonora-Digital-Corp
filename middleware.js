export default function middleware(req) {
  const url = new URL(req.url)

  if (url.hostname === "abe.sonoradigitalcorp.com") {
    url.pathname = "/abe/index.html"
    return Response.rewrite(url)
  }

  if (url.hostname === "sonoradigitalcorp.com" || url.hostname === "www.sonoradigitalcorp.com") {
    if (url.pathname === "/") {
      url.pathname = "/landing/index.html"
      return Response.rewrite(url)
    }
  }

  return Response.rewrite(url)
}

export const config = {
  matcher: "/",
}
