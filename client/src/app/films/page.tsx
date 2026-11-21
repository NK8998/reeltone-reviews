import "./page.css";
import Footer from "@/components/reusables/Footer/Footer";
import Navbar from "@/components/reusables/Navbar/Navbar";
import { getServerBackendService } from "@/services/serverBackendService";
import FilmsMainSection from "@/components/films/MainSection";

export default async function Films() {
  const backendService = await getServerBackendService();
  const data = await backendService.filmsData();

  return (
    <div className='films-page'>
      <Navbar />
      <div className='main-content'>
        <main className='films-main'>
          <FilmsMainSection data={data} />
        </main>
      </div>
      <Footer />
    </div>
  );
}
