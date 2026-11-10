const API_URL = (
  import.meta.env.VITE_API_URL ||
  "https://sistemrekomendasipantaimalangselatan.onrender.com"
).replace(/\/$/, "");

export async function simpanRiwayatPencarian(keyword, resultCount = 0) {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    console.warn("Token tidak ditemukan. Silakan login kembali.");
    return null;
  }

  const response = await fetch(`${API_URL}/search-history`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      keyword: keyword.trim(),
      result_count: resultCount,
    }),
  });

  const hasil = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      typeof hasil.detail === "string"
        ? hasil.detail
        : "Gagal menyimpan riwayat pencarian.",
    );
  }

  return hasil;
}

export async function ambilSemuaRiwayatPencarian() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Sesi login tidak ditemukan. Silakan login kembali.");
  }

  const response = await fetch(`${API_URL}/search-history/admin`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Gagal mengambil riwayat pencarian.",
    );
  }

  return data;
}

export async function ambilKataKunciPopuler() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Sesi login tidak ditemukan. Silakan login kembali.");
  }

  const response = await fetch(
    `${API_URL}/search-history/admin/popular-keywords`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Gagal mengambil kata kunci populer.",
    );
  }

  return data;
}
