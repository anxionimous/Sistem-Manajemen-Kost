import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="KostManager", page_icon="🏠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #0f0f14 !important;
}

[data-testid="stSidebar"] * {
    color: #e0e0f0 !important;
}

.metric-card {
    background: #f8f9ff;
    border: 1px solid #e0e4f0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'Syne', sans-serif;
    color: #1a1a2e;
}

.metric-label {
    font-size: 0.85rem;
    color: #666;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

DB_PATH = "kos_manajemen.db"

# =========================
# DATABASE
# =========================

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS penyewa (
        id_penyewa TEXT PRIMARY KEY,
        nama TEXT NOT NULL,
        alamat TEXT,
        no_hp TEXT,
        tgl_masuk TEXT,
        tgl_keluar TEXT
    );

    CREATE TABLE IF NOT EXISTS kamar (
        id_kamar TEXT PRIMARY KEY,
        no_kamar TEXT NOT NULL,
        harga_dasar INTEGER,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS fasilitas (
        id_fasilitas TEXT PRIMARY KEY,
        nama_fasilitas TEXT,
        harga_tambahan INTEGER
    );

    CREATE TABLE IF NOT EXISTS detail_kamar (
        id_detail TEXT PRIMARY KEY,
        id_kamar TEXT,
        id_fasilitas TEXT
    );

    CREATE TABLE IF NOT EXISTS pembayaran (
        id_pembayaran TEXT PRIMARY KEY,
        id_penyewa TEXT,
        id_kamar TEXT,
        tgl_bayar TEXT,
        jumlah_bayar INTEGER,
        status_bayar TEXT
    );
    """)

    # =========================
    # SEED DATA SEDERHANA
    # =========================

    if conn.execute("SELECT COUNT(*) FROM kamar").fetchone()[0] == 0:

        kamar_seed = [
            ("K001", "101", 900000, "Tersedia"),
            ("K002", "102", 900000, "Terisi"),
            ("K003", "103", 1200000, "Tersedia"),
            ("K004", "104", 1500000, "Maintenance")
        ]

        fasilitas_seed = [
            ("F001", "AC", 150000),
            ("F002", "TV", 100000),
            ("F003", "WiFi", 50000),
            ("F004", "Kulkas", 125000)
        ]

        conn.executemany(
            "INSERT INTO kamar VALUES (?,?,?,?)",
            kamar_seed
        )

        conn.executemany(
            "INSERT INTO fasilitas VALUES (?,?,?)",
            fasilitas_seed
        )

    conn.commit()
    conn.close()

init_db()

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.markdown("## 🏠 KostManager")
    st.markdown("---")

    menu = st.radio(
        "Navigasi",
        [
            "📊 Dashboard",
            "👤 Penyewa",
            "💳 Pembayaran",
            "🔍 Cari Penyewa",
            "📋 Lihat Data",
            "📈 Analisis",
        ],
        label_visibility="collapsed"
    )

page = menu.split(" ", 1)[1]

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("Dashboard")

    conn = get_conn()

    total_penyewa = pd.read_sql(
        "SELECT COUNT(*) as n FROM penyewa",
        conn
    ).iloc[0, 0]

    total_kamar = pd.read_sql(
        "SELECT COUNT(*) as n FROM kamar",
        conn
    ).iloc[0, 0]

    kamar_tersedia = pd.read_sql(
        "SELECT COUNT(*) as n FROM kamar WHERE status='Tersedia'",
        conn
    ).iloc[0, 0]

    belum_lunas = pd.read_sql(
        "SELECT COUNT(*) as n FROM pembayaran WHERE status_bayar='Belum Lunas'",
        conn
    ).iloc[0, 0]

    total_pemasukan = pd.read_sql(
        """
        SELECT COALESCE(SUM(jumlah_bayar),0) as n
        FROM pembayaran
        WHERE status_bayar='Lunas'
        """,
        conn
    ).iloc[0, 0]

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{total_penyewa}</div>
                <div class="metric-label">Total Penyewa</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{total_kamar}</div>
                <div class="metric-label">Total Kamar</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{kamar_tersedia}</div>
                <div class="metric-label">Kamar Tersedia</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#e53e3e">
                    {belum_lunas}
                </div>
                <div class="metric-label">Belum Lunas</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#276749;font-size:1.3rem">
                    Rp{total_pemasukan:,.0f}
                </div>
                <div class="metric-label">Total Pemasukan</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    conn.close()

# =========================================================
# PENYEWA
# =========================================================

elif page == "Penyewa":

    st.title("Manajemen Penyewa")

    tab1, tab2 = st.tabs([
        "➕ Tambah Penyewa",
        "🗑️ Hapus Penyewa"
    ])

    # =====================================================
    # TAMBAH PENYEWA
    # =====================================================

    with tab1:

        conn = get_conn()

        kamar_df = pd.read_sql(
            "SELECT * FROM kamar",
            conn
        )

        fasilitas_df = pd.read_sql(
            "SELECT * FROM fasilitas",
            conn
        )

        conn.close()

        with st.form("form_penyewa"):

            st.markdown("#### Data Penyewa")

            c1, c2 = st.columns(2)

            with c1:

                id_penyewa = st.text_input(
                    "ID Penyewa",
                    placeholder="P001"
                )

                nama = st.text_input("Nama")

                alamat = st.text_input("Alamat")

            with c2:

                no_hp = st.text_input("No HP")

                tgl_masuk = st.date_input(
                    "Tanggal Masuk",
                    value=datetime.today()
                )

                tgl_keluar = tgl_masuk + timedelta(days=30)

                st.text_input(
                    "Tanggal Keluar (+30 hari)",
                    value=str(tgl_keluar),
                    disabled=True
                )

            st.markdown("---")

            st.markdown("#### Kamar & Pembayaran Awal")

            c3, c4 = st.columns(2)

            with c3:

                kamar_opts = [
                    f"Kamar {r['no_kamar']} — Rp{int(r['harga_dasar']):,}"
                    for _, r in kamar_df.iterrows()
                ]

                pilih_k = st.selectbox(
                    "Pilih Kamar",
                    kamar_opts
                )

                id_kamar_val = kamar_df.iloc[
                    kamar_opts.index(pilih_k)
                ]["id_kamar"]

                harga_kamar = int(
                    kamar_df.iloc[
                        kamar_opts.index(pilih_k)
                    ]["harga_dasar"]
                )

            with c4:

                id_bayar_awal = st.text_input(
                    "ID Pembayaran Awal",
                    placeholder="PB001"
                )

                # =============================
                # FITUR BARU STATUS PEMBAYARAN
                # =============================

                status_bayar_awal = st.selectbox(
                    "Status Pembayaran Awal",
                    ["Belum Lunas", "Lunas"]
                )

            st.markdown("### Fasilitas Tambahan")

            fas_cols = st.columns(4)

            fas_selected = []

            for i, (_, row) in enumerate(fasilitas_df.iterrows()):

                with fas_cols[i % 4]:

                    if st.checkbox(
                        f"{row['nama_fasilitas']} (+Rp{int(row['harga_tambahan']):,})",
                        key=f"fas_{i}"
                    ):
                        fas_selected.append(row)

            harga_fas = sum(
                int(r["harga_tambahan"])
                for r in fas_selected
            )

            total = harga_kamar + harga_fas

            st.info(
                f"""
                💰 Total Tagihan Awal: Rp{total:,}

                Status: {status_bayar_awal}
                """
            )

            submitted = st.form_submit_button(
                "💾 Simpan Penyewa",
                use_container_width=True
            )

            if submitted:

                if not id_penyewa or not nama:

                    st.error(
                        "ID Penyewa dan Nama wajib diisi!"
                    )

                elif not id_bayar_awal:

                    st.error(
                        "ID Pembayaran wajib diisi!"
                    )

                else:

                    try:

                        conn = get_conn()

                        # =============================
                        # SIMPAN PENYEWA
                        # =============================

                        conn.execute(
                            """
                            INSERT OR IGNORE INTO penyewa
                            VALUES (?,?,?,?,?,?)
                            """,
                            (
                                id_penyewa,
                                nama,
                                alamat,
                                no_hp,
                                str(tgl_masuk),
                                str(tgl_keluar)
                            )
                        )

                        # =============================
                        # SIMPAN PEMBAYARAN
                        # =============================

                        conn.execute(
                            """
                            INSERT OR IGNORE INTO pembayaran
                            VALUES (?,?,?,?,?,?)
                            """,
                            (
                                id_bayar_awal,
                                id_penyewa,
                                id_kamar_val,
                                str(tgl_masuk),
                                total,
                                status_bayar_awal
                            )
                        )

                        # =============================
                        # DETAIL FASILITAS
                        # =============================

                        for r in fas_selected:

                            detail_id = (
                                f"DK{id_kamar_val}{r['id_fasilitas']}"
                            )

                            conn.execute(
                                """
                                INSERT OR IGNORE INTO detail_kamar
                                VALUES (?,?,?)
                                """,
                                (
                                    detail_id,
                                    id_kamar_val,
                                    r["id_fasilitas"]
                                )
                            )

                        conn.commit()
                        conn.close()

                        st.success(
                            f"""
                            ✅ Penyewa {nama} berhasil ditambahkan!

                            💳 Pembayaran awal berhasil dibuat
                            dengan status:
                            {status_bayar_awal}

                            💰 Total:
                            Rp{total:,}
                            """
                        )

                    except Exception as e:

                        st.error(f"Error: {e}")

        # =============================
        # TAMPILKAN DATA
        # =============================

        conn = get_conn()

        df = pd.read_sql(
            "SELECT * FROM penyewa",
            conn
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        conn.close()

    # =====================================================
    # HAPUS PENYEWA
    # =====================================================

    with tab2:

        conn = get_conn()

        df_p = pd.read_sql(
            "SELECT id_penyewa, nama FROM penyewa",
            conn
        )

        conn.close()

        options = [
            f"{r['nama']} ({r['id_penyewa']})"
            for _, r in df_p.iterrows()
        ]

        if len(options) > 0:

            pilih = st.selectbox(
                "Pilih Penyewa",
                options
            )

            id_hapus = df_p.iloc[
                options.index(pilih)
            ]["id_penyewa"]

            st.warning(
                f"⚠️ Yakin ingin menghapus {pilih}?"
            )

            if st.button(
                "🗑️ Hapus Penyewa",
                type="primary"
            ):

                conn = get_conn()

                conn.execute(
                    "DELETE FROM penyewa WHERE id_penyewa=?",
                    (id_hapus,)
                )

                conn.commit()
                conn.close()

                st.success(
                    "Penyewa berhasil dihapus!"
                )

                st.rerun()

# =========================================================
# PEMBAYARAN
# =========================================================

elif page == "Pembayaran":

    st.title("Manajemen Pembayaran")

    conn = get_conn()

    df = pd.read_sql(
        "SELECT * FROM pembayaran",
        conn
    )

    conn.close()

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================================================
# CARI PENYEWA
# =========================================================

elif page == "Cari Penyewa":

    st.title("Cari Penyewa")

    kata = st.text_input(
        "Masukkan nama atau ID penyewa"
    )

    if kata:

        conn = get_conn()

        df = pd.read_sql(
            """
            SELECT * FROM penyewa
            WHERE nama LIKE ?
            OR id_penyewa LIKE ?
            """,
            conn,
            params=(f"%{kata}%", f"%{kata}%")
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        conn.close()

# =========================================================
# LIHAT DATA
# =========================================================

elif page == "Lihat Data":

    st.title("Lihat Data")

    tabel = st.selectbox(
        "Pilih Tabel",
        [
            "penyewa",
            "kamar",
            "fasilitas",
            "detail_kamar",
            "pembayaran"
        ]
    )

    conn = get_conn()

    df = pd.read_sql(
        f"SELECT * FROM {tabel}",
        conn
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    conn.close()

# =========================================================
# ANALISIS
# =========================================================

elif page == "Analisis":

    st.title("Analisis")

    conn = get_conn()

    st.subheader("Status Kamar")

    df = pd.read_sql(
        """
        SELECT status, COUNT(*) AS jumlah
        FROM kamar
        GROUP BY status
        """,
        conn
    )

    st.dataframe(df)
    st.bar_chart(df.set_index("status"))

    conn.close()
