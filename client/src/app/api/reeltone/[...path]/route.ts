import { NextRequest } from "next/server";
import { reviewsCookie } from "@/lib/reviewsAuth";
import { getBackendUrl } from "@/lib/serverBackend";

type Context = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: Context) {
  const { path } = await context.params;
  if (path.some((part) => part === "." || part === ".." || /[\\/\0]/.test(part))) {
    return new Response("Invalid request path", { status: 400 });
  }
  const address = `${getBackendUrl()}/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;
  const headers = new Headers();
  for (const name of ["Content-Type", "Origin"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  const cookie = request.cookies.get(reviewsCookie);
  if (cookie) headers.set("Cookie", `${reviewsCookie}=${cookie.value}`);
  let upstream: Response;
  try {
    upstream = await fetch(address, {
      method: request.method,
      headers,
      body: request.method === "POST" ? await request.arrayBuffer() : undefined,
      redirect: "manual",
      cache: "no-store",
    });
  } catch {
    return new Response("Reviews API is unavailable", { status: 502 });
  }
  const responseHeaders = new Headers({ "Cache-Control": "private, no-store" });
  for (const name of ["Content-Type", "Location"]) {
    const value = upstream.headers.get(name);
    if (value) responseHeaders.set(name, value);
  }
  for (const value of upstream.headers.getSetCookie()) responseHeaders.append("Set-Cookie", value);
  return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
}

export { proxy as GET, proxy as HEAD, proxy as POST };
