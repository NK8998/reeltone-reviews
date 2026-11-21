import "./page.css";
import Footer from "@/components/reusables/Footer/Footer";
import Navbar from "@/components/reusables/Navbar/Navbar";
import { getServerBackendService } from "@/services/serverBackendService";
import MainContent from "@/components/landing/MainContent";

export default async function Landing() {
  const backendService = await getServerBackendService();
  const landingData = await backendService.landingData().catch(() => null);
  return (
    <div className='landing-page'>
      <Navbar />
      <main className='landing-main'>
        {landingData ? <MainContent landingData={landingData} loading={false} /> : (
          <div className="p-8">
            <p>Movie data is temporarily unavailable.</p>
            <a href="/members">Browse community members</a>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
