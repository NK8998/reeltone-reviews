import { cache } from "react";
import { cookies } from "next/headers";
import { reviewsCookie, type ReviewsUser } from "./reviewsAuth";

export function getBackendUrl() {
  return (process.env.REVIEWS_BACKEND_URL || "http://127.0.0.1:5000").replace(/\/$/, "");
}

export async function sessionHeaders(): Promise<Record<string, string>> {
  const cookie = (await cookies()).get(reviewsCookie);
  return cookie ? { Cookie: `${reviewsCookie}=${cookie.value}` } : {};
}

export const currentUser = cache(async (): Promise<ReviewsUser | null> => {
  const headers = await sessionHeaders();
  if (!headers.Cookie) return null;
  try {
    const response = await fetch(`${getBackendUrl()}/auth/session`, { headers, cache: "no-store" });
    if (!response.ok) return null;
    const { user } = await response.json() as { user: ReviewsUser | null };
    return user;
  } catch {
    return null;
  }
});
