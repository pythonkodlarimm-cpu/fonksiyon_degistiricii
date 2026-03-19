# -*- coding: utf-8 -*-
from jnius import autoclass
from android.runnable import run_on_ui_thread


@run_on_ui_thread
def show_banner():
    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        AdView = autoclass("com.google.android.gms.ads.AdView")
        AdSize = autoclass("com.google.android.gms.ads.AdSize")
        AdRequestBuilder = autoclass("com.google.android.gms.ads.AdRequest$Builder")
        MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
        LinearLayout = autoclass("android.widget.LinearLayout")
        LayoutParams = autoclass("android.widget.LinearLayout$LayoutParams")

        activity = PythonActivity.mActivity

        # AdMob başlat
        MobileAds.initialize(activity)

        # Banner oluştur
        adview = AdView(activity)

        # ⚠️ TEST ID (ilk testte bunu kullan)
        adview.setAdUnitId("ca-app-pub-3940256099942544/9214589741")

        adview.setAdSize(AdSize.BANNER)

        # Layout
        layout = LinearLayout(activity)
        layout.setOrientation(LinearLayout.VERTICAL)

        params = LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.WRAP_CONTENT
        )

        layout.addView(adview, params)

        # Root view al
        root = activity.getWindow().getDecorView().getRootView()

        activity.addContentView(layout, params)

        # Reklam yükle
        ad_request = AdRequestBuilder().build()
        adview.loadAd(ad_request)

    except Exception as e:
        print("AdMob hata:", e)