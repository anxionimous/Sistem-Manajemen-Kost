import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="KostManager", page_icon="🏠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
[data-testid="stSidebar"] { background: #0f0f14 !important; }
[data-testid="stSidebar"] * { color: #e0e0f0 !important; }
.metric-card {
    background: #f8f9ff;
    border: 1px solid #e0e4f0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 800; font-family: 'Syne', sans-serif; color: #1a1a2e; }
.metric-label { font-size: 0.85rem; color: #666; margin-top: 4px; }
.stButton > button {
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

DB_PATH = "kos_manajemen.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.executescript('''
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
    ''')
    conn.commit()
    conn.close()

init_db()

# ── Sidebar Navigation ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏠 KostManager")
    st.markdown("---")
    menu = st.radio("Navigasi", [
        "📊 Dashboard",
        "👤 Penyewa",
        "💳 Pembayaran",
        "🔍 Cari Penyewa",
        "📋 Lihat Data",
        "📈 Analisis",
    ], label_visibility="collapsed")

page = menu.split(" ", 1)[1]

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.title("Dashboard")
    conn = get_conn()

    total_penyewa   = pd.read_sql("SELECT COUNT(*) as n FROM penyewa", conn).iloc[0,0]
    total_kamar     = pd.read_sql("SELECT COUNT(*) as n FROM kamar", conn).iloc[0,0]
    kamar_tersedia  = pd.read_sql("SELECT COUNT(*) as n FROM kamar WHERE status='Tersedia'", conn).iloc[0,0]
    belum_lunas     = pd.read_sql("SELECT COUNT(*) as n FROM pembayaran WHERE status_bayar='Belum Lunas'", conn).iloc[0,0]
    total_pemasukan = pd.read_sql("SELECT COALESCE(SUM(jumlah_bayar),0) as n FROM pembayaran WHERE status_bayar='Lunas'", conn).iloc[0,0]

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_penyewa}</div><div class="metric-label">Total Penyewa</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_kamar}</div><div class="metric-label">Total Kamar</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{kamar_tersedia}</div><div class="metric-label">Kamar Tersedia</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#e53e3e">{belum_lunas}</div><div class="metric-label">Belum Lunas</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#276749">Rp{total_pemasukan:,.0f}</div><div class="metric-label">Total Pemasukan</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Status Kamar")
        df_status = pd.read_sql("SELECT status, COUNT(*) as jumlah FROM kamar GROUP BY status", conn)
        if not df_status.empty:
            st.bar_chart(df_status.set_index("status"))
        else:
            st.info("Belum ada data kamar.")

    with col2:
        st.subheader("Pemasukan per Bulan")
        df_bulan = pd.read_sql("""
            SELECT strftime('%Y-%m', tgl_bayar) AS bulan, SUM(jumlah_bayar) AS total
            FROM pembayaran WHERE status_bayar='Lunas'
            GROUP BY bulan ORDER BY bulan
        """, conn)
        if not df_bulan.empty:
            st.bar_chart(df_bulan.set_index("bulan"))
        else:
            st.info("Belum ada data pembayaran lunas.")

    conn.close()

# ══════════════════════════════════════════════════════════════════════════════
# PENYEWA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Penyewa":
    st.title("Manajemen Penyewa")
    tab1, tab2 = st.tabs(["➕ Tambah Penyewa", "🗑️ Hapus Penyewa"])

    with tab1:
        with st.form("form_penyewa"):
            c1, c2 = st.columns(2)
            with c1:
                id_penyewa = st.text_input("ID Penyewa", placeholder="P001")
                nama       = st.text_input("Nama")
                alamat     = st.text_input("Alamat")
            with c2:
                no_hp      = st.text_input("No HP")
                tgl_masuk  = st.date_input("Tanggal Masuk", value=datetime.today())
                tgl_keluar = tgl_masuk + timedelta(days=30)
                st.text_input("Tanggal Keluar (otomatis)", value=str(tgl_keluar), disabled=True)

            submitted = st.form_submit_button("💾 Simpan Penyewa", use_container_width=True)
            if submitted:
                if not id_penyewa or not nama:
                    st.error("ID Penyewa dan Nama wajib diisi!")
                else:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT OR IGNORE INTO penyewa VALUES (?,?,?,?,?,?)",
                            (id_penyewa, nama, alamat, no_hp, str(tgl_masuk), str(tgl_keluar)))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Penyewa **{nama}** berhasil ditambahkan!")
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown("#### Data Penyewa")
        conn = get_conn()
        st.dataframe(pd.read_sql("SELECT * FROM penyewa", conn), use_container_width=True)
        conn.close()

    with tab2:
        conn = get_conn()
        df_p = pd.read_sql("SELECT id_penyewa, nama FROM penyewa", conn)
        conn.close()
        if df_p.empty:
            st.info("Belum ada data penyewa.")
        else:
            options = [f"{r['nama']} ({r['id_penyewa']})" for _, r in df_p.iterrows()]
            pilih   = st.selectbox("Pilih Penyewa", options)
            idx     = options.index(pilih)
            id_hapus = df_p.iloc[idx]["id_penyewa"]

            st.warning(f"⚠️ Yakin ingin menghapus **{pilih}**? Data pembayaran terkait tidak ikut terhapus.")
            if st.button("🗑️ Hapus Penyewa", type="primary"):
                conn = get_conn()
                conn.execute("DELETE FROM penyewa WHERE id_penyewa=?", (id_hapus,))
                conn.commit()
                conn.close()
                st.success("Penyewa berhasil dihapus!")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PEMBAYARAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Pembayaran":
    st.title("Manajemen Pembayaran")
    tab1, tab2 = st.tabs(["➕ Tambah Pembayaran", "✅ Update Status"])

    conn = get_conn()
    penyewa_df   = pd.read_sql("SELECT * FROM penyewa", conn)
    kamar_df     = pd.read_sql("SELECT * FROM kamar", conn)
    fasilitas_df = pd.read_sql("SELECT * FROM fasilitas", conn)
    conn.close()

    with tab1:
        if penyewa_df.empty or kamar_df.empty:
            st.warning("Tambahkan data penyewa dan kamar terlebih dahulu.")
        else:
            with st.form("form_bayar"):
                c1, c2 = st.columns(2)
                with c1:
                    id_bayar   = st.text_input("ID Pembayaran", placeholder="PB001")
                    penyewa_opts = [f"{r['nama']} ({r['id_penyewa']})" for _, r in penyewa_df.iterrows()]
                    pilih_p      = st.selectbox("Penyewa", penyewa_opts)
                    id_penyewa_val = penyewa_df.iloc[penyewa_opts.index(pilih_p)]["id_penyewa"]

                with c2:
                    kamar_opts = [f"Kamar {r['no_kamar']} — Rp{int(r['harga_dasar']):,}" for _, r in kamar_df.iterrows()]
                    pilih_k    = st.selectbox("Kamar", kamar_opts)
                    id_kamar_val   = kamar_df.iloc[kamar_opts.index(pilih_k)]["id_kamar"]
                    harga_kamar    = int(kamar_df.iloc[kamar_opts.index(pilih_k)]["harga_dasar"])

                if not fasilitas_df.empty:
                    st.markdown("**Fasilitas Tambahan:**")
                    fas_cols = st.columns(min(3, len(fasilitas_df)))
                    fas_selected = []
                    for i, (_, row) in enumerate(fasilitas_df.iterrows()):
                        with fas_cols[i % 3]:
                            if st.checkbox(f"{row['nama_fasilitas']} (+Rp{int(row['harga_tambahan']):,})", key=f"fas_{i}"):
                                fas_selected.append(row)

                tgl_bayar  = st.date_input("Tanggal Bayar", value=datetime.today())
                status_bayar = st.selectbox("Status", ["Lunas", "Belum Lunas"])

                harga_fas  = sum(int(r["harga_tambahan"]) for r in fas_selected) if not fasilitas_df.empty else 0
                total      = harga_kamar + harga_fas
                st.info(f"💰 **Total Bayar: Rp{total:,}**")

                submitted = st.form_submit_button("💾 Simpan Pembayaran", use_container_width=True)
                if submitted:
                    if not id_bayar:
                        st.error("ID Pembayaran wajib diisi!")
                    else:
                        try:
                            conn = get_conn()
                            conn.execute("INSERT OR IGNORE INTO pembayaran VALUES (?,?,?,?,?,?)",
                                (id_bayar, id_penyewa_val, id_kamar_val, str(tgl_bayar), total, status_bayar))
                            for r in fas_selected:
                                id_det = f"DK{id_kamar_val}{r['id_fasilitas']}"
                                conn.execute("INSERT OR IGNORE INTO detail_kamar VALUES (?,?,?)",
                                    (id_det, id_kamar_val, r["id_fasilitas"]))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ Pembayaran **{id_bayar}** berhasil disimpan! Total: Rp{total:,}")
                        except Exception as e:
                            st.error(f"Error: {e}")

        st.markdown("#### Data Pembayaran")
        conn = get_conn()
        st.dataframe(pd.read_sql("SELECT * FROM pembayaran", conn), use_container_width=True)
        conn.close()

    with tab2:
        conn = get_conn()
        df_tagihan = pd.read_sql("""
            SELECT pb.id_pembayaran, p.nama, pb.jumlah_bayar, pb.status_bayar
            FROM pembayaran pb JOIN penyewa p ON pb.id_penyewa = p.id_penyewa
            WHERE pb.status_bayar = 'Belum Lunas'
        """, conn)
        conn.close()

        if df_tagihan.empty:
            st.success("🎉 Semua pembayaran sudah lunas!")
        else:
            st.dataframe(df_tagihan, use_container_width=True)
            opts = [f"{r['nama']} — {r['id_pembayaran']} — Rp{int(r['jumlah_bayar']):,}" for _, r in df_tagihan.iterrows()]
            pilih = st.selectbox("Pilih tagihan:", opts)
            id_tagihan = df_tagihan.iloc[opts.index(pilih)]["id_pembayaran"]

            if st.button("✅ Tandai Lunas", type="primary"):
                conn = get_conn()
                conn.execute("UPDATE pembayaran SET status_bayar='Lunas' WHERE id_pembayaran=?", (id_tagihan,))
                conn.commit()
                conn.close()
                st.success(f"Pembayaran {id_tagihan} berhasil diperbarui!")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CARI PENYEWA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Cari Penyewa":
    st.title("Cari Penyewa")
    kata = st.text_input("Masukkan nama atau ID penyewa", placeholder="contoh: Budi atau P001")
    if kata:
        conn = get_conn()
        df = pd.read_sql(
            "SELECT * FROM penyewa WHERE nama LIKE ? OR id_penyewa LIKE ?",
            conn, params=(f"%{kata}%", f"%{kata}%"))
        conn.close()
        st.info(f"{len(df)} data ditemukan")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            # Tampilkan riwayat pembayaran
            if len(df) == 1:
                id_p = df.iloc[0]["id_penyewa"]
                conn = get_conn()
                df_pay = pd.read_sql("SELECT * FROM pembayaran WHERE id_penyewa=?", conn, params=(id_p,))
                conn.close()
                if not df_pay.empty:
                    st.markdown("#### Riwayat Pembayaran")
                    st.dataframe(df_pay, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# LIHAT DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Lihat Data":
    st.title("Lihat Data")
    tabel = st.selectbox("Pilih Tabel", ["penyewa", "kamar", "fasilitas", "detail_kamar", "pembayaran"])

    filter_val = None
    if tabel == "kamar":
        filter_val = st.selectbox("Filter Status", ["Semua", "Tersedia", "Terisi", "Maintenance"])
    elif tabel == "pembayaran":
        filter_val = st.selectbox("Filter Status Bayar", ["Semua", "Lunas", "Belum Lunas"])

    conn = get_conn()
    if tabel == "kamar" and filter_val and filter_val != "Semua":
        df = pd.read_sql("SELECT * FROM kamar WHERE status=?", conn, params=(filter_val,))
    elif tabel == "pembayaran" and filter_val and filter_val != "Semua":
        df = pd.read_sql("SELECT * FROM pembayaran WHERE status_bayar=?", conn, params=(filter_val,))
    else:
        df = pd.read_sql(f"SELECT * FROM {tabel}", conn)
    conn.close()

    st.info(f"{len(df)} data ditemukan")
    st.dataframe(df, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ANALISIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Analisis":
    st.title("Analisis")
    conn = get_conn()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Status Kamar")
        df = pd.read_sql("SELECT status, COUNT(*) AS jumlah FROM kamar GROUP BY status", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("status"))
        else:
            st.info("Belum ada data kamar.")

    with col2:
        st.subheader("Penyewa Belum Lunas")
        df = pd.read_sql("""
            SELECT p.nama, pb.id_pembayaran, pb.tgl_bayar, pb.jumlah_bayar
            FROM pembayaran pb JOIN penyewa p ON pb.id_penyewa = p.id_penyewa
            WHERE pb.status_bayar = 'Belum Lunas'
        """, conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.success("Tidak ada tunggakan! 🎉")

    st.subheader("Total Pemasukan per Bulan")
    df = pd.read_sql("""
        SELECT strftime('%Y-%m', tgl_bayar) AS bulan, SUM(jumlah_bayar) AS total
        FROM pembayaran WHERE status_bayar = 'Lunas'
        GROUP BY bulan ORDER BY bulan
    """, conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("bulan"))
    else:
        st.info("Belum ada pembayaran lunas.")

    st.subheader("Fasilitas per Kamar")
    df = pd.read_sql("""
        SELECT k.no_kamar, f.nama_fasilitas, f.harga_tambahan
        FROM detail_kamar dk
        JOIN kamar k ON dk.id_kamar = k.id_kamar
        JOIN fasilitas f ON dk.id_fasilitas = f.id_fasilitas
        ORDER BY k.no_kamar
    """, conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data fasilitas kamar.")

    conn.close()
