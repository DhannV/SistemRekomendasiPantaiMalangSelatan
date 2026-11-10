import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const navigate = useNavigate();

  const greeting = `Hello, ${user?.username || "User"}!`;
  const [typedGreeting, setTypedGreeting] = useState("");

  useEffect(() => {
    if (!user) {
      setTypedGreeting("");
      return;
    }

    let index = 0;
    let isDeleting = false;
    let timeout;

    const typeSpeed = 80;
    const deleteSpeed = 45;
    const pauseAfterTyping = 1000;

    setTypedGreeting("");

    function animateTyping() {
      if (!isDeleting) {
        // Mengetik dari kiri ke kanan
        index++;
        setTypedGreeting(greeting.slice(0, index));

        if (index >= greeting.length) {
          // Tunggu 20 detik setelah selesai mengetik
          timeout = setTimeout(() => {
            isDeleting = true;
            animateTyping();
          }, pauseAfterTyping);
          return;
        }

        timeout = setTimeout(animateTyping, typeSpeed);
      } else {
        // Menghapus teks seperti menekan backspace
        index--;
        setTypedGreeting(greeting.slice(0, index));

        if (index <= 0) {
          isDeleting = false;
          timeout = setTimeout(animateTyping, 500);
          return;
        }

        timeout = setTimeout(animateTyping, deleteSpeed);
      }
    }

    timeout = setTimeout(animateTyping, typeSpeed);

    return () => clearTimeout(timeout);
  }, [greeting, user]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/");
    } catch (error) {
      console.error("Gagal logout:", error);
    }
  };

  return (
    <nav className="relative z-20 w-full px-4 pt-4 sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl items-center justify-between rounded-2xl border border-white/70 bg-white/65 px-5 py-3 shadow-lg shadow-sky-900/5 backdrop-blur-xl sm:px-7">
        {/* Bagian kiri */}
        <div className="flex min-h-10 items-center gap-3">
          {!loading &&
            (user ? (
              <span className="font-semibold tracking-wide text-sky-800">
                {typedGreeting}
                <span className="ml-0.5 animate-pulse text-sky-500">|</span>
              </span>
            ) : (
              <>
                <Link
                  to="/login"
                  className="rounded-xl px-4 py-2 font-medium text-slate-700 transition hover:bg-sky-50 hover:text-sky-700"
                >
                  Login
                </Link>

                <Link
                  to="/register"
                  className="rounded-xl bg-sky-600 px-4 py-2 font-semibold text-white shadow-md shadow-sky-600/20 transition hover:bg-sky-700"
                >
                  Register
                </Link>
              </>
            ))}
        </div>

        {/* Bagian kanan */}
        <div className="flex items-center">
          {!loading && user && (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 rounded-xl border border-red-100 bg-red-50 px-4 py-2 font-semibold text-red-600 transition hover:border-red-200 hover:bg-red-100"
            >
              <LogOut size={17} />
              <span>Logout</span>
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
