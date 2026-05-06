"""Reference constants — channels, topics, regions, classifications, requestor types, targets."""

CURRENT_PERIOD_LABEL = "Mei 2026"
CURRENT_YEAR = 2026
CURRENT_MONTH = 5

SXI_TARGET = 84.0
SSI_TARGET = 83.0

# 5-dimension satisfaction model: (key, label, target_t2b%, icon)
INDICES = [
    ("overall",  "Kepuasan Overall",  86.0, "💬"),
    ("effort",   "Customer Effort",   78.0, "👤"),
    ("trust",    "Trust",             88.0, "🛡"),
    ("loyalty",  "Loyalty",           82.0, "❤"),
    ("advokasi", "Advokasi",          76.0, "📣"),
]

# Demografi
AGE_BRACKETS = [
    ("18-25 tahun", 0.22),
    ("26-35 tahun", 0.36),
    ("36-45 tahun", 0.26),
    (">45 tahun",   0.16),
]
GENDERS = [("Perempuan", 0.51), ("Laki-laki", 0.49)]

# Matches Jun 2025 benchmark donut (Media Komunikasi)
CHANNELS = [
    ("Email", 0.3324),
    ("Telepon", 0.2799),
    ("Media Sosial", 0.2207),
    ("Livechat", 0.1068),
    ("Lainnya", 0.0440),
    ("Visitor Center", 0.0162),
]

# 7 Hot topics from benchmark + Lainnya bucket
TOPICS = [
    ("Seputar Uang Rupiah", 0.1417),
    ("Informasi Terkait Dompet Elektronik", 0.0713),
    ("Informasi terkait BIFAST", 0.0653),
    ("Informasi terkait SIMODIS", 0.0561),
    ("Informasi terkait BI-RTGS", 0.0497),
    ("PKL/Magang", 0.0460),
    ("Pengadaan", 0.0390),
    ("Lainnya", 0.5309),
]

# Klasifikasi Informasi (UU 14/2008) — from Jun 2025
CLASSIFICATIONS = [
    ("Setiap Saat", 0.7170),
    ("Berkala", 0.2779),
    ("Dikecualikan", 0.0047),
    ("Serta Merta", 0.0004),
]

# Kategori Pemohon — from Jun 2025
REQUESTORS = [
    ("Masyarakat Umum", 0.3571),
    ("Perbankan", 0.1620),
    ("Lainnya", 0.1362),
    ("Akademisi", 0.1007),
    ("Nasabah Bank", 0.0942),
    ("Kalangan Dunia Usaha", 0.0598),
    ("Pemerintah", 0.0500),
    ("Media", 0.0400),
]

# Indonesian provinces (subset for choropleth — uses ISO codes via plotly)
PROVINCES = [
    "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "Jawa Timur", "Banten",
    "DI Yogyakarta", "Bali", "Sumatera Utara", "Sumatera Barat", "Sumatera Selatan",
    "Riau", "Lampung", "Kalimantan Timur", "Kalimantan Selatan", "Kalimantan Barat",
    "Sulawesi Selatan", "Sulawesi Utara", "Sulawesi Tengah", "Aceh", "Kepulauan Riau",
    "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Papua", "Maluku", "Bengkulu",
    "Jambi",
]

# Wilayah Koordinasi: 5 regional groupings of provinces
WILAYAH = {
    "Jawa": ["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "Jawa Timur", "Banten", "DI Yogyakarta"],
    "Sumatera": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Sumatera Selatan", "Riau", "Lampung", "Bengkulu", "Jambi", "Kepulauan Riau"],
    "Kalimantan": ["Kalimantan Timur", "Kalimantan Selatan", "Kalimantan Barat"],
    "Sulawesi, Maluku, Papua": ["Sulawesi Selatan", "Sulawesi Utara", "Sulawesi Tengah", "Maluku", "Papua"],
    "Bali, Nusa Tenggara": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"],
}
PROVINCE_TO_WILAYAH = {p: w for w, ps in WILAYAH.items() for p in ps}
WILAYAH_NAMES = list(WILAYAH.keys())

# Social platforms for SSI
PLATFORMS = [
    ("X (Twitter)", 0.35),
    ("Instagram", 0.25),
    ("Facebook", 0.15),
    ("TikTok", 0.10),
    ("Berita Online", 0.10),
    ("YouTube", 0.05),
]

SENTIMENT_DIST = {
    "Positif": 0.78,
    "Netral": 0.19,
    "Negatif": 0.03,
}

# Months in Bahasa
MONTH_ID = [
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
]
MONTH_ID_FULL = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

# Status tiket
STATUSES = [
    ("Dikabulkan", 0.985),
    ("Dikecualikan", 0.012),
    ("Ditolak", 0.003),
]

REJECTION_REASONS = [
    "Termasuk informasi dikecualikan",
    "Data belum tersedia",
    "Bukan kewenangan BI",
    "Permohonan tidak lengkap",
    "Duplikasi permohonan",
]
