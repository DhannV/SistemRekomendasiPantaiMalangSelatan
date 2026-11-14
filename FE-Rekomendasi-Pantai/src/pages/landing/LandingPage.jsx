import React from "react";
import HeroSearch from "./sections/HeroSearch";
import CaraKerja from "./sections/CaraKerja";
import StatistikData from "./sections/StatistikData";
import Footer from "../../components/footer";
import Navbar from "../../components/navbar";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-800">
      <Navbar />
      <HeroSearch />
      <StatistikData />
      <CaraKerja />

      {/* Footer Sederhana */}
      <Footer />
    </div>
  );
};

export default LandingPage;
