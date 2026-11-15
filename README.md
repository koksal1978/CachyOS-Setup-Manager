# CachyOS Setup Manager — Public Edition 0.8

CachyOS / Arch tabanlı sistemler için bağımsız Türkçe grafik uygulama kurulum yöneticisi. Resmi CachyOS ürünü değildir.

## Başlatma

ZIP arşivini çıkarın ve klasörde terminal açın:

```bash
bash launch.sh
```

KDE üzerinde `Kurulumu-Baslat.desktop` dosyası da kullanılabilir; güven uyarısı çıkarsa içeriğini inceleyin. HTML dosyası terminal komutu çalıştırmaz. Normal kullanıcı olarak çalıştırın.

## Özellikler

- 11 kategori; tekil, toplu ve eksik paket seçimi, Türkçe açıklamalar, sistem ikonları.
- Pacman ve isteğe bağlı AUR; Flatpak ve Docker yapılandırma işlemleri.
- Kurulu sürüm ve depo/AUR güncelleme kontrolü; tam sistem güncellemesi.
- Kurulum planı, canlı günlük ve işlem sonrası durum kontrolü.
- Genel çevrimdışı HTML rehberi.

## Güvenlik ve sınırlamalar

Önce planı inceleyin. AUR varsayılan kapalıdır; kaynak kodunu incelemeden etkinleştirmeyin. Disk biçimlendirme, VPN kimlik bilgileri ve yedek geri yükleme otomatik değildir. Docker erişimi yüksek yetkilidir. SQL Developer yalnız geliştirme/test içindir; Docker ortamındaki SA parolası yetkili kullanıcılarca okunabilir. Günlükler yerel kullanıcı dizininde saklanır; paylaşmadan önce temizleyin. Paket ve servis uygunluğu dağıtım sürümüne göre değişebilir. Docker imajları otomatik güncellenmez. Flatpak güncelleme kontrolü ayrı satır bazında gösterilmez. Kısayol ikonları sistemden alınır; üçüncü taraf logo dosyaları dağıtılmaz.

V0.8 statik kontrollerden geçti; gerçek CachyOS kurulum/güncelleme testi henüz yapılmadı. Üretim ortamında kullanmadan önce sanal makinede deneyin.

Lisans: MIT (önerilen açık kaynak lisansı; yayıncı lisans tercihini yayın öncesi doğrulamalıdır). Üçüncü taraf uygulamalar kendi lisanslarına tabidir.

## Güncelleme hataları
Flutter ve RustDesk dosya çakışmalarına özel güvenli tanı ve yedekleme adımları genel rehberde bulunur. Arayüzden Güncelleme hataları / çözüm düğmesiyle erişilir. Otomatik dosya taşıma veya silme yoktur.

## 0.8 yenilikleri
- GitHub CLI ve 7-Zip katalogda; Git mevcut.
- Grafik QCOW2 dönüştürücü (kaynak koruma, tahmin, sıkıştırma, check). Hedef dosya sistemi hard link desteklemelidir; desteklemiyorsa geçici çıktı korunur.
- DHCP Ethernet br0 sihirbazı, plan ve geri alma; yalnız yerel konsolda kullanın.
- Genel KVM/SPICE/Remmina rehberi. VirtIO performans değişiklikleri öneridir.
- Yeni araçlar gerçek CachyOS üzerinde henüz denenmedi; yayın öncesi test edin.
