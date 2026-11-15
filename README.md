# 🚀 CachyOS Setup Manager — Windows to Linux

### Windows alışkanlıklarınızı bırakmadan CachyOS'a geçin!

![Version](https://img.shields.io/badge/Version-0.8_Beta-blue)
![Platform](https://img.shields.io/badge/Platform-CachyOS%20%7C%20Arch_Linux-1793D1)
![Python](https://img.shields.io/badge/Python-3-3776AB)
![GUI](https://img.shields.io/badge/GUI-PySide6-41CD52)
![License](https://img.shields.io/badge/License-MIT-green)
![Language](https://img.shields.io/badge/Language-Türkçe-red)

## 🌍 Bu Proje Neden Geliştirildi?

Windows'tan Linux'a geçmek istiyor ancak yıllardır kullandığınız uygulamalardan, alışkanlıklarınızdan ve çalışma düzeninizden vazgeçmek istemiyor musunuz?

- Windows'ta yaptığım işleri Linux'ta da yapabilir miyim?
- Kullandığım programların Linux karşılıkları nelerdir?
- SQL Server, uzak masaüstü ve yazılım geliştirme araçlarını kullanabilir miyim?
- Hyper-V ve VirtualBox sanal makinelerimi taşıyabilir miyim?
- Format sonrasında bütün uygulamalarımı nasıl yeniden kurabilirim?
- Her işlem için terminal komutlarını öğrenmek zorunda mıyım?

**CachyOS Setup Manager, bu sorulara çözüm üretmek amacıyla geliştirilmiştir.**

Windows kullanıcılarının Linux'a geçişini kolaylaştırmayı, alıştıkları çalışma ortamını CachyOS üzerinde yeniden oluşturmalarına yardımcı olmayı ve teknik işlemleri mümkün olduğunca basitleştirmeyi hedefler.

Yalnızca bir uygulama kurulum scripti değil; bir **Linux geçiş, adaptasyon, kurulum ve sistem yönetim projesidir.**

## 🎯 Kimler İçin?

- Windows'tan Linux'a geçmek isteyenler
- Yeni CachyOS kullanıcıları
- Sistem ve ağ yöneticileri
- Bilgi işlem ve teknik destek uzmanları
- Yazılım geliştiriciler
- SQL ve veritabanı yöneticileri
- Sanallaştırma teknolojileriyle çalışanlar
- Format sonrası kurulumlarını hızlandırmak isteyenler

## 🔄 Windows'ta Ne Kullanıyordunuz? Linux'ta Ne Kullanabilirsiniz?

| Windows uygulaması veya işlevi | Linux alternatifi |
|---|---|
| Microsoft Office | ONLYOFFICE |
| WinRAR / WinZip | Ark / 7-Zip |
| SQL Server Management Studio | DBeaver / SQLCMD |
| Microsoft SQL Server | SQL Server Docker Edition |
| Windows Hyper-V | QEMU / KVM / Virt-Manager |
| VirtualBox | VirtualBox / KVM |
| VMware Workstation | QEMU / KVM |
| Uzak Masaüstü Bağlantısı | Remmina / KRDC |
| TeamViewer / AnyDesk | RustDesk |
| Windows Görev Yöneticisi | Mission Center / Btop |
| WizTree / TreeSize | QDirStat / Filelight |
| Everything Search | FSearch |
| CrystalDiskMark | KDiskMark |
| CrystalDiskInfo | GSmartControl |
| CPU-Z | CPU-X |
| AIDA64 | Hardinfo2 |
| Total Commander | Dolphin / Nemo |
| Notepad++ | Notepadqq / Kate |
| Adobe Acrobat - PDF düzenleme | PDF Arranger / Xournal++ |
| CCleaner | BleachBit |
| Rufus | Ventoy |
| Windows Güvenlik Duvarı | UFW |
| GlassWire | OpenSnitch |
| WinMerge | Meld |
| Angry IP Scanner | Nmap / Zenmap |
| Windows PowerShell | PowerShell 7 |
| Visual Studio Code | Visual Studio Code |
| Postman | Postman |
| FileZilla | FileZilla |
| FreeFileSync | FreeFileSync |

Bu araçlar Windows alışkanlıklarına yakın alternatifler sunar; bütün özelliklerin birebir aynı olması garanti edilmez.

## 📦 Uygulama Merkezi

V0.8 sürümü, 11 farklı kategoride 122 paket içeren bir uygulama kataloğu sunmaktadır.

| Kategori | İçerik |
|---|---|
| 🖥️ Sistem ve optimizasyon | Donanım analizi, disk yönetimi, sistem izleme |
| 📁 Ofis ve günlük kullanım | Ofis, internet, PDF, arşiv ve medya |
| 🗄️ Veritabanı yönetimi | SQL Server, DBeaver, SQLCMD |
| 💻 Yazılım geliştirme | VS Code, Flutter, Android, .NET, Git |
| 🪟 Windows uyumluluğu | Wine ve Windows uygulama rehberi |
| 🌐 VPN ve uzak bağlantı | RustDesk, Remmina, FreeRDP |
| 🐳 Konteyner yönetimi | Docker, Compose, Portainer |
| ⚙️ Sanallaştırma | KVM, QEMU, VirtualBox |
| 💾 Yedekleme | Duplicati, Backrest, Restic |
| 🛡️ Ağ ve güvenlik | Nmap, Wireshark, UFW, OpenSnitch |
| 🎨 Masaüstü | Uygulama simgeleri ve kısayollar |

## ✨ Temel Özellikler

- Grafik arayüz üzerinden uygulama kurulumu
- Silent Setup mantığıyla kontrollü toplu kurulum
- Tekil ve kategori bazında uygulama seçimi
- Kurulu uygulamaları otomatik algılama
- Yalnızca eksik uygulamaları seçme
- Mevcut paket sürümlerini görüntüleme
- Güncelleme kontrolü
- Türkçe uygulama açıklamaları
- Uygulama simgeleri
- Kurulum öncesi işlem planı
- Anlık işlem günlüğü
- Kurulum sonrası durum kontrolü
- Çevrimdışı HTML kullanım rehberi

## 🐳 Docker ve SQL Server

Windows ortamında kullanılan veritabanı ve geliştirme araçlarının Linux üzerinde de kullanılabilmesi hedeflenmektedir.

Desteklenen araçlar:

- Docker Engine
- Docker Compose
- Portainer
- Lazydocker
- Microsoft SQL Server 2022 Developer
- DBeaver
- SQLCMD

SQL Server için kalıcı Docker veri alanı ve yerel bağlantı yapılandırması sunulur.

Developer Edition yalnızca geliştirme ve test amaçlıdır.

## 💻 Yazılım Geliştirme Ortamı

Geliştiricilerin format sonrasında çalışma ortamlarını daha kolay hazırlayabilmeleri için çeşitli uygulamalar sunulmaktadır.

- Visual Studio Code
- Android Studio ve Android SDK
- Flutter ve FVM
- .NET SDK
- Python
- Node.js ve NPM
- PowerShell
- Git ve GitHub CLI
- Postman
- CMake

DBeaver için Java 21 yapılandırması gibi uygulamaya özel çözümler de bulunmaktadır.

## 💽 Sanal Makine Disk Dönüştürme

Mevcut Windows sanal makinelerinizi tamamen yeniden kurmak yerine Linux ortamına taşımak için grafik disk dönüştürme aracı geliştirilmiştir.

| Kaynak | Kaynak biçimi | Hedef |
|---|---|---|
| Hyper-V | VHDX | QCOW2 |
| VirtualBox | VDI | QCOW2 |
| VMware | VMDK | QCOW2 |

Dönüştürme aracının özellikleri:

- Kaynak ve hedef dosya seçimi
- Gerekli disk alanı tahmini
- Sıkıştırılmış QCOW2 oluşturma
- Dönüşüm sonrası bütünlük kontrolü
- Orijinal disk dosyasını koruma

Dönüştürmeden önce sanal makine kapatılmalı ve snapshot bağımlılıkları kontrol edilmelidir. Dönüştürülen işletim sisteminin açılışı ayrıca doğrulanmalıdır.

## 🌐 Sanal Makine Ağ Yöneticisi

Hyper-V External Virtual Switch benzeri Ethernet köprüsü oluşturulmasına yardımcı olur.

- Fiziksel Ethernet kartı seçimi
- DHCP tabanlı br0 köprüsü
- Yapılandırma önizlemesi
- Ağ ayarlarını geri alma
- Virt-Manager ile yerel ağ bağlantısı

Sanal makinelerin fiziksel ağ üzerinden erişilebilir olabilmesi hedeflenir.

Ağ köprüsü işlemleri yalnızca yerel konsolda yapılmalıdır. Ağ bağlantısı geçici olarak kesilebilir.

## 🔄 Paket ve Güncelleme Yönetimi

| Paket kaynağı | Kullanım |
|---|---|
| Pacman | CachyOS ve Arch Linux depoları |
| AUR / Paru | Topluluk paketleri |
| Flatpak | Bağımsız uygulamalar |
| Docker | Konteyner tabanlı servisler |

Kurulu paketler kontrol edilerek gereksiz tekrar kurulumlar önlenmeye çalışılır.

Arch Linux tabanlı sistemlerde kısmi sistem güncellemelerinden kaçınılır. AUR varsayılan olarak kapalıdır ve paket kaynakları incelenerek etkinleştirilmelidir.

Docker imajları otomatik güncellenmez.

## 🛠️ Sorun Giderme ve Teknik Rehber

Proje yalnızca kurulum işlemlerini değil, karşılaşılabilecek problemlerin çözümünü de kapsamaktadır.

- Flutter güncelleme çakışmaları
- RustDesk dosya çakışmaları
- Pacman dosya sahipliği kontrolü
- Java sürüm uyumsuzlukları
- DBeaver Java 21 yapılandırması
- Docker ve SQL Server yapılandırması
- KVM sanal makine kurulumu
- Hyper-V disk dönüşümü
- Ethernet ağ köprüsü
- SPICE Guest Tools
- Remmina dinamik ekran çözünürlüğü
- VirtIO performans önerileri

Sorun giderme işlemlerinde kontrolsüz dosya silme yerine inceleme ve yedekleme esas alınır.

## 📚 İnteraktif HTML Rehberi

Proje ile birlikte çevrimdışı kullanılabilen genel bir kurulum ve kullanım rehberi sunulmaktadır.

- [Kurulum talimatları](KURULUM.html)
- [Genel kullanım rehberi](rehber.html)

Rehber sayesinde uygulama kurulumlarını ve teknik yapılandırmaları manuel olarak da gerçekleştirebilirsiniz.

## 🚀 Nasıl Kurulur?

### Git ile kurulum

```bash
sudo pacman -S --needed git

git clone https://github.com/koksal1978/CachyOS-Setup-Manager.git

cd CachyOS-Setup-Manager

bash launch.sh
```

### ZIP ile kurulum

1. GitHub sayfasından Code → Download ZIP seçeneğine tıklayın.
2. Arşivi çıkartın.
3. Proje klasöründe terminal açın.
4. Aşağıdaki komutu çalıştırın:

```bash
bash launch.sh
```

KDE Plasma kullanıcıları masaüstü başlatıcısını da kullanabilir.

Uygulamayı normal kullanıcı olarak çalıştırın. Yönetici yetkisi gerektiğinde sudo üzerinden alınır.

## 📂 Proje Yapısı

```text
CachyOS-Setup-Manager/
├── manager.py
├── vmtools.py
├── catalog.json
├── metadata.json
├── launch.sh
├── Kurulumu-Baslat.sh
├── Kurulumu-Baslat.desktop
├── KURULUM.html
├── rehber.html
├── README.md
├── SECURITY.md
├── LICENSE
├── .gitattributes
└── .gitignore
```

## 🛡️ Güvenlik ve Gizlilik

- Kurulumdan önce yapılacak işlemleri inceleyin.
- AUR paketlerinin kaynaklarını doğrulayın.
- Disk biçimlendirme otomatik olarak yapılmaz.
- Yedekten geri yükleme otomatik değildir.
- Kurumsal VPN ve erişim bilgileri kullanıcı tarafından yapılandırılır.
- Docker erişimi yüksek sistem yetkileri sağlayabilir.
- Docker ortam değişkenlerindeki parolalar yetkili kullanıcılar tarafından okunabilir.
- İşlem günlüklerini paylaşmadan önce hassas bilgiler açısından kontrol edin.

Güvenlik bildirimleri için [SECURITY.md](SECURITY.md) dosyasını inceleyin.

## 🧪 Geliştirme Durumu

**V0.8 Public Beta**

Proje aktif geliştirme aşamasındadır. Temel kod ve sözdizimi kontrolleri gerçekleştirilmiştir ancak bütün kurulum ve yapılandırma işlemlerinin gerçek sistemlerde uçtan uca testleri tamamlanmamıştır.

Üretim ortamlarında kullanmadan önce sanal makinede test edilmesi önerilir.

CachyOS Setup Manager bağımsız bir topluluk projesidir. Resmî CachyOS ürünü değildir.

## 🗺️ Gelecek Sürüm Hedefleri

- [ ] İngilizce ve çoklu dil desteği
- [ ] Gelişmiş uygulama mağazası görünümü
- [ ] Windows uygulamalarına göre Linux alternatifi arama
- [ ] Kişiselleştirilebilir kurulum profilleri
- [ ] Format öncesi sistem envanteri
- [ ] Format sonrası otomatik geri yükleme
- [ ] Gelişmiş servis yönetimi
- [ ] Grafik yedekleme ve kurtarma merkezi
- [ ] Sistem performans analizleri
- [ ] Snapper entegrasyonu
- [ ] AppImage dağıtımı
- [ ] Otomatik test altyapısı

## 🤝 Topluluk ve Katkı

Bu proje Linux'a geçiş yapmak isteyen herkesin yararlanabileceği bir kaynak olmayı hedeflemektedir.

Uygulama önerileri, hata bildirimleri, kod geliştirmeleri, rehber katkıları ve çeviriler değerlendirilebilir.

[Hata bildir veya öneride bulun](https://github.com/koksal1978/CachyOS-Setup-Manager/issues)

Projeyi faydalı bulduysanız yıldız vererek destekleyebilirsiniz.

## 📄 Lisans

MIT License

Üçüncü taraf uygulamalar kendi lisanslarına ve kullanım koşullarına tabidir.

## 🇬🇧 English Summary

**Switch from Windows to CachyOS without losing your familiar workflows.**

CachyOS Setup Manager is an independent, open-source graphical setup and system management assistant designed to simplify Windows-to-Linux migration.

It brings Linux application alternatives, automated software installation, package updates, development tools, SQL Server, Docker, virtualization, virtual disk conversion and troubleshooting together in one project.

The current version is V0.8 Public Beta. Full end-to-end testing is still required.

---

### Windows to CachyOS

**Discover • Install • Configure • Migrate • Manage**

*Linux'a geçiş bir vazgeçiş değil, yeni bir çalışma ortamına uyum süreci olsun.*