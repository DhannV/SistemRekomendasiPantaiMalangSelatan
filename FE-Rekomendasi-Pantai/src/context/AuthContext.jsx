
import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import { apiRequest } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadUser() {
      const token = sessionStorage.getItem("access_token");

      if (!token) {
        if (active) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        const data = await apiRequest("/auth/me");

        // Backend mengembalikan data user secara langsung.
        if (active) {
          setUser(data.user ?? data);
        }
      } catch (error) {
        if (active) {
          sessionStorage.removeItem("access_token");
          setUser(null);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      active = false;
    };
  }, []);

  async function login(username, password) {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    });

    if (!data.access_token) {
      throw new Error("Token login tidak ditemukan dari backend.");
    }

    // Simpan token sebelum meminta profil user.
    sessionStorage.setItem("access_token", data.access_token);

    try {
      const profile = await apiRequest("/auth/me");

      setUser(profile.user ?? profile);

      return {
        ...data,
        user: profile.user ?? profile,
      };
    } catch (error) {
      sessionStorage.removeItem("access_token");
      setUser(null);
      throw error;
    }
  }

  async function register(username, password) {
    return apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    });
  }

  function logout() {
    sessionStorage.removeItem("access_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth harus digunakan di dalam AuthProvider."
    );
  }

  return context;
}
