# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge/yoneticisi.py

ROL:
- Belge katmanına tek giriş noktası sağlamak
- UI ve diğer katmanların belge servis detaylarını bilmesini engellemek
- Belge oturumu, içe aktarma, dışa yazma, geri yükleme ve yedek akışlarını merkezileştirmek

MİMARİ:
- Alt belge servislerine lazy import ile erişir
- UI katmanı sadece bu yöneticiyi bilir
- Belge davranışını tek yerden kontrol etmeyi kolaylaştırır
- Android / dosya / yedek katmanlarıyla belge akışını düzenli bağlar

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage / SAF ile uyumlu belge akışına uygundur
- APK / AAB davranış farkını azaltacak izole katman sağlar

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeYoneticisi:
    # =========================================================
    # OTURUM
    # =========================================================
    def oturum_baslat(self, selection: DocumentSelection) -> DocumentSession:
        from app.services.belge.oturum_servisi import oturum_baslat
        return oturum_baslat(selection)

    def oturum_identifier(self, session: DocumentSession) -> str:
        from app.services.belge.oturum_servisi import oturum_identifier
        return oturum_identifier(session)

    def oturum_display_name(self, session: DocumentSession) -> str:
        from app.services.belge.oturum_servisi import oturum_display_name
        return oturum_display_name(session)

    def calisma_dosyasi_yolu(self, session: DocumentSession) -> str:
        from app.services.belge.oturum_servisi import calisma_dosyasi_yolu
        return calisma_dosyasi_yolu(session)

    def calisma_kopyasi_var_mi(self, session: DocumentSession) -> bool:
        from app.services.belge.oturum_servisi import calisma_kopyasi_var_mi
        return calisma_kopyasi_var_mi(session)

    def guncellenmis_icerigi_kaydet(self, session: DocumentSession, new_content: str) -> str:
        from app.services.belge.oturum_servisi import guncellenmis_icerigi_kaydet
        return guncellenmis_icerigi_kaydet(session, new_content)

    def son_yedek_yolu(self, session: DocumentSession) -> str:
        from app.services.belge.oturum_servisi import son_yedek_yolu
        return son_yedek_yolu(session)

    # =========================================================
    # ICE AKTARMA
    # =========================================================
    def belgeyi_ice_aktar(self, selection: DocumentSelection) -> DocumentSession:
        from app.services.belge.belge_ice_aktarma_servisi import belgeyi_ice_aktar
        return belgeyi_ice_aktar(selection)

    # =========================================================
    # DISARI YAZMA
    # =========================================================
    def belgeyi_disari_yaz(self, session: DocumentSession, content: str) -> str:
        from app.services.belge.belge_disari_yazma_servisi import belgeyi_disari_yaz
        return belgeyi_disari_yaz(session, content)

    # =========================================================
    # GERI YUKLEME
    # =========================================================
    def belgeyi_geri_yukle(self, session: DocumentSession, backup_path: str) -> str:
        from app.services.belge.belge_geri_yukleme_servisi import belgeyi_geri_yukle
        return belgeyi_geri_yukle(session, backup_path)

    # =========================================================
    # YEDEK
    # =========================================================
    def belge_yedegi_olustur(self, session: DocumentSession) -> str:
        from app.services.belge.belge_yedek_servisi import belge_yedegi_olustur
        return belge_yedegi_olustur(session)