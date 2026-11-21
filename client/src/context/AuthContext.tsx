"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { ReviewsUser } from "@/lib/reviewsAuth";

const AuthContext = createContext<ReviewsUser | null>(null);

export function AuthProvider({ user, children }: { user: ReviewsUser | null; children: ReactNode }) {
  return <AuthContext.Provider value={user}>{children}</AuthContext.Provider>;
}

export function useUser() {
  const user = useContext(AuthContext);
  return user ? { user, isSignedIn: true as const } : { user: null, isSignedIn: false as const };
}
