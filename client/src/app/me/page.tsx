import { redirect } from "next/navigation";
import "./page.css";
import Footer from "@/components/reusables/Footer/Footer";
import Navbar from "@/components/reusables/Navbar/Navbar";
import { getServerBackendService } from "@/services/serverBackendService";
import MainContent from "@/components/me/MainContent";
import { currentUser } from "@/lib/serverBackend";

export default async function Me() {
  const backendService = await getServerBackendService();
  const user = await currentUser();
  if (!user) redirect("/auth/sign-in?next=/me");

  const data = await backendService.meData();

  return (
    <div className='me-page'>
      <Navbar />
      <main className='main-content'>
        <MainContent data={data} />
      </main>
      <Footer />
    </div>
  );
}
