# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/guard.py

ROL:
- UI ortak katmanı için merkezi sözleşmeyi (contract) tanımlar
- UI başlangıcında ortak modüllerin ve zorunlu sabitlerin varlığını doğrular
- Hata durumunda nokta atışı çözüm mesajı üretir
- UI katmanının tek ortak merkezden beslendiğini garanti altına alır

MİMARİ:
- Runtime guard + contract metni birlikte sunulur
- UI ile ilgili ortak yapı yalnızca app/ui/ortak altında tanımlanır
- Ekranlar / popup'lar / bileşenler bu guard sözleşmesine uymalıdır
- Geriye uyumluluk katmanı içermez
- Deterministik davranır

DENETLENENLER:
- app/ui/ortak klasörü
- zorunlu ortak dosyalar
- ortak modüllerin import edilebilir olması
- kritik sabit / fonksiyonların modüllerde tanımlı olması

ENTEGRASYON:
- Bu guard doğrudan main.py içine gömülmez
- app/ui/yoneticisi.py içinde UI root üretilmeden hemen önce çağrılmalıdır

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Final


# =========================================================
# CONTRACT SABITLERI
# =========================================================
UI_ORTAK_KLASOR: Final[str] = "app/ui/ortak"

RENK_MODULU: Final[str] = "app.ui.ortak.renkler"
BOYUT_MODULU: Final[str] = "app.ui.ortak.boyutlar"
STIL_MODULU: Final[str] = "app.ui.ortak.stiller"
IKON_MODULU: Final[str] = "app.ui.ortak.ikonlar"
YARDIMCI_MODULU: Final[str] = "app.ui.ortak.yardimcilar"

ZORUNLU_ORTAK_DOSYALAR: Final[tuple[str, ...]] = (
    "__init__.py",
    "guard.py",
    "renkler.py",
    "boyutlar.py",
    "stiller.py",
    "ikonlar.py",
    "yardimcilar.py",
)

UI_CONTRACT_METNI: Final[str] = (
    "UI ortak yapı sözleşmesi:\n"
    "1) Ortak renkler sadece app/ui/ortak/renkler.py içinden alınır.\n"
    "2) Ortak boyutlar sadece app/ui/ortak/boyutlar.py içinden alınır.\n"
    "3) Ortak stiller sadece app/ui/ortak/stiller.py içinden alınır.\n"
    "4) Ortak ikon çözümleme sadece app/ui/ortak/ikonlar.py içinden alınır.\n"
    "5) Ortak yardımcılar sadece app/ui/ortak/yardimcilar.py içinden alınır.\n"
    "6) UI dosyalarında hardcoded tema/boyut/ikon çözümü yazılmaz.\n"
    "7) app/ui/ortak dışına ikinci bir ortak UI merkezi kurulmaz."
)

YASAK_ORNEKLER: Final[tuple[str, ...]] = (
    "Color(0.12, 0.13, 0.16, 1.0)",
    "dp(13)  # ekran içinde rastgele sabit",
    "source='app/assets/icons/menu.png'",
    "self.bg_color = (...)  # ortak modül dışı tema",
)

SERBEST_ORNEKLER: Final[tuple[str, ...]] = (
    "from app.ui.ortak.renkler import ARKAPLAN",
    "from app.ui.ortak.boyutlar import BOSLUK_MD",
    "from app.ui.ortak.ikonlar import ikon_yolu",
    "from app.ui.ortak.stiller import rounded_bg",
)


# =========================================================
# KRITIK BEKLENTILER
# =========================================================
ZORUNLU_MODUL_UYELERI: Final[dict[str, tuple[str, ...]]] = {
    RENK_MODULU: (
        "ARKAPLAN",
        "KART",
        "KART_ALT",
        "METIN",
        "METIN_SOLUK",
        "VURGU",
        "BASARI",
        "UYARI",
        "HATA",
        "KENARLIK",
        "SEFFAF",
    ),
    BOYUT_MODULU: (
        "BOSLUK_MD",
        "YUKSEKLIK_TOOLBAR",
        "YUKSEKLIK_BUTON",
    ),
    STIL_MODULU: (
        "rounded_bg",
    ),
    IKON_MODULU: (
        "ikon_yolu",
    ),
    YARDIMCI_MODULU: (
        "guvenli_yazi",
        "kisalt_yol",
    ),
}


