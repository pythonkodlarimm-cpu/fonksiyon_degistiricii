package org.fy.bridge;

import android.app.Activity;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;

import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
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
                }
            } catch (Throwable t) {
                t.printStackTrace();
            }
        });
    }

    public static void loadBanner(Activity activity, String adUnitId) {
        activity.runOnUiThread(() -> {
            try {
                if (banner != null) {
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

                AdRequest request = new AdRequest.Builder().build();

                FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                        FrameLayout.LayoutParams.WRAP_CONTENT,
                        FrameLayout.LayoutParams.WRAP_CONTENT
                );
                params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;

                activity.addContentView(banner, params);
                banner.loadAd(request);

            } catch (Throwable t) {
                t.printStackTrace();
            }
        });
    }

    public static void hideBanner(Activity activity) {
        activity.runOnUiThread(() -> {
            try {
                if (banner != null) {
                    banner.setVisibility(View.GONE);
                }
            } catch (Throwable t) {
                t.printStackTrace();
            }
        });
    }

    public static void showBanner(Activity activity) {
        activity.runOnUiThread(() -> {
            try {
                if (banner != null) {
                    banner.setVisibility(View.VISIBLE);
                }
            } catch (Throwable t) {
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
                }
            } catch (Throwable t) {
                t.printStackTrace();
            }
        });
    }
}
