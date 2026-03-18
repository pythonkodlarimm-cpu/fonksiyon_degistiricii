# -*- coding: utf-8 -*-
from __future__ import annotations


class RootLazyImportsMixin:
    def _get_core_helpers(self):
        from app.core.degistirici import find_item_by_identity, update_function_in_code
        from app.core.tarayici import scan_functions_from_file

        return {
            "find_item_by_identity": find_item_by_identity,
            "update_function_in_code": update_function_in_code,
            "scan_functions_from_file": scan_functions_from_file,
        }

    def _get_belge_geri_yukleme(self):
        from app.services.belge_geri_yukleme_servisi import (
            BelgeGeriYuklemeServisiHatasi,
            son_yedekten_geri_yukle,
        )

        return {
            "BelgeGeriYuklemeServisiHatasi": BelgeGeriYuklemeServisiHatasi,
            "son_yedekten_geri_yukle": son_yedekten_geri_yukle,
        }

    def _get_belge_oturumu(self):
        from app.services.belge_oturumu_servisi import (
            BelgeOturumuServisiHatasi,
            calisma_dosyasi_yolu,
            calisma_kopyasi_var_mi,
            guncellenmis_icerigi_kaydet,
            oturum_baslat,
            oturum_display_name,
            oturum_identifier,
            son_yedek_yolu,
        )

        return {
            "BelgeOturumuServisiHatasi": BelgeOturumuServisiHatasi,
            "calisma_dosyasi_yolu": calisma_dosyasi_yolu,
            "calisma_kopyasi_var_mi": calisma_kopyasi_var_mi,
            "guncellenmis_icerigi_kaydet": guncellenmis_icerigi_kaydet,
            "oturum_baslat": oturum_baslat,
            "oturum_display_name": oturum_display_name,
            "oturum_identifier": oturum_identifier,
            "son_yedek_yolu": son_yedek_yolu,
        }

    def _get_dosya_servisi(self):
        from app.services.dosya_servisi import read_text

        return {
            "read_text": read_text,
        }

    def _get_gecici_bildirim_servisi(self):
        from app.services.gecici_bildirim_servisi import gecici_bildirim_servisi
        return gecici_bildirim_servisi

    def _get_document_selection_class(self):
        from app.ui.dosya_secici_paketi.models import DocumentSelection
        return DocumentSelection

    def _get_replace_karar_servisi_class(self):
        from app.services.replace_karar_servisi import ReplaceKararServisi
        return ReplaceKararServisi

    def _get_replace_karar_popup_class(self):
        from app.ui.replace_karar_popup import ReplaceKararPopup
        return ReplaceKararPopup