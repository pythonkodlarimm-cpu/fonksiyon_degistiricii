package org.fy.bridge;

import android.app.Activity;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;

import androidx.annotation.NonNull;

import com.google.android.gms.ads.AdListener;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;

public class AdMobBridge {

    private static AdView banner;
    private static boolean initialized = false;

    public static void initialize(Activity activity) {
        activity.runOnUiThread(() -> {
            try {
                if (!initialized) {
                    MobileAds.initialize(activity);
                    initialized = true;
                    System.out.println("[ADMOB] MobileAds initialize tamam");
                } else {
                    System.out.println("[ADMOB] MobileAds zaten initialize");
                }
            } catch (Throwable t) {
                System.out.println("[ADMOB] initialize hatasi");
                t.printStackTrace();
            }
        });
    }

    public static void loadBanner(Activity activity, String adUnitId) {
        activity.runOnUiThread(() -> {
            try {
                System.out.println("[ADMOB] loadBanner basladi");
                System.out.println("[ADMOB] adUnitId = " + adUnitId);

                if (banner != null) {
                    System.out.println("[ADMOB] onceki banner temizleniyor");
                    if (banner.getParent() instanceof ViewGroup) {
                        ViewGroup parent = (ViewGroup) banner.getParent();
                        parent.removeView(banner);
                    }
                    banner.destroy();
                    banner = null;
                }

                banner = new AdView(activity);
                banner.setAdUnitId(adUnitId);
                banner.setAdSize(AdSize.BANNER);
                banner.setVisibility(View.VISIBLE);

                banner.setAdListener(new AdListener() {
                    @Override
                    public void onAdLoaded() {
                        System.out.println("[ADMOB] onAdLoaded");
                    }

                    @Override
                    public void onAdFailedToLoad(@NonNull LoadAdError adError) {
                        System.out.println("[ADMOB] onAdFailedToLoad");
                        System.out.println("[ADMOB] code = " + adError.getCode());
                        System.out.println("[ADMOB] message = " + adError.getMessage());
                        System.out.println("[ADMOB] response = " + adError.toString());
                    }

                    @Override
                    public void onAdImpression() {
                        System.out.println("[ADMOB] onAdImpression");
                    }

                    @Override
                    public void onAdOpened() {
                        System.out.println("[ADMOB] onAdOpened");
                    }

                    @Override
                    public void onAdClosed() {
                        System.out.println("[ADMOB] onAdClosed");
                    }

                    @Override
                    public void onAdClicked() {
                        System.out.println("[ADMOB] onAdClicked");
                    }
                });

                AdRequest request = new AdRequest.Builder().build();

                FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                        FrameLayout.LayoutParams.WRAP_CONTENT,
                        FrameLayout.LayoutParams.WRAP_CONTENT
                );
                params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;

                activity.addContentView(banner, params);
                System.out.println("[ADMOB] banner activity'ye eklendi");

                banner.loadAd(request);
                System.out.println("[ADMOB] loadAd cagrildi");

            } catch (Throwable t) {
                System.out.println("[ADMOB] loadBanner hatasi");
                t.printStackTrace();
            }
        });
    }

    public static void hideBanner(Activity activity) {
        activity.runOnUiThread(() -> {
            try {
                if (banner != null) {
                    banner.setVisibility(View.GONE);
                    System.out.println("[ADMOB] banner gizlendi");
                } else {
                    System.out.println("[ADMOB] hideBanner: banner null");
                }
            } catch (Throwable t) {
                System.out.println("[ADMOB] hideBanner hatasi");
                t.printStackTrace();
            }
        });
    }

    public static void showBanner(Activity activity) {
        activity.runOnUiThread(() -> {
            try {
                if (banner != null) {
                    banner.setVisibility(View.VISIBLE);
                    System.out.println("[ADMOB] banner gosterildi");

                    if (banner.getParent() == null) {
                        System.out.println("[ADMOB] showBanner: parent yok");
                    } else {
                        System.out.println("[ADMOB] showBanner: parent var -> " + banner.getParent().getClass().getName());
                    }
                } else {
                    System.out.println("[ADMOB] showBanner: banner null");
                }
            } catch (Throwable t) {
                System.out.println("[ADMOB] showBanner hatasi");
                t.printStackTrace();
            }
        });
    }

    public static void destroyBanner(Activity activity) {
        activity.runOnUiThread(() -> {
            try {
                if (banner != null) {
                    if (banner.getParent() instanceof ViewGroup) {
                        ViewGroup parent = (ViewGroup) banner.getParent();
                        parent.removeView(banner);
                    }
                    banner.destroy();
                    banner = null;
                    System.out.println("[ADMOB] banner yok edildi");
                } else {
                    System.out.println("[ADMOB] destroyBanner: banner null");
                }
            } catch (Throwable t) {
                System.out.println("[ADMOB] destroyBanner hatasi");
                t.printStackTrace();
            }
        });
    }
                    }