# =========================================================
# HATA MODELI
# =========================================================
@dataclass(frozen=True, slots=True)
class UIGuardSorunu:
    """
    UI guard tarafından üretilen tekil sorun kaydı.
    """

    kod: str
    baslik: str
    hedef: str
    detay: str
    cozum: str

    def metin(self) -> str:
        return (
            f"{self.baslik}\n"
            f"Hedef: {self.hedef}\n"
            f"Detay: {self.detay}\n\n"
            f"Çözüm:\n{self.cozum}"
        )


class UIGuardHatasi(RuntimeError):
    """
    UI ortak katman guard hatası.
    """

    def __init__(self, sorunlar: list[UIGuardSorunu]) -> None:
        self.sorunlar = list(sorunlar)

        metin = "\n\n---\n\n".join(
            f"[{index}] {sorun.metin()}"
            for index, sorun in enumerate(self.sorunlar, start=1)
        )
        super().__init__(metin)


# =========================================================
# INTERNAL YARDIMCILAR
# =========================================================
def _proje_koku() -> Path:
    """
    Proje kökünü çözer.
    guard.py -> ortak -> ui -> app -> proje_kökü
    """
    return Path(__file__).resolve().parents[3]


def _ui_ortak_dizini() -> Path:
    return Path(__file__).resolve().parent


def _dosya_yolu(dosya_adi: str) -> Path:
    return _ui_ortak_dizini() / dosya_adi


def _sorun(
    *,
    kod: str,
    baslik: str,
    hedef: str,
    detay: str,
    cozum: str,
) -> UIGuardSorunu:
    return UIGuardSorunu(
        kod=kod,
        baslik=baslik,
        hedef=hedef,
        detay=detay,
        cozum=cozum,
    )


def _modul_import_et(modul_yolu: str):
    return import_module(modul_yolu)


# =========================================================
# KONTROLLER
# =========================================================
def _klasor_kontrolu() -> list[UIGuardSorunu]:
    sorunlar: list[UIGuardSorunu] = []

    ortak_dir = _ui_ortak_dizini()
    if not ortak_dir.exists():
        sorunlar.append(
            _sorun(
                kod="ui_ortak_klasor_yok",
                baslik="UI ortak klasörü bulunamadı",
                hedef=UI_ORTAK_KLASOR,
                detay=f"Beklenen klasör mevcut değil: {ortak_dir}",
                cozum=(
                    "app/ui/ortak klasörünü oluştur.\n"
                    "İçine zorunlu dosyaları ekle:\n"
                    "- __init__.py\n"
                    "- guard.py\n"
                    "- renkler.py\n"
                    "- boyutlar.py\n"
                    "- stiller.py\n"
                    "- ikonlar.py\n"
                    "- yardimcilar.py"
                ),
            )
        )

    return sorunlar


def _zorunlu_dosyalar_kontrolu() -> list[UIGuardSorunu]:
    sorunlar: list[UIGuardSorunu] = []

    for dosya_adi in ZORUNLU_ORTAK_DOSYALAR:
        path_obj = _dosya_yolu(dosya_adi)
        if path_obj.exists() and path_obj.is_file():
            continue

        sorunlar.append(
            _sorun(
                kod="ui_ortak_dosya_eksik",
                baslik="Zorunlu UI ortak dosyası eksik",
                hedef=str(path_obj),
                detay=f"Beklenen dosya bulunamadı: {dosya_adi}",
                cozum=(
                    f"{path_obj} dosyasını oluştur.\n"
                    "Bu dosya app/ui/ortak contract'ının zorunlu parçasıdır."
                ),
            )
        )

    return sorunlar


def _moduller_import_kontrolu() -> list[UIGuardSorunu]:
    sorunlar: list[UIGuardSorunu] = []

    for modul_yolu in ZORUNLU_MODUL_UYELERI:
        try:
            _modul_import_et(modul_yolu)
        except Exception as exc:
            hedef_dosya = modul_yolu.replace(".", "/") + ".py"
            sorunlar.append(
                _sorun(
                    kod="ui_ortak_modul_import_hatasi",
                    baslik="UI ortak modülü import edilemedi",
                    hedef=modul_yolu,
                    detay=f"{exc.__class__.__name__}: {exc}",
                    cozum=(
                        f"{hedef_dosya} dosyasını aç.\n"
                        "Dosya içindeki syntax / import hatasını düzelt.\n"
                        "Gerekirse eksik bağımlılığı ekle ve modülün tek başına import "
                        "edilebilir olduğundan emin ol."
                    ),
                )
            )

    return sorunlar


