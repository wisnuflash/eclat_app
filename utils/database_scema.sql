-- ============================================
-- SISTEM MANAJEMEN OBAT DAN TRANSAKSI APOTEK
-- ============================================

-- Tabel Master Kategori Obat
CREATE TABLE kategori_obat (
    id_kategori INT PRIMARY KEY AUTO_INCREMENT,
    nama_kategori VARCHAR(100) NOT NULL,
    deskripsi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabel Master Bentuk Sediaan
CREATE TABLE bentuk_sediaan (
    id_bentuk INT PRIMARY KEY AUTO_INCREMENT,
    nama_bentuk VARCHAR(50) NOT NULL, -- Tablet, Kapsul, Sirup, dll
    deskripsi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Master Supplier/Distributor
CREATE TABLE supplier (
    id_supplier INT PRIMARY KEY AUTO_INCREMENT,
    kode_supplier VARCHAR(20) UNIQUE NOT NULL,
    nama_supplier VARCHAR(200) NOT NULL,
    alamat TEXT,
    telepon VARCHAR(20),
    email VARCHAR(100),
    pic_name VARCHAR(100), -- Person In Charge
    pic_phone VARCHAR(20),
    status ENUM('aktif', 'non_aktif') DEFAULT 'aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabel Master Obat
CREATE TABLE obat (
    id_obat INT PRIMARY KEY AUTO_INCREMENT,
    kode_obat VARCHAR(50) UNIQUE NOT NULL,
    nama_obat VARCHAR(200) NOT NULL,
    nama_generik VARCHAR(200),
    id_kategori INT,
    id_bentuk INT,
    kandungan TEXT, -- Komposisi obat
    dosis VARCHAR(100), -- 500mg, 250mg/5ml, dll
    kemasan VARCHAR(100), -- Strip, Botol, Box, dll
    isi_kemasan INT, -- Jumlah per kemasan
    satuan VARCHAR(20), -- Tablet, Kapsul, ml, dll
    golongan ENUM('bebas', 'bebas_terbatas', 'keras', 'narkotika', 'psikotropika'),
    harga_beli DECIMAL(15,2) DEFAULT 0,
    harga_jual DECIMAL(15,2) DEFAULT 0,
    margin_persen DECIMAL(5,2) DEFAULT 0,
    keterangan TEXT,
    status ENUM('aktif', 'non_aktif') DEFAULT 'aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_kategori) REFERENCES kategori_obat(id_kategori),
    FOREIGN KEY (id_bentuk) REFERENCES bentuk_sediaan(id_bentuk)
);

-- Tabel Stok Obat
CREATE TABLE stok_obat (
    id_stok INT PRIMARY KEY AUTO_INCREMENT,
    id_obat INT NOT NULL,
    batch_number VARCHAR(50),
    tanggal_produksi DATE,
    tanggal_kadaluwarsa DATE NOT NULL,
    stok_awal INT DEFAULT 0,
    stok_masuk INT DEFAULT 0,
    stok_keluar INT DEFAULT 0,
    stok_akhir INT DEFAULT 0,
    lokasi_simpan VARCHAR(100), -- Rak A1, Kulkas, dll
    id_supplier INT,
    status ENUM('normal', 'hampir_kadaluwarsa', 'kadaluwarsa', 'rusak') DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_obat) REFERENCES obat(id_obat),
    FOREIGN KEY (id_supplier) REFERENCES supplier(id_supplier)
);

-- Tabel Pembelian/Purchase Order
CREATE TABLE pembelian (
    id_pembelian INT PRIMARY KEY AUTO_INCREMENT,
    no_po VARCHAR(50) UNIQUE NOT NULL,
    id_supplier INT NOT NULL,
    tanggal_po DATE NOT NULL,
    tanggal_kirim DATE,
    status ENUM('pending', 'diproses', 'dikirim', 'diterima', 'dibatalkan') DEFAULT 'pending',
    total_item INT DEFAULT 0,
    total_harga DECIMAL(15,2) DEFAULT 0,
    diskon DECIMAL(15,2) DEFAULT 0,
    ppn DECIMAL(15,2) DEFAULT 0,
    total_bayar DECIMAL(15,2) DEFAULT 0,
    keterangan TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_supplier) REFERENCES supplier(id_supplier)
);

-- Tabel Detail Pembelian
CREATE TABLE detail_pembelian (
    id_detail_pembelian INT PRIMARY KEY AUTO_INCREMENT,
    id_pembelian INT NOT NULL,
    id_obat INT NOT NULL,
    batch_number VARCHAR(50),
    tanggal_kadaluwarsa DATE,
    qty_pesan INT NOT NULL,
    qty_terima INT DEFAULT 0,
    harga_satuan DECIMAL(15,2) NOT NULL,
    diskon_persen DECIMAL(5,2) DEFAULT 0,
    diskon_nilai DECIMAL(15,2) DEFAULT 0,
    subtotal DECIMAL(15,2) NOT NULL,
    keterangan TEXT,
    FOREIGN KEY (id_pembelian) REFERENCES pembelian(id_pembelian),
    FOREIGN KEY (id_obat) REFERENCES obat(id_obat)
);

-- Tabel Dokter (untuk resep)
CREATE TABLE dokter (
    id_dokter INT PRIMARY KEY AUTO_INCREMENT,
    kode_dokter VARCHAR(20) UNIQUE NOT NULL,
    nama_dokter VARCHAR(200) NOT NULL,
    spesialisasi VARCHAR(100),
    no_sip VARCHAR(50), -- Surat Izin Praktik
    telepon VARCHAR(20),
    alamat TEXT,
    status ENUM('aktif', 'non_aktif') DEFAULT 'aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Pasien/Customer
CREATE TABLE customer (
    id_customer INT PRIMARY KEY AUTO_INCREMENT,
    kode_customer VARCHAR(20) UNIQUE,
    nama_customer VARCHAR(200) NOT NULL,
    jenis_kelamin ENUM('L', 'P'),
    tanggal_lahir DATE,
    alamat TEXT,
    telepon VARCHAR(20),
    email VARCHAR(100),
    no_ktp VARCHAR(20),
    no_bpjs VARCHAR(20),
    alergi_obat TEXT, -- Riwayat alergi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabel Transaksi Penjualan
CREATE TABLE transaksi (
    id_transaksi INT PRIMARY KEY AUTO_INCREMENT,
    no_transaksi VARCHAR(50) UNIQUE NOT NULL,
    tanggal_transaksi DATETIME NOT NULL,
    jenis_transaksi ENUM('resep', 'bebas', 'konsinyasi') NOT NULL,
    id_customer INT,
    id_dokter INT, -- Untuk transaksi resep
    no_resep VARCHAR(50), -- Nomor resep dari dokter
    total_item INT DEFAULT 0,
    total_harga DECIMAL(15,2) DEFAULT 0,
    diskon DECIMAL(15,2) DEFAULT 0,
    total_bayar DECIMAL(15,2) DEFAULT 0,
    bayar_tunai DECIMAL(15,2) DEFAULT 0,
    bayar_non_tunai DECIMAL(15,2) DEFAULT 0,
    kembalian DECIMAL(15,2) DEFAULT 0,
    metode_bayar ENUM('tunai', 'debit', 'kredit', 'transfer', 'bpjs', 'asuransi') DEFAULT 'tunai',
    status ENUM('pending', 'selesai', 'dibatalkan') DEFAULT 'pending',
    keterangan TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_customer) REFERENCES customer(id_customer),
    FOREIGN KEY (id_dokter) REFERENCES dokter(id_dokter)
);

-- Tabel Detail Transaksi
CREATE TABLE detail_transaksi (
    id_detail_transaksi INT PRIMARY KEY AUTO_INCREMENT,
    id_transaksi INT NOT NULL,
    id_obat INT NOT NULL,
    id_stok INT NOT NULL, -- Untuk tracking batch
    qty INT NOT NULL,
    harga_satuan DECIMAL(15,2) NOT NULL,
    diskon_persen DECIMAL(5,2) DEFAULT 0,
    diskon_nilai DECIMAL(15,2) DEFAULT 0,
    subtotal DECIMAL(15,2) NOT NULL,
    aturan_pakai TEXT, -- Untuk obat resep
    keterangan TEXT,
    FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi),
    FOREIGN KEY (id_obat) REFERENCES obat(id_obat),
    FOREIGN KEY (id_stok) REFERENCES stok_obat(id_stok)
);

-- Tabel Retur Penjualan
CREATE TABLE retur_penjualan (
    id_retur INT PRIMARY KEY AUTO_INCREMENT,
    no_retur VARCHAR(50) UNIQUE NOT NULL,
    id_transaksi INT NOT NULL,
    tanggal_retur DATE NOT NULL,
    alasan_retur TEXT NOT NULL,
    total_retur DECIMAL(15,2) DEFAULT 0,
    status ENUM('pending', 'disetujui', 'ditolak') DEFAULT 'pending',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi)
);

