const API_URL = (
  import.meta.env.VITE_API_URL || "https://sistemrekomendasipantaimalangselatan.onrender.com"
).replace(/\/$/, "");

export async function ambilRekomendasi(query, topN = 5) {
  const response = await fetch(`${API_URL}/pantai/rekomendasi`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      top_n: topN,
    }),
  });

  const hasil = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof hasil.detail === "string"
        ? hasil.detail
        : "Gagal mengambil rekomendasi pantai.",
    );
  }

  return hasil;
}

// Mengambil koordinat seluruh pantai dari backend
export async function ambilKoordinatPantai() {
  const response = await fetch(`${API_URL}/pantai/koordinat`);

  const hasil = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof hasil.detail === "string"
        ? hasil.detail
        : "Gagal mengambil koordinat pantai.",
    );
  }

  return hasil.data || [];
}
