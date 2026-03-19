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
        FrameLayoutParams = autoclass("android.widget.FrameLayout$LayoutParams")
        Gravity = autoclass("android.view.Gravity")

        activity = PythonActivity.mActivity

        MobileAds.initialize(activity)

        adview = AdView(activity)

        # TEST banner
        adview.setAdUnitId("ca-app-pub-3940256099942544/9214589741")
        adview.setAdSize(AdSize.BANNER)

        params = FrameLayoutParams(
            FrameLayoutParams.MATCH_PARENT,
            FrameLayoutParams.WRAP_CONTENT,
        )
        params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL

        activity.addContentView(adview, params)

        ad_request = AdRequestBuilder().build()
        adview.loadAd(ad_request)

        print("[ADMOB] Banner altta yüklendi")

    except Exception as e:
        print("[ADMOB] HATA:", e)