-- Tabel Detail Retur Penjualan
CREATE TABLE detail_retur_penjualan (
    id_detail_retur INT PRIMARY KEY AUTO_INCREMENT,
    id_retur INT NOT NULL,
    id_detail_transaksi INT NOT NULL,
    qty_retur INT NOT NULL,
    harga_satuan DECIMAL(15,2) NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL,
    kondisi_obat ENUM('baik', 'rusak', 'kadaluwarsa') DEFAULT 'baik',
    FOREIGN KEY (id_retur) REFERENCES retur_penjualan(id_retur),
    FOREIGN KEY (id_detail_transaksi) REFERENCES detail_transaksi(id_detail_transaksi)
);

-- Tabel Mutasi Stok (Stock Movement)
CREATE TABLE mutasi_stok (
    id_mutasi INT PRIMARY KEY AUTO_INCREMENT,
    id_obat INT NOT NULL,
    id_stok INT NOT NULL,
    jenis_mutasi ENUM('masuk', 'keluar', 'adjustment', 'transfer', 'expired', 'rusak') NOT NULL,
    referensi_id INT, -- ID dari tabel referensi (pembelian, transaksi, dll)
    referensi_tipe VARCHAR(50), -- 'pembelian', 'penjualan', 'adjustment', dll
    qty_before INT NOT NULL,
    qty_mutasi INT NOT NULL,
    qty_after INT NOT NULL,
    harga_satuan DECIMAL(15,2),
    keterangan TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_obat) REFERENCES obat(id_obat),
    FOREIGN KEY (id_stok) REFERENCES stok_obat(id_stok)
);

