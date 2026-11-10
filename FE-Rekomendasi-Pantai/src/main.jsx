import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import LandingPage from "./pages/landing/LandingPage";
import SearchResult from "./pages/search/SearchResult";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import AdminDashboard from "./pages/admin/AdminDashboard";
import EvaluasiPage from "./pages/admin/evaluasi/EvaluasiPage";
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Halaman umum */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/hasil" element={<SearchResult />} />

          {/* Halaman autentikasi */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Khusus pengguna yang sudah login sebagai admin */}
          <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/evaluasi" element={<EvaluasiPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
