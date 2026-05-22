bash

cat > /home/claude/kost-app/app.py << 'ENDOFFILE'
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
    background: #f8f9ff; border: 1px solid #e0e4f0;
    border-radius: 12px; padding: 20px; text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 800; font-family: 'Syne', sans-serif; color: #1a1a2e; }
.metric-label { font-size: 0.85rem; color: #666; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

DB_PATH = "kos_manajemen.db"

# ── Seed Data ─────────────────────────────────────────────────────────────────
SEED_PENYEWA = [['P001', 'Andi Saputra', 'Jl. Mawar No.12, Depok', '089124942603', '2024-01-13', '2024-07-01'], ['P002', 'Budi Santoso', 'Jl. Melati No.5, Bogor', '084139958838', '2024-03-12', '2024-06-02'], ['P003', 'Citra Dewi', 'Jl. Kenanga No.8, Bekasi', '089683197857', '2024-02-14', '2025-01-11'], ['P004', 'Dian Permata', 'Jl. Flamboyan No.3, Tangerang', '086414265799', '2024-01-16', '2024-04-02'], ['P005', 'Eko Prasetyo', 'Jl. Anggrek No.17, Jakarta Selatan', '083741227216', '2024-09-15', '2025-08-19'], ['P006', 'Fajar Nugroho', 'Jl. Cempaka No.22, Bandung', '081385329037', '2024-04-11', '2025-04-08'], ['P007', 'Gita Rahayu', 'Jl. Dahlia No.9, Sukabumi', '089983140807', '2024-08-02', '2024-12-22'], ['P008', 'Hendra Kusuma', 'Jl. Edelweis No.1, Cianjur', '086789089901', '2024-05-22', '2024-06-24'], ['P009', 'Indah Lestari', 'Jl. Bougenville No.14, Karawang', '083066722344', '2024-06-23', '2024-12-12'], ['P010', 'Joko Widodo', 'Jl. Tulip No.6, Purwakarta', '082938898923', '2024-06-21', '2024-09-11'], ['P011', 'Kartika Sari', 'Jl. Mawar No.12, Depok', '082160992979', '2024-02-19', '2024-09-19'], ['P012', 'Lukman Hakim', 'Jl. Melati No.5, Bogor', '085491030736', '2024-05-15', '2024-07-06'], ['P013', 'Maya Putri', 'Jl. Kenanga No.8, Bekasi', '086881971316', '2024-03-04', '2024-10-13'], ['P014', 'Nanda Rizki', 'Jl. Flamboyan No.3, Tangerang', '082084093639', '2024-05-30', '2025-05-16'], ['P015', 'Oktavia Wulan', 'Jl. Anggrek No.17, Jakarta Selatan', '088958537831', '2024-10-22', '2025-02-27'], ['P016', 'Pandu Setiawan', 'Jl. Cempaka No.22, Bandung', '081816150444', '2024-04-26', '2024-10-21'], ['P017', 'Qori Amaliah', 'Jl. Dahlia No.9, Sukabumi', '082041244663', '2024-02-21', '2024-10-02'], ['P018', 'Rudi Hartono', 'Jl. Edelweis No.1, Cianjur', '084570855700', '2024-07-05', '2024-10-26'], ['P019', 'Siti Aminah', 'Jl. Bougenville No.14, Karawang', '085757683626', '2024-04-17', '2024-09-30'], ['P020', 'Tono Basuki', 'Jl. Tulip No.6, Purwakarta', '089996977837', '2024-02-06', '2025-01-12'], ['P021', 'Umar Faruq', 'Jl. Mawar No.12, Depok', '089132969840', '2024-09-30', '2025-03-04'], ['P022', 'Vina Claudia', 'Jl. Melati No.5, Bogor', '083072043515', '2024-07-13', '2024-12-28'], ['P023', 'Wahyu Hidayat', 'Jl. Kenanga No.8, Bekasi', '089184752529', '2024-04-22', '2024-11-04'], ['P024', 'Xena Pratiwi', 'Jl. Flamboyan No.3, Tangerang', '081740742311', '2024-01-17', '2024-07-26'], ['P025', 'Yoga Firmansyah', 'Jl. Anggrek No.17, Jakarta Selatan', '086145935572', '2024-02-03', '2024-06-20'], ['P026', 'Zahra Nuraini', 'Jl. Cempaka No.22, Bandung', '088252235350', '2024-04-18', '2025-04-18'], ['P027', 'Agus Salim', 'Jl. Dahlia No.9, Sukabumi', '087363100814', '2024-08-22', '2024-12-03'], ['P028', 'Bella Anggraeni', 'Jl. Edelweis No.1, Cianjur', '084328740864', '2024-05-06', '2025-03-19'], ['P029', 'Cahyo Nugroho', 'Jl. Bougenville No.14, Karawang', '087845264581', '2024-10-26', '2025-07-02'], ['P030', 'Dewi Susanti', 'Jl. Tulip No.6, Purwakarta', '088463606628', '2024-07-04', '2024-11-23'], ['P031', 'Erlangga Putra', 'Jl. Mawar No.12, Depok', '082778387461', '2024-09-09', '2024-11-24'], ['P032', 'Fitri Handayani', 'Jl. Melati No.5, Bogor', '081624716857', '2024-03-19', '2025-03-05'], ['P033', 'Galih Saputra', 'Jl. Kenanga No.8, Bekasi', '083066661351', '2024-02-02', '2024-09-16'], ['P034', 'Hani Rahmawati', 'Jl. Flamboyan No.3, Tangerang', '085889978790', '2024-08-27', '2025-06-23'], ['P035', 'Imam Santoso', 'Jl. Anggrek No.17, Jakarta Selatan', '084284252722', '2024-01-06', '2024-04-03'], ['P036', 'Julia Permatasari', 'Jl. Cempaka No.22, Bandung', '089782070937', '2024-05-16', '2025-05-09'], ['P037', 'Kurnia Adi', 'Jl. Dahlia No.9, Sukabumi', '085324972279', '2024-05-30', '2025-02-06'], ['P038', 'Laila Nur', 'Jl. Edelweis No.1, Cianjur', '083070897765', '2024-01-02', '2024-06-14'], ['P039', 'Muhamad Rizal', 'Jl. Bougenville No.14, Karawang', '087433978249', '2024-09-16', '2024-12-09'], ['P040', 'Novita Sari', 'Jl. Tulip No.6, Purwakarta', '089050056581', '2024-09-16', '2025-08-23'], ['P041', 'Oscar Pratama', 'Jl. Mawar No.12, Depok', '083530513739', '2024-07-10', '2024-10-30'], ['P042', 'Putri Handayani', 'Jl. Melati No.5, Bogor', '087981182864', '2024-01-01', '2024-12-02'], ['P043', 'Qorry Nabilah', 'Jl. Kenanga No.8, Bekasi', '085175579548', '2024-01-10', '2024-04-06'], ['P044', 'Rafli Akbar', 'Jl. Flamboyan No.3, Tangerang', '085651273847', '2024-05-02', '2024-06-30'], ['P045', 'Shinta Dewi', 'Jl. Anggrek No.17, Jakarta Selatan', '084086149359', '2024-02-10', '2024-04-23'], ['P046', 'Tirta Wicaksono', 'Jl. Cempaka No.22, Bandung', '087219289546', '2024-09-29', '2025-01-01'], ['P047', 'Ulfa Mariana', 'Jl. Dahlia No.9, Sukabumi', '082698550256', '2024-08-31', '2025-07-08'], ['P048', 'Vicky Prasetya', 'Jl. Edelweis No.1, Cianjur', '083145575298', '2024-09-27', '2025-09-02'], ['P049', 'Widya Astuti', 'Jl. Bougenville No.14, Karawang', '086438427073', '2024-10-03', '2025-02-12'], ['P050', 'Yoga Dwi', 'Jl. Tulip No.6, Purwakarta', '084963551839', '2024-07-10', '2025-03-21']]
SEED_KAMAR = [['K001', '101', '900000', 'Tersedia'], ['K002', '102', '900000', 'Tersedia'], ['K003', '103', '900000', 'Tersedia'], ['K004', '104', '900000', 'Terisi'], ['K005', '105', '900000', 'Terisi'], ['K006', '106', '900000', 'Terisi'], ['K007', '107', '900000', 'Terisi'], ['K008', '108', '900000', 'Terisi'], ['K009', '109', '900000', 'Maintenance'], ['K010', '110', '900000', 'Tersedia'], ['K011', '201', '900000', 'Tersedia'], ['K012', '202', '900000', 'Tersedia'], ['K013', '203', '900000', 'Tersedia'], ['K014', '204', '900000', 'Terisi'], ['K015', '205', '900000', 'Terisi'], ['K016', '206', '900000', 'Terisi'], ['K017', '207', '900000', 'Terisi'], ['K018', '208', '900000', 'Terisi'], ['K019', '209', '900000', 'Maintenance'], ['K020', '210', '900000', 'Tersedia'], ['K021', '301', '900000', 'Tersedia'], ['K022', '302', '900000', 'Tersedia'], ['K023', '303', '900000', 'Tersedia'], ['K024', '304', '900000', 'Terisi'], ['K025', '305', '900000', 'Terisi'], ['K026', '306', '900000', 'Terisi'], ['K027', '307', '900000', 'Terisi'], ['K028', '308', '900000', 'Terisi'], ['K029', '309', '900000', 'Maintenance'], ['K030', '310', '900000', 'Tersedia'], ['K031', '401', '900000', 'Tersedia'], ['K032', '402', '900000', 'Tersedia'], ['K033', '403', '900000', 'Tersedia'], ['K034', '404', '900000', 'Terisi'], ['K035', '405', '900000', 'Terisi'], ['K036', '406', '900000', 'Terisi'], ['K037', '407', '900000', 'Terisi'], ['K038', '408', '900000', 'Terisi'], ['K039', '409', '900000', 'Maintenance'], ['K040', '410', '900000', 'Tersedia'], ['K041', '501', '900000', 'Tersedia'], ['K042', '502', '900000', 'Tersedia'], ['K043', '503', '900000', 'Tersedia'], ['K044', '504', '900000', 'Terisi'], ['K045', '505', '900000', 'Terisi'], ['K046', '506', '900000', 'Terisi'], ['K047', '507', '900000', 'Terisi'], ['K048', '508', '900000', 'Terisi'], ['K049', '509', '900000', 'Maintenance'], ['K050', '510', '900000', 'Tersedia'], ['K051', '601', '900000', 'Tersedia'], ['K052', '602', '900000', 'Tersedia'], ['K053', '603', '900000', 'Tersedia'], ['K054', '604', '900000', 'Terisi'], ['K055', '605', '900000', 'Terisi'], ['K056', '606', '900000', 'Terisi'], ['K057', '607', '900000', 'Terisi'], ['K058', '608', '900000', 'Terisi'], ['K059', '609', '900000', 'Maintenance'], ['K060', '610', '900000', 'Tersedia'], ['K061', '701', '900000', 'Tersedia'], ['K062', '702', '900000', 'Tersedia'], ['K063', '703', '900000', 'Tersedia'], ['K064', '704', '900000', 'Terisi'], ['K065', '705', '900000', 'Terisi'], ['K066', '706', '900000', 'Terisi'], ['K067', '707', '900000', 'Terisi'], ['K068', '708', '900000', 'Terisi'], ['K069', '709', '900000', 'Maintenance'], ['K070', '710', '900000', 'Tersedia']]
SEED_FASILITAS = [['F001', 'AC', '150000'], ['F002', 'TV', '100000'], ['F003', 'Dispenser', '75000'], ['F004', 'Kulkas', '125000']]
SEED_DETAIL_KAMAR = [['D0001', 'K001', 'F004'], ['D0002', 'K001', 'F003'], ['D0003', 'K002', 'F004'], ['D0004', 'K002', 'F003'], ['D0005', 'K003', 'F004'], ['D0006', 'K003', 'F003'], ['D0007', 'K004', 'F004'], ['D0008', 'K004', 'F003'], ['D0009', 'K005', 'F004'], ['D0010', 'K005', 'F003'], ['D0011', 'K006', 'F004'], ['D0012', 'K006', 'F003'], ['D0013', 'K007', 'F004'], ['D0014', 'K007', 'F003'], ['D0015', 'K008', 'F004'], ['D0016', 'K008', 'F003'], ['D0017', 'K009', 'F004'], ['D0018', 'K009', 'F003'], ['D0019', 'K010', 'F004'], ['D0020', 'K010', 'F003'], ['D0021', 'K011', 'F001'], ['D0022', 'K011', 'F004'], ['D0023', 'K011', 'F003'], ['D0024', 'K012', 'F001'], ['D0025', 'K012', 'F004'], ['D0026', 'K012', 'F003'], ['D0027', 'K013', 'F001'], ['D0028', 'K013', 'F004'], ['D0029', 'K013', 'F003'], ['D0030', 'K014', 'F001'], ['D0031', 'K014', 'F004'], ['D0032', 'K014', 'F003'], ['D0033', 'K015', 'F001'], ['D0034', 'K015', 'F004'], ['D0035', 'K015', 'F003'], ['D0036', 'K016', 'F001'], ['D0037', 'K016', 'F004'], ['D0038', 'K016', 'F003'], ['D0039', 'K017', 'F001'], ['D0040', 'K017', 'F004'], ['D0041', 'K017', 'F003'], ['D0042', 'K018', 'F001'], ['D0043', 'K018', 'F004'], ['D0044', 'K018', 'F003'], ['D0045', 'K019', 'F001'], ['D0046', 'K019', 'F004'], ['D0047', 'K019', 'F003'], ['D0048', 'K020', 'F001'], ['D0049', 'K020', 'F004'], ['D0050', 'K020', 'F003'], ['D0051', 'K021', 'F001'], ['D0052', 'K021', 'F002'], ['D0053', 'K021', 'F004'], ['D0054', 'K022', 'F001'], ['D0055', 'K022', 'F002'], ['D0056', 'K022', 'F004'], ['D0057', 'K023', 'F001'], ['D0058', 'K023', 'F002'], ['D0059', 'K023', 'F004'], ['D0060', 'K024', 'F001'], ['D0061', 'K024', 'F002'], ['D0062', 'K024', 'F004'], ['D0063', 'K025', 'F001'], ['D0064', 'K025', 'F002'], ['D0065', 'K025', 'F004'], ['D0066', 'K026', 'F001'], ['D0067', 'K026', 'F002'], ['D0068', 'K026', 'F004'], ['D0069', 'K027', 'F001'], ['D0070', 'K027', 'F002'], ['D0071', 'K027', 'F004'], ['D0072', 'K028', 'F001'], ['D0073', 'K028', 'F002'], ['D0074', 'K028', 'F004'], ['D0075', 'K029', 'F001'], ['D0076', 'K029', 'F002'], ['D0077', 'K029', 'F004'], ['D0078', 'K030', 'F001'], ['D0079', 'K030', 'F002'], ['D0080', 'K030', 'F004'], ['D0081', 'K031', 'F001'], ['D0082', 'K031', 'F002'], ['D0083', 'K031', 'F003'], ['D0084', 'K031', 'F004'], ['D0085', 'K032', 'F001'], ['D0086', 'K032', 'F002'], ['D0087', 'K032', 'F003'], ['D0088', 'K032', 'F004'], ['D0089', 'K033', 'F001'], ['D0090', 'K033', 'F002'], ['D0091', 'K033', 'F003'], ['D0092', 'K033', 'F004'], ['D0093', 'K034', 'F001'], ['D0094', 'K034', 'F002'], ['D0095', 'K034', 'F003'], ['D0096', 'K034', 'F004'], ['D0097', 'K035', 'F001'], ['D0098', 'K035', 'F002'], ['D0099', 'K035', 'F003'], ['D0100', 'K035', 'F004'], ['D0101', 'K036', 'F001'], ['D0102', 'K036', 'F002'], ['D0103', 'K036', 'F003'], ['D0104', 'K036', 'F004'], ['D0105', 'K037', 'F001'], ['D0106', 'K037', 'F002'], ['D0107', 'K037', 'F003'], ['D0108', 'K037', 'F004'], ['D0109', 'K038', 'F001'], ['D0110', 'K038', 'F002'], ['D0111', 'K038', 'F003'], ['D0112', 'K038', 'F004'], ['D0113', 'K039', 'F001'], ['D0114', 'K039', 'F002'], ['D0115', 'K039', 'F003'], ['D0116', 'K039', 'F004'], ['D0117', 'K040', 'F001'], ['D0118', 'K040', 'F002'], ['D0119', 'K040', 'F003'], ['D0120', 'K040', 'F004'], ['D0121', 'K041', 'F001'], ['D0122', 'K041', 'F002'], ['D0123', 'K041', 'F003'], ['D0124', 'K041', 'F004'], ['D0126', 'K042', 'F001'], ['D0127', 'K042', 'F002'], ['D0128', 'K042', 'F003'], ['D0129', 'K042', 'F004'], ['D0131', 'K043', 'F001'], ['D0132', 'K043', 'F002'], ['D0133', 'K043', 'F003'], ['D0134', 'K043', 'F004'], ['D0136', 'K044', 'F001'], ['D0137', 'K044', 'F002'], ['D0138', 'K044', 'F003'], ['D0139', 'K044', 'F004'], ['D0141', 'K045', 'F001'], ['D0142', 'K045', 'F002'], ['D0143', 'K045', 'F003'], ['D0144', 'K045', 'F004'], ['D0146', 'K046', 'F001'], ['D0147', 'K046', 'F002'], ['D0148', 'K046', 'F003'], ['D0149', 'K046', 'F004'], ['D0151', 'K047', 'F001'], ['D0152', 'K047', 'F002'], ['D0153', 'K047', 'F003'], ['D0154', 'K047', 'F004'], ['D0156', 'K048', 'F001'], ['D0157', 'K048', 'F002'], ['D0158', 'K048', 'F003'], ['D0159', 'K048', 'F004'], ['D0161', 'K049', 'F001'], ['D0162', 'K049', 'F002'], ['D0163', 'K049', 'F003'], ['D0164', 'K049', 'F004'], ['D0166', 'K050', 'F001'], ['D0167', 'K050', 'F002'], ['D0168', 'K050', 'F003'], ['D0169', 'K050', 'F004'], ['D0171', 'K051', 'F001'], ['D0172', 'K051', 'F002'], ['D0173', 'K051', 'F003'], ['D0174', 'K051', 'F004'], ['D0177', 'K052', 'F001'], ['D0178', 'K052', 'F002'], ['D0179', 'K052', 'F003'], ['D0180', 'K052', 'F004'], ['D0183', 'K053', 'F001'], ['D0184', 'K053', 'F002'], ['D0185', 'K053', 'F003'], ['D0186', 'K053', 'F004'], ['D0189', 'K054', 'F001'], ['D0190', 'K054', 'F002'], ['D0191', 'K054', 'F003'], ['D0192', 'K054', 'F004'], ['D0195', 'K055', 'F001'], ['D0196', 'K055', 'F002'], ['D0197', 'K055', 'F003'], ['D0198', 'K055', 'F004'], ['D0201', 'K056', 'F001'], ['D0202', 'K056', 'F002'], ['D0203', 'K056', 'F003'], ['D0204', 'K056', 'F004'], ['D0207', 'K057', 'F001'], ['D0208', 'K057', 'F002'], ['D0209', 'K057', 'F003'], ['D0210', 'K057', 'F004'], ['D0213', 'K058', 'F001'], ['D0214', 'K058', 'F002'], ['D0215', 'K058', 'F003'], ['D0216', 'K058', 'F004'], ['D0219', 'K059', 'F001'], ['D0220', 'K059', 'F002'], ['D0221', 'K059', 'F003'], ['D0222', 'K059', 'F004'], ['D0225', 'K060', 'F001'], ['D0226', 'K060', 'F002'], ['D0227', 'K060', 'F003'], ['D0228', 'K060', 'F004'], ['D0231', 'K061', 'F001'], ['D0232', 'K061', 'F002'], ['D0233', 'K061', 'F003'], ['D0234', 'K061', 'F004'], ['D0237', 'K062', 'F001'], ['D0238', 'K062', 'F002'], ['D0239', 'K062', 'F003'], ['D0240', 'K062', 'F004'], ['D0243', 'K063', 'F001'], ['D0244', 'K063', 'F002'], ['D0245', 'K063', 'F003'], ['D0246', 'K063', 'F004'], ['D0249', 'K064', 'F001'], ['D0250', 'K064', 'F002'], ['D0251', 'K064', 'F003'], ['D0252', 'K064', 'F004'], ['D0255', 'K065', 'F001'], ['D0256', 'K065', 'F002'], ['D0257', 'K065', 'F003'], ['D0258', 'K065', 'F004'], ['D0261', 'K066', 'F001'], ['D0262', 'K066', 'F002'], ['D0263', 'K066', 'F003'], ['D0264', 'K066', 'F004'], ['D0267', 'K067', 'F001'], ['D0268', 'K067', 'F002'], ['D0269', 'K067', 'F003'], ['D0270', 'K067', 'F004'], ['D0273', 'K068', 'F001'], ['D0274', 'K068', 'F002'], ['D0275', 'K068', 'F003'], ['D0276', 'K068', 'F004'], ['D0279', 'K069', 'F001'], ['D0280', 'K069', 'F002'], ['D0281', 'K069', 'F003'], ['D0282', 'K069', 'F004'], ['D0285', 'K070', 'F001'], ['D0286', 'K070', 'F002'], ['D0287', 'K070', 'F003'], ['D0288', 'K070', 'F004']]
SEED_PEMBAYARAN = [['PB001', 'P001', 'K004', '2024-11-04', '1100000', 'Lunas'], ['PB002', 'P001', 'K004', '2024-12-04', '1100000', 'Lunas'], ['PB003', 'P002', 'K005', '2024-12-09', '1100000', 'Lunas'], ['PB004', 'P003', 'K006', '2024-04-05', '1100000', 'Lunas'], ['PB005', 'P004', 'K007', '2024-11-24', '1100000', 'Lunas'], ['PB006', 'P004', 'K007', '2024-12-24', '1100000', 'Lunas'], ['PB007', 'P005', 'K008', '2024-10-14', '1100000', 'Lunas'], ['PB008', 'P006', 'K014', '2024-01-03', '1250000', 'Lunas'], ['PB009', 'P007', 'K015', '2024-04-17', '1250000', 'Lunas'], ['PB010', 'P007', 'K015', '2024-05-17', '1250000', 'Lunas'], ['PB011', 'P008', 'K016', '2024-09-07', '1250000', 'Belum Lunas'], ['PB012', 'P009', 'K017', '2024-04-15', '1250000', 'Lunas'], ['PB013', 'P010', 'K018', '2024-01-25', '1250000', 'Lunas'], ['PB014', 'P010', 'K018', '2024-02-25', '1250000', 'Lunas'], ['PB015', 'P011', 'K024', '2024-12-14', '1275000', 'Lunas'], ['PB016', 'P012', 'K025', '2024-05-05', '1275000', 'Lunas'], ['PB017', 'P013', 'K026', '2024-06-04', '1275000', 'Lunas'], ['PB018', 'P013', 'K026', '2024-07-04', '1275000', 'Lunas'], ['PB019', 'P014', 'K027', '2024-07-04', '1275000', 'Lunas'], ['PB020', 'P015', 'K028', '2024-06-20', '1275000', 'Lunas'], ['PB021', 'P016', 'K034', '2024-01-24', '1350000', 'Belum Lunas'], ['PB022', 'P016', 'K034', '2024-02-24', '1350000', 'Lunas'], ['PB023', 'P017', 'K035', '2024-09-04', '1350000', 'Belum Lunas'], ['PB024', 'P018', 'K036', '2024-02-18', '1350000', 'Lunas'], ['PB025', 'P019', 'K037', '2024-11-20', '1350000', 'Lunas'], ['PB026', 'P019', 'K037', '2024-12-20', '1350000', 'Lunas'], ['PB027', 'P020', 'K038', '2024-10-07', '1350000', 'Lunas'], ['PB028', 'P021', 'K044', '2024-01-22', '1350000', 'Lunas'], ['PB029', 'P022', 'K045', '2024-05-03', '1350000', 'Lunas'], ['PB030', 'P022', 'K045', '2024-06-03', '1350000', 'Lunas'], ['PB031', 'P023', 'K046', '2024-02-13', '1350000', 'Lunas'], ['PB032', 'P024', 'K047', '2024-08-21', '1350000', 'Lunas'], ['PB033', 'P025', 'K048', '2024-03-12', '1350000', 'Lunas'], ['PB034', 'P025', 'K048', '2024-04-12', '1350000', 'Lunas'], ['PB035', 'P026', 'K054', '2024-04-22', '1350000', 'Lunas'], ['PB036', 'P027', 'K055', '2024-12-22', '1350000', 'Lunas'], ['PB037', 'P028', 'K056', '2024-10-21', '1350000', 'Lunas'], ['PB038', 'P028', 'K056', '2024-11-21', '1350000', 'Lunas'], ['PB039', 'P029', 'K057', '2024-09-24', '1350000', 'Lunas'], ['PB040', 'P030', 'K058', '2024-03-15', '1350000', 'Belum Lunas'], ['PB041', 'P031', 'K064', '2024-05-21', '1350000', 'Lunas'], ['PB042', 'P031', 'K064', '2024-06-21', '1350000', 'Lunas'], ['PB043', 'P032', 'K065', '2024-11-11', '1350000', 'Lunas'], ['PB044', 'P033', 'K066', '2024-04-27', '1350000', 'Lunas'], ['PB045', 'P034', 'K067', '2024-06-13', '1350000', 'Lunas'], ['PB046', 'P034', 'K067', '2024-07-13', '1350000', 'Lunas'], ['PB047', 'P035', 'K068', '2024-02-07', '1350000', 'Lunas'], ['PB048', 'P036', 'K004', '2024-04-21', '1100000', 'Belum Lunas'], ['PB049', 'P037', 'K005', '2024-07-21', '1100000', 'Belum Lunas'], ['PB050', 'P037', 'K005', '2024-08-21', '1100000', 'Lunas'], ['PB051', 'P038', 'K006', '2024-03-09', '1100000', 'Lunas'], ['PB052', 'P039', 'K007', '2024-04-24', '1100000', 'Lunas'], ['PB053', 'P040', 'K008', '2024-12-19', '1100000', 'Belum Lunas'], ['PB054', 'P040', 'K008', '2024-12-19', '1100000', 'Lunas'], ['PB055', 'P041', 'K014', '2024-10-13', '1250000', 'Lunas'], ['PB056', 'P042', 'K015', '2024-04-05', '1250000', 'Belum Lunas'], ['PB057', 'P043', 'K016', '2024-02-25', '1250000', 'Lunas'], ['PB058', 'P043', 'K016', '2024-03-25', '1250000', 'Lunas'], ['PB059', 'P044', 'K017', '2024-02-05', '1250000', 'Lunas'], ['PB060', 'P045', 'K018', '2024-11-14', '1250000', 'Lunas'], ['PB061', 'P046', 'K024', '2024-07-13', '1275000', 'Belum Lunas'], ['PB062', 'P046', 'K024', '2024-08-13', '1275000', 'Lunas'], ['PB063', 'P047', 'K025', '2024-09-09', '1275000', 'Lunas'], ['PB064', 'P048', 'K026', '2024-11-24', '1275000', 'Lunas'], ['PB065', 'P049', 'K027', '2024-11-18', '1275000', 'Lunas'], ['PB066', 'P049', 'K027', '2024-12-18', '1275000', 'Lunas'], ['PB067', 'P050', 'K028', '2024-11-11', '1275000', 'Lunas']]

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS penyewa (
            id_penyewa TEXT PRIMARY KEY, nama TEXT NOT NULL,
            alamat TEXT, no_hp TEXT, tgl_masuk TEXT, tgl_keluar TEXT);
        CREATE TABLE IF NOT EXISTS kamar (
            id_kamar TEXT PRIMARY KEY, no_kamar TEXT NOT NULL,
            harga_dasar INTEGER, status TEXT);
        CREATE TABLE IF NOT EXISTS fasilitas (
            id_fasilitas TEXT PRIMARY KEY, nama_fasilitas TEXT, harga_tambahan INTEGER);
        CREATE TABLE IF NOT EXISTS detail_kamar (
            id_detail TEXT PRIMARY KEY, id_kamar TEXT, id_fasilitas TEXT);
        CREATE TABLE IF NOT EXISTS pembayaran (
            id_pembayaran TEXT PRIMARY KEY, id_penyewa TEXT, id_kamar TEXT,
            tgl_bayar TEXT, jumlah_bayar INTEGER, status_bayar TEXT);
    ''')
    # Seed data jika tabel masih kosong
    if conn.execute("SELECT COUNT(*) FROM penyewa").fetchone()[0] == 0:
        conn.executemany("INSERT OR IGNORE INTO penyewa VALUES (?,?,?,?,?,?)", SEED_PENYEWA)
        conn.executemany("INSERT OR IGNORE INTO kamar VALUES (?,?,?,?)", SEED_KAMAR)
        conn.executemany("INSERT OR IGNORE INTO fasilitas VALUES (?,?,?)", SEED_FASILITAS)
        conn.executemany("INSERT OR IGNORE INTO detail_kamar VALUES (?,?,?)", SEED_DETAIL_KAMAR)
        conn.executemany("INSERT OR IGNORE INTO pembayaran VALUES (?,?,?,?,?,?)", SEED_PEMBAYARAN)
    conn.commit()
    conn.close()

init_db()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏠 KostManager")
    st.markdown("---")
    menu = st.radio("Navigasi", [
        "📊 Dashboard", "👤 Penyewa", "💳 Pembayaran",
        "🔍 Cari Penyewa", "📋 Lihat Data", "📈 Analisis",
    ], label_visibility="collapsed")

page = menu.split(" ", 1)[1]

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
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{total_penyewa}</div><div class="metric-label">Total Penyewa</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{total_kamar}</div><div class="metric-label">Total Kamar</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{kamar_tersedia}</div><div class="metric-label">Kamar Tersedia</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#e53e3e">{belum_lunas}</div><div class="metric-label">Belum Lunas</div></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#276749;font-size:1.3rem">Rp{total_pemasukan:,.0f}</div><div class="metric-label">Total Pemasukan</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Status Kamar")
        df = pd.read_sql("SELECT status, COUNT(*) as jumlah FROM kamar GROUP BY status", conn)
        st.bar_chart(df.set_index("status"))
    with col2:
        st.subheader("Pemasukan per Bulan")
        df = pd.read_sql("SELECT strftime('%Y-%m', tgl_bayar) AS bulan, SUM(jumlah_bayar) AS total FROM pembayaran WHERE status_bayar='Lunas' GROUP BY bulan ORDER BY bulan", conn)
        if not df.empty: st.bar_chart(df.set_index("bulan"))
        else: st.info("Belum ada data pembayaran lunas.")
    conn.close()

elif page == "Penyewa":
    st.title("Manajemen Penyewa")
    tab1, tab2 = st.tabs(["➕ Tambah Penyewa", "🗑️ Hapus Penyewa"])

    with tab1:
        with st.form("form_penyewa"):
            c1, c2 = st.columns(2)
            with c1:
                id_penyewa = st.text_input("ID Penyewa", placeholder="P051")
                nama       = st.text_input("Nama")
                alamat     = st.text_input("Alamat")
            with c2:
                no_hp      = st.text_input("No HP")
                tgl_masuk  = st.date_input("Tanggal Masuk", value=datetime.today())
                tgl_keluar = tgl_masuk + timedelta(days=30)
                st.text_input("Tanggal Keluar (otomatis +30 hari)", value=str(tgl_keluar), disabled=True)
            submitted = st.form_submit_button("💾 Simpan Penyewa", use_container_width=True)
            if submitted:
                if not id_penyewa or not nama:
                    st.error("ID Penyewa dan Nama wajib diisi!")
                else:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT OR IGNORE INTO penyewa VALUES (?,?,?,?,?,?)",
                            (id_penyewa, nama, alamat, no_hp, str(tgl_masuk), str(tgl_keluar)))
                        conn.commit(); conn.close()
                        st.success(f"✅ Penyewa **{nama}** berhasil ditambahkan!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        conn = get_conn()
        st.dataframe(pd.read_sql("SELECT * FROM penyewa", conn), use_container_width=True)
        conn.close()

    with tab2:
        conn = get_conn()
        df_p = pd.read_sql("SELECT id_penyewa, nama FROM penyewa", conn); conn.close()
        options = [f"{r['nama']} ({r['id_penyewa']})" for _, r in df_p.iterrows()]
        pilih   = st.selectbox("Pilih Penyewa", options)
        id_hapus = df_p.iloc[options.index(pilih)]["id_penyewa"]
        st.warning(f"⚠️ Yakin ingin menghapus **{pilih}**?")
        if st.button("🗑️ Hapus Penyewa", type="primary"):
            conn = get_conn()
            conn.execute("DELETE FROM penyewa WHERE id_penyewa=?", (id_hapus,))
            conn.commit(); conn.close()
            st.success("Penyewa berhasil dihapus!"); st.rerun()

elif page == "Pembayaran":
    st.title("Manajemen Pembayaran")
    tab1, tab2 = st.tabs(["➕ Tambah Pembayaran", "✅ Update Status"])

    conn = get_conn()
    penyewa_df   = pd.read_sql("SELECT * FROM penyewa", conn)
    kamar_df     = pd.read_sql("SELECT * FROM kamar", conn)
    fasilitas_df = pd.read_sql("SELECT * FROM fasilitas", conn)
    conn.close()

    with tab1:
        with st.form("form_bayar"):
            c1, c2 = st.columns(2)
            with c1:
                id_bayar = st.text_input("ID Pembayaran", placeholder="PB068")
                penyewa_opts = [f"{r['nama']} ({r['id_penyewa']})" for _, r in penyewa_df.iterrows()]
                pilih_p      = st.selectbox("Penyewa", penyewa_opts)
                id_penyewa_val = penyewa_df.iloc[penyewa_opts.index(pilih_p)]["id_penyewa"]
            with c2:
                kamar_opts = [f"Kamar {r['no_kamar']} — Rp{int(r['harga_dasar']):,}" for _, r in kamar_df.iterrows()]
                pilih_k    = st.selectbox("Kamar", kamar_opts)
                id_kamar_val = kamar_df.iloc[kamar_opts.index(pilih_k)]["id_kamar"]
                harga_kamar  = int(kamar_df.iloc[kamar_opts.index(pilih_k)]["harga_dasar"])

            st.markdown("**Fasilitas Tambahan:**")
            fas_cols = st.columns(4)
            fas_selected = []
            for i, (_, row) in enumerate(fasilitas_df.iterrows()):
                with fas_cols[i % 4]:
                    if st.checkbox(f"{row['nama_fasilitas']} (+Rp{int(row['harga_tambahan']):,})", key=f"fas_{i}"):
                        fas_selected.append(row)

            tgl_bayar    = st.date_input("Tanggal Bayar", value=datetime.today())
            status_bayar = st.selectbox("Status", ["Lunas", "Belum Lunas"])
            harga_fas    = sum(int(r["harga_tambahan"]) for r in fas_selected)
            total        = harga_kamar + harga_fas
            st.info(f"💰 **Total Bayar: Rp{total:,}**")

            if st.form_submit_button("💾 Simpan Pembayaran", use_container_width=True):
                if not id_bayar:
                    st.error("ID Pembayaran wajib diisi!")
                else:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT OR IGNORE INTO pembayaran VALUES (?,?,?,?,?,?)",
                            (id_bayar, id_penyewa_val, id_kamar_val, str(tgl_bayar), total, status_bayar))
                        for r in fas_selected:
                            conn.execute("INSERT OR IGNORE INTO detail_kamar VALUES (?,?,?)",
                                (f"DK{id_kamar_val}{r['id_fasilitas']}", id_kamar_val, r["id_fasilitas"]))
                        conn.commit(); conn.close()
                        st.success(f"✅ Pembayaran **{id_bayar}** disimpan! Total: Rp{total:,}")
                    except Exception as e:
                        st.error(f"Error: {e}")

        conn = get_conn()
        st.dataframe(pd.read_sql("SELECT * FROM pembayaran", conn), use_container_width=True)
        conn.close()

    with tab2:
        conn = get_conn()
        df_tagihan = pd.read_sql("""
            SELECT pb.id_pembayaran, p.nama, pb.jumlah_bayar, pb.status_bayar
            FROM pembayaran pb JOIN penyewa p ON pb.id_penyewa = p.id_penyewa
            WHERE pb.status_bayar = 'Belum Lunas'
        """, conn); conn.close()
        if df_tagihan.empty:
            st.success("🎉 Semua pembayaran sudah lunas!")
        else:
            st.dataframe(df_tagihan, use_container_width=True)
            opts  = [f"{r['nama']} — {r['id_pembayaran']} — Rp{int(r['jumlah_bayar']):,}" for _, r in df_tagihan.iterrows()]
            pilih = st.selectbox("Pilih tagihan:", opts)
            id_tagihan = df_tagihan.iloc[opts.index(pilih)]["id_pembayaran"]
            if st.button("✅ Tandai Lunas", type="primary"):
                conn = get_conn()
                conn.execute("UPDATE pembayaran SET status_bayar='Lunas' WHERE id_pembayaran=?", (id_tagihan,))
                conn.commit(); conn.close()
                st.success(f"Pembayaran {id_tagihan} berhasil diperbarui!"); st.rerun()

elif page == "Cari Penyewa":
    st.title("Cari Penyewa")
    kata = st.text_input("Masukkan nama atau ID penyewa", placeholder="contoh: Budi atau P001")
    if kata:
        conn = get_conn()
        df = pd.read_sql("SELECT * FROM penyewa WHERE nama LIKE ? OR id_penyewa LIKE ?",
            conn, params=(f"%{kata}%", f"%{kata}%"))
        st.info(f"{len(df)} data ditemukan")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            if len(df) == 1:
                df_pay = pd.read_sql("SELECT * FROM pembayaran WHERE id_penyewa=?",
                    conn, params=(df.iloc[0]["id_penyewa"],))
                if not df_pay.empty:
                    st.markdown("#### Riwayat Pembayaran")
                    st.dataframe(df_pay, use_container_width=True)
        conn.close()

elif page == "Lihat Data":
    st.title("Lihat Data")
    tabel = st.selectbox("Pilih Tabel", ["penyewa", "kamar", "fasilitas", "detail_kamar", "pembayaran"])
    filter_val = None
    if tabel == "kamar":
        filter_val = st.selectbox("Filter Status", ["Semua", "Tersedia", "Terisi", "Maintenance"])
    elif tabel == "pembayaran":
        filter_val = st.selectbox("Filter Status", ["Semua", "Lunas", "Belum Lunas"])
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

elif page == "Analisis":
    st.title("Analisis")
    conn = get_conn()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Status Kamar")
        df = pd.read_sql("SELECT status, COUNT(*) AS jumlah FROM kamar GROUP BY status", conn)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("status"))
    with col2:
        st.subheader("Penyewa Belum Lunas")
        df = pd.read_sql("""
            SELECT p.nama, pb.id_pembayaran, pb.tgl_bayar, pb.jumlah_bayar
            FROM pembayaran pb JOIN penyewa p ON pb.id_penyewa = p.id_penyewa
            WHERE pb.status_bayar = 'Belum Lunas'
        """, conn)
        if not df.empty: st.dataframe(df, use_container_width=True)
        else: st.success("Tidak ada tunggakan! 🎉")

    st.subheader("Total Pemasukan per Bulan")
    df = pd.read_sql("""
        SELECT strftime('%Y-%m', tgl_bayar) AS bulan, SUM(jumlah_bayar) AS total
        FROM pembayaran WHERE status_bayar = 'Lunas'
        GROUP BY bulan ORDER BY bulan
    """, conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("bulan"))

    st.subheader("Fasilitas per Kamar")
    df = pd.read_sql("""
        SELECT k.no_kamar, f.nama_fasilitas, f.harga_tambahan
        FROM detail_kamar dk
        JOIN kamar k ON dk.id_kamar = k.id_kamar
        JOIN fasilitas f ON dk.id_fasilitas = f.id_fasilitas
        ORDER BY k.no_kamar
    """, conn)
    if not df.empty: st.dataframe(df, use_container_width=True)
    conn.close()
ENDOFFILE
echo "Done"

ini udah selesai belum app.py nya
