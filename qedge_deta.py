# qedge_data.py -- Formula Master Index edge export, 2026-08-15
# (deterministic SQL paging: ORDER BY 公式 ID, url; two pages, 100 + 82)
# TOTAL_ROWS / DECLARED_ISLANDS are same-day full-table SQL measurements.
# ROWS: (page_hex_id, title, [merged unique target hex ids])
TOTAL_ROWS = 940
DECLARED_ISLANDS = 758
ROWS = [
    ("9a4620e1e8cc4090801bcaa6c239d071", "ACO-002｜測厚解析度—時間解析度關係（Resolution–Timing Relation）", ["07f625b656164bd7b4a6c9c724f928b7"]),
    ("06b9524c44cf4b52a24d48f5f63d90e7", "BAYES-001｜貝氏定理與可信區間（Bayesian Updating & Credible Interval）", ["0e4e14ffddfd44e7a1e49d4029f63c49"]),
    ("2590f2c6f43e49d69231d0cf3a1d57d6", "BB-001｜黑體輻射能量密度", ["3e2d5f8f14db4e75b5e5ba5c165ee6ee"]),
    ("3cd42a3f0bc14ffa9c9f0b6f9e35e37b", "BFI-001｜Bit-Formula Isomorphism", ["191f0f5c759f80e6ae05d6f4e6ba57ab"]),
    ("3d6ff18a83180d9a49dc3f20a4e0a2d7", "BH-001｜Schwarzschild 視界半徑", ["3c55ff18a83180688010c0d7b1ab31d2"]),
    ("3d5ff18a83180aa891f9c33e1ba48f4e", "BH-003｜Bekenstein–Hawking 熵", ["3d9ff18a83180749e6fdd9f77fb9a2e2", "3deff18a83180a0b8bd2f3e0f7d3b9e1"]),
    ("3c5ff18a831807ab5e8f5b47e31f3a5c", "BH-005｜Schwarzschild Hawking 溫度", ["3d9ff18a83180749e6fdd9f77fb9a2e2", "3c55ff18a83180688010c0d7b1ab31d2"]),
    ("3e8ff18a831803a8e3c8d0e5e5f5d7f6", "BH-009｜Kerr Hawking 溫度", ["3e1ff18a8318067a90bc575ab0f2da10", "3e5ff18a831808dab9c4f60e96b9a3f4"]),
    ("3cbff18a83180e2fa4b9c53a10ba1a4f", "BH-021｜Schwarzschild Hawking 功率近似", ["3c55ff18a83180688010c0d7b1ab31d2"]),
    ("3d0ff18a83180f8c9a3bf2e1f1e8d5c2", "BH-022｜Schwarzschild 蒸發時間近似", ["3d9ff18a83180749e6fdd9f77fb9a2e2"]),
    ("3e5ff18a831808dab9c4f60e96b9a3f4", "BH-026｜Kerr–Newman Smarr 關係", ["3e1ff18a8318067a90bc575ab0f2da10", "3e5ff18a83180a3e9f28c8f8e5a2a6e6", "3d0ff18a83180b5f9b4ee2c9d8b2e4a1"]),
    ("3d9ff18a83180749e6fdd9f77fb9a2e2", "BH-029｜Schwarzschild 負熱容恆等式 C = −2S_BH", ["3d5ff18a83180aa891f9c33e1ba48f4e", "3c5ff18a831807ab5e8f5b47e31f3a5c", "3d7ff18a83180a8ca8e3c2e2d8f9e5f1", "3e1ff18a8318067a90bc575ab0f2da10", "3deff18a83180a0b8bd2f3e0f7d3b9e1", "3e5ff18a83180a3e9f28c8f8e5a2a6e6", "3d0ff18a83180b5f9b4ee2c9d8b2e4a1", "3c0ff18a83180a1e9d8fc5e6a7b9c2d3", "3c2ff18a83180f9da9e4c1b7d6e5f0a8", "3d2ff18a83180e4b9a6cc7d8e9f0a1b2"]),
    ("3c55ff18a83180688010c0d7b1ab31d2", "BH-030｜黑洞定態掃描：Ṁ = ηF_in − F_out 的單根與不穩定性", ["3d7ff18a83180a8ca8e3c2e2d8f9e5f1", "3c5ff18a831807ab5e8f5b47e31f3a5c", "3cbff18a83180e2fa4b9c53a10ba1a4f", "3d6ff18a83180d9a49dc3f20a4e0a2d7"]),
    ("3e1ff18a8318067a90bc575ab0f2da10", "BH-031｜Davies 點：加毛使熱容翻正（C = −2S 的普遍性被推翻）", ["3d9ff18a83180749e6fdd9f77fb9a2e2", "3e8ff18a831803a8e3c8d0e5e5f5d7f6", "3e5ff18a831808dab9c4f60e96b9a3f4", "3d7ff18a83180a8ca8e3c2e2d8f9e5f1", "3e5ff18a83180a3e9f28c8f8e5a2a6e6", "3d0ff18a83180b5f9b4ee2c9d8b2e4a1"]),
    ("3deff18a83180a0b8bd2f3e0f7d3b9e1", "BH-032｜對數修正下的溫度偏离與熱容（條件式）", ["3d9ff18a83180749e6fdd9f77fb9a2e2", "3d3ff18a83180e0da5f7c8b2a1d4e6f9", "3d7ff18a83180a8ca8e3c2e2d8f9e5f1", "3d5ff18a83180aa891f9c33e1ba48f4e"]),
    ("3e5ff18a83180a3e9f28c8f8e5a2a6e6", "BH-033｜極端極限的三分法：Nernst 違反、C ∝ T、不可達性存活", ["3e1ff18a8318067a90bc575ab0f2da10", "3d9ff18a83180749e6fdd9f77fb9a2e2", "3e8ff18a831803a8e3c8d0e5e5f5d7f6", "3e5ff18a831808dab9c4f60e96b9a3f4", "3d0ff18a83180b5f9b4ee2c9d8b2e4a1"]),
    ("3d0ff18a83180b5f9b4ee2c9d8b2e4a1", "BH-034｜RN-AdS 延伸相空間：M 是焓，P–V 臨界點與 3/8 普適比", ["3e1ff18a8318067a90bc575ab0f2da10", "3e5ff18a831808dab9c4f60e96b9a3f4"]),
    ("3d1ff18a83180f8f9e2dc4b7a5c3e8f2", "BH-035｜熱力學幾何的表示相依性：Ruppeiner 曲率的散度不是 Davies 點的獨立證據v", ["3e1ff18a8318067a90bc575ab0f2da10", "3e5ff18a83180a3e9f28c8f8e5a2a6e6", "3d9ff18a83180749e6fdd9f77fb9a2e2"]),
    ("3e2d5f8f14db4e75b5e5ba5c165ee6ee", "BIOHEAT-001｜體表輻射散熱（Stefan–Boltzmann Surface Application）", ["2590f2c6f43e49d69231d0cf3a1d57d6", "3e9ff18a83180c3f9a2bd5e7c1f8b4d6"]),
    ("3cbff18a8318057b8e4a9d2c6f1e7b8a", "BIOHEAT-002｜生物熱傳導（Pennes Bioheat Equation）", ["3e9ff18a83180c3f9a2bd5e7c1f8b4d6", "3e6ff18a8318049d8c5ba3f7e2d9c1b5"]),
    ("3d4ff18a8318083aa9c8f5e2b7d1c6a9", "BIOHEAT-003｜對流散熱（Newton 冷卻與 Nu 關係式）", ["3e9ff18a83180c3f9a2bd5e7c1f8b4d6"]),
    ("3ecff18a831801fb8a4cd6e2b9f5c7a3", "BIOHEAT-004｜蒸發潛熱與 Lewis 參數封閉（Evaporative Latent Heat & Lewis Closure）", ["3e9ff18a83180c3f9a2bd5e7c1f8b4d6", "3e6ff18a8318049d8c5ba3f7e2d9c1b5"]),
    ("3e9ff18a83180c3f9a2bd5e7c1f8b4d6", "BIOHEAT-005｜人體熱傳輸統一場方程與運算矩陣（Unified Field Equation & Operation Matrix）", ["3e2d5f8f14db4e75b5e5ba5c165ee6ee", "3cbff18a8318057b8e4a9d2c6f1e7b8a", "3d4ff18a8318083aa9c8f5e2b7d1c6a9", "3ecff18a831801fb8a4cd6e2b9f5c7a3", "3e6ff18a8318049d8c5ba3f7e2d9c1b5"]),
    ("3e6ff18a8318049d8c5ba3f7e2d9c1b5", "BIOHEAT-006｜生理熱調節控制律與極限環（Thermoregulatory Control Law & Limit Cycle）", ["3cbff18a8318057b8e4a9d2c6f1e7b8a", "3ecff18a831801fb8a4cd6e2b9f5c7a3", "3e9ff18a83180c3f9a2bd5e7c1f8b4d6"]),
    ("191f0f5c759f80e6ae05d6f4e6ba57ab", "BITMAT-001｜經典位元運算矩陣（Classical Bit Operation Matrix）", ["3c5ff18a83180d2b9a4ef7c1d8e6b5a2", "3cd42a3f0bc14ffa9c9f0b6f9e35e37b", "3e0ff18a83180a7d9c4bf2e6a8d5c1b9", "3d8ff18a83180a6f9c2be4d7a1f5c8e3", "3ebff18a8318062d9a7cf4e1b8d3c6a5"]),
    ("3f0ff18a83180e1b9c6ad3e7f2c4b8a6", "BM-001｜Blandford–McKee 自相似爆震解", ["3f1ff18a83180c5d9a4be7f1c6d8e2a4"]),
    ("3dbff18a83180f7c9a3ed5b8f1c6e4a7", "CE-0002｜State Space", ["3f2ff18a83180a9d7c4be6f3d8c1e5a9", "3f3ff18a83180b8e6d4cf7a2e9d5c1b8", "3f4ff18a83180c9f5e4da8b6e1c7d3a5", "3f5ff18a83180d1a6f4ec9b7d2e8c5a1", "3f6ff18a83180e2b7a5fd4c8e3f9d6b2", "3f7ff18a83180f3c8b6ae5d9f4c1e7a3"]),
    ("3dcff18a8318018d9c4fa6e2b7d5f8a4", "CE-0004｜Residual Topology", ["3f2ff18a83180a9d7c4be6f3d8c1e5a9", "3f3ff18a83180b8e6d4cf7a2e9d5c1b8", "3f8ff18a8318019c7b4df6e2a8d5c9b1", "3f9ff18a831802ad8c5e4f7b1d6e9c2", "3faff18a831803be9d6f4a8c5e2b7d1", "3fbff18a831804cfae7a5b9d6c3e8f2"]),
    ("3ddff18a8318029e8c5ab7f3d9e6c1b5", "CE-0007｜CKM as Unitary Representation Transformation", ["3f2ff18a83180a9d7c4be6f3d8c1e5a9", "3f9ff18a831802ad8c5e4f7b1d6e9c2", "3fcff18a831805d0bf8a6c9e4d7f1a3", "3fdff18a831806e1c0a9b7d5f2e8c4a6"]),
    ("3deff18a831803af9d6bc8e4f1a7d2b6", "CE-0008｜Continuity System & Identity Seed", ["3f2ff18a83180a9d7c4be6f3d8c1e5a9", "3f3ff18a83180b8e6d4cf7a2e9d5c1b8", "3feff18a831807f2d1ba8c6e4f9d5b7", "3ffff18a83180803e2cb9d7f5a1e6c4"]),
]