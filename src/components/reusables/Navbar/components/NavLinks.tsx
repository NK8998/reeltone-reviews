import { useUser } from "@/context/AuthContext";
import Link from "next/link";

export default function NavLinks() {
  const { user } = useUser();

  return (
    <nav className='nav-middle nav-section'>
      {!user && (
        <>
          <a href="/auth/sign-in">SIGN IN</a>
          <a href="/auth/sign-up">CREATE ACCOUNT</a>
        </>
      )}
      <Link href={"/me"}>ME</Link>
      <Link href={"/films"}>FILMS</Link>
      <Link href={"/members/new"}>MEMBERS</Link>
    </nav>
  );
}
