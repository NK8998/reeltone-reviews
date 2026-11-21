import { redirect } from "next/navigation";
import { reviewsApi } from "@/lib/reviewsAuth";
import { currentUser } from "@/lib/serverBackend";

export default async function ProfilePage() {
  if (!await currentUser()) redirect("/auth/sign-in?next=/profile");
  redirect(`${reviewsApi}/auth/account`);
}