-- Tabel Users/Karyawan
CREATE TABLE users (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    telepon VARCHAR(20),
    role ENUM('admin', 'apoteker', 'asisten_apoteker', 'kasir', 'owner') NOT NULL,
    status ENUM('aktif', 'non_aktif') DEFAULT 'aktif',
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabel Audit Log
CREATE TABLE audit_log (
    id_log INT PRIMARY KEY AUTO_INCREMENT,
    id_user INT,
    tabel_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action ENUM('create', 'update', 'delete') NOT NULL,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES users(id_user)
);

-- ============================================
-- INDEXES UNTUK OPTIMASI PERFORMA
-- ============================================

-- Indexes untuk tabel obat
CREATE INDEX idx_obat_kode ON obat(kode_obat);
CREATE INDEX idx_obat_nama ON obat(nama_obat);
CREATE INDEX idx_obat_kategori ON obat(id_kategori);
CREATE INDEX idx_obat_status ON obat(status);

-- Indexes untuk tabel stok_obat
CREATE INDEX idx_stok_obat ON stok_obat(id_obat);
CREATE INDEX idx_stok_batch ON stok_obat(batch_number);
CREATE INDEX idx_stok_expired ON stok_obat(tanggal_kadaluwarsa);
CREATE INDEX idx_stok_status ON stok_obat(status);

-- Indexes untuk tabel transaksi
CREATE INDEX idx_transaksi_no ON transaksi(no_transaksi);
CREATE INDEX idx_transaksi_tanggal ON transaksi(tanggal_transaksi);
CREATE INDEX idx_transaksi_customer ON transaksi(id_customer);
CREATE INDEX idx_transaksi_dokter ON transaksi(id_dokter);
CREATE INDEX idx_transaksi_status ON transaksi(status);

-- Indexes untuk tabel detail_transaksi
CREATE INDEX idx_detail_transaksi ON detail_transaksi(id_transaksi);
CREATE INDEX idx_detail_obat ON detail_transaksi(id_obat);

-- Indexes untuk tabel mutasi_stok
CREATE INDEX idx_mutasi_obat ON mutasi_stok(id_obat);
CREATE INDEX idx_mutasi_tanggal ON mutasi_stok(created_at);
CREATE INDEX idx_mutasi_jenis ON mutasi_stok(jenis_mutasi);

-- ============================================
-- CONTOH DATA SAMPLE
-- ============================================

-- Sample data kategori obat
INSERT INTO kategori_obat (nama_kategori, deskripsi) VALUES
('Analgesik', 'Obat pereda nyeri'),
('Antibiotik', 'Obat anti bakteri'),
('Antasida', 'Obat maag'),
('Vitamin', 'Vitamin dan suplemen'),
('Antihipertensi', 'Obat tekanan darah tinggi');

-- Sample data bentuk sediaan
INSERT INTO bentuk_sediaan (nama_bentuk, deskripsi) VALUES
('Tablet', 'Bentuk padat berbentuk tablet'),
('Kapsul', 'Bentuk kapsul'),
('Sirup', 'Bentuk cair'),
('Injeksi', 'Bentuk suntikan'),
('Salep', 'Bentuk topikal');

-- Sample data supplier
INSERT INTO supplier (kode_supplier, nama_supplier, alamat, telepon, email, pic_name, pic_phone) VALUES
('SUP001', 'PT. Kimia Farma', 'Jakarta Pusat', '021-123456', 'info@kimiafarma.com', 'Budi Santoso', '081234567890'),
('SUP002', 'PT. Kalbe Farma', 'Jakarta Timur', '021-789012', 'info@kalbe.com', 'Sari Dewi', '081987654321');

-- Sample data obat
INSERT INTO obat (kode_obat, nama_obat, nama_generik, id_kategori, id_bentuk, kandungan, dosis, kemasan, isi_kemasan, satuan, golongan, harga_beli, harga_jual, margin_persen) VALUES
('OBT001', 'Paracetamol 500mg', 'Paracetamol', 1, 1, 'Paracetamol 500mg', '500mg', 'Strip', 10, 'Tablet', 'bebas', 15000, 18000, 20.00),
('OBT002', 'Amoxicillin 500mg', 'Amoxicillin', 2, 2, 'Amoxicillin 500mg', '500mg', 'Strip', 10, 'Kapsul', 'keras', 25000, 30000, 20.00),
('OBT003', 'Promag Tablet', 'Antasida', 3, 1, 'Mg(OH)2, Al(OH)3', '1 tablet', 'Strip', 10, 'Tablet', 'bebas', 8000, 10000, 25.00);

-- Sample data users
INSERT INTO users (username, password, nama_lengkap, email, role) VALUES
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Administrator', 'admin@apotek.com', 'admin'),
('apoteker1', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Dr. Ahmad Apoteker', 'apoteker@apotek.com', 'apoteker'),
('kasir1', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Sinta Kasir', 'kasir@apotek.com', 'kasir');