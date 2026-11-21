"use client";

import { toast } from "sonner";
import { reviewsApi } from "@/lib/reviewsAuth";

export default function useSignOut() {
  const handleSignOut = async () => {
    try {
      const response = await fetch(`${reviewsApi}/auth/logout`, { method: "POST" });
      if (!response.ok) throw new Error("Sign-out failed");
      window.location.assign("/");
    } catch {
      toast.error("There was an error when signing out.");
    }
  };

  return { handleSignOut };
}
