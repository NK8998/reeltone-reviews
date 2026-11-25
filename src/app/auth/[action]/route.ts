import { NextRequest } from "next/server";
import { reviewsApi } from "@/lib/reviewsAuth";

export async function GET(request: NextRequest, { params }: { params: Promise<{ action: string }> }) {
  const { action } = await params;
  if (action === "reset") return new Response(null, { status: 303, headers: { Location: `${reviewsApi}/auth/forgot-password` } });
  if (action !== "sign-in" && action !== "sign-up") return new Response("Not found", { status: 404 });
  const search = new URLSearchParams();
  const next = request.nextUrl.searchParams.get("next");
  if (next) search.set("next", next);
  if (action === "sign-up") search.set("mode", "signup");
  return new Response(null, { status: 303, headers: { Location: `${reviewsApi}/auth/login?${search}` } });
}