def _modul_uye_kontrolu() -> list[UIGuardSorunu]:
    sorunlar: list[UIGuardSorunu] = []

    for modul_yolu, beklenen_uyeler in ZORUNLU_MODUL_UYELERI.items():
        try:
            modul = _modul_import_et(modul_yolu)
        except Exception:
            continue

        for uye_adi in beklenen_uyeler:
            if hasattr(modul, uye_adi):
                continue

            hedef_dosya = modul_yolu.replace(".", "/") + ".py"
            ornek = _uye_ornek_cozum(modul_yolu, uye_adi)

            sorunlar.append(
                _sorun(
                    kod="ui_ortak_uye_eksik",
                    baslik="UI ortak modülünde zorunlu üye eksik",
                    hedef=f"{modul_yolu}.{uye_adi}",
                    detay=(
                        f"{modul_yolu!r} modülünde {uye_adi!r} tanımı bulunamadı."
                    ),
                    cozum=(
                        f"{hedef_dosya} dosyasını aç.\n"
                        f"{uye_adi} adında zorunlu üye tanımla.\n"
                        f"Örnek çözüm:\n{ornek}"
                    ),
                )
            )

    return sorunlar


def _uye_ornek_cozum(modul_yolu: str, uye_adi: str) -> str:
    if modul_yolu == RENK_MODULU:
        return f"{uye_adi} = (0.0, 0.0, 0.0, 1.0)"

    if modul_yolu == BOYUT_MODULU:
        return f"{uye_adi} = dp(12)"

    if modul_yolu == IKON_MODULU and uye_adi == "ikon_yolu":
        return (
            "def ikon_yolu(dosya_adi: str, fallback: str = '') -> str:\n"
            "    ...\n"
        )

    if modul_yolu == STIL_MODULU and uye_adi == "rounded_bg":
        return (
            "def rounded_bg(widget, *, bg_color, line_color, radius=None) -> None:\n"
            "    ...\n"
        )

    if modul_yolu == YARDIMCI_MODULU:
        if uye_adi == "guvenli_yazi":
            return (
                "def guvenli_yazi(value) -> str:\n"
                "    return str(value if value is not None else '')\n"
            )
        if uye_adi == "kisalt_yol":
            return (
                "def kisalt_yol(path: str, max_len: int = 56) -> str:\n"
                "    ...\n"
            )

    return f"{uye_adi} = ..."


# =========================================================
# PUBLIC API
# =========================================================
def ui_contract_metni() -> str:
    """
    UI ortak contract metnini döndürür.
    """
    return UI_CONTRACT_METNI


def ui_ortak_klasoru() -> str:
    """
    UI ortak klasör yolunu döndürür.
    """
    return UI_ORTAK_KLASOR


def zorunlu_ortak_dosyalar() -> tuple[str, ...]:
    """
    UI ortak katmanda bulunması gereken dosyaları döndürür.
    """
    return ZORUNLU_ORTAK_DOSYALAR


def yasak_ornekler() -> tuple[str, ...]:
    """
    UI içinde kullanılmaması gereken örnekleri döndürür.
    """
    return YASAK_ORNEKLER


def serbest_ornekler() -> tuple[str, ...]:
    """
    UI içinde tercih edilmesi gereken örnekleri döndürür.
    """
    return SERBEST_ORNEKLER


def ui_guard_raporu() -> list[UIGuardSorunu]:
    """
    Tüm UI ortak katman kontrollerini çalıştırır ve sorun listesini döndürür.
    """
    sorunlar: list[UIGuardSorunu] = []
    sorunlar.extend(_klasor_kontrolu())
    sorunlar.extend(_zorunlu_dosyalar_kontrolu())
    sorunlar.extend(_moduller_import_kontrolu())
    sorunlar.extend(_modul_uye_kontrolu())
    return sorunlar


def ui_guard_kontrolu() -> None:
    """
    UI ortak katman guard denetimini çalıştırır.
    Sorun varsa nokta atışı çözüm mesajlarıyla hata fırlatır.
    """
    sorunlar = ui_guard_raporu()
    if sorunlar:
        raise UIGuardHatasi(sorunlar)


def ui_guard_ozet_metni() -> str:
    """
    Guard başarısız olduğunda kullanıcıya / log'a yazdırılabilecek özet metni döndürür.
    """
    sorunlar = ui_guard_raporu()
    if not sorunlar:
        return "UI guard kontrolü başarılı."

    return "\n\n".join(
        f"[{sorun.kod}] {sorun.baslik}\n{ sorun.metin() }"
        for sorun in sorunlar
    )
def ui_guard_hata_metni(exc: Exception) -> str:
    """
    Guard hatasını kullanıcıya gösterilecek metne çevirir.
    """
    if isinstance(exc, UIGuardHatasi):
        return str(exc)

    return f"{exc.__class__.__name__}: {exc}"