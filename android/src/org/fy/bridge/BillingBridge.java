package org.fy.bridge;

import android.app.Activity;

import com.android.billingclient.api.*;

import java.util.List;

public class BillingBridge {

    private static BillingClient billingClient;
    private static boolean premiumActive = false;

    // ---------------------------------------------------------
    // INIT BILLING
    // ---------------------------------------------------------
    public static void init(Activity activity) {

        billingClient = BillingClient.newBuilder(activity)
                .enablePendingPurchases()
                .setListener(new PurchasesUpdatedListener() {
                    @Override
                    public void onPurchasesUpdated(
                            BillingResult billingResult,
                            List<Purchase> purchases
                    ) {

                        if (billingResult.getResponseCode()
                                == BillingClient.BillingResponseCode.OK
                                && purchases != null) {

                            for (Purchase purchase : purchases) {

                                if (purchase.getPurchaseState()
                                        == Purchase.PurchaseState.PURCHASED) {

                                    premiumActive = true;

                                }
                            }
                        }
                    }
                })
                .build();

        billingClient.startConnection(new BillingClientStateListener() {

            @Override
            public void onBillingSetupFinished(BillingResult billingResult) {

                if (billingResult.getResponseCode()
                        == BillingClient.BillingResponseCode.OK) {

                    queryPurchases();
                }
            }

            @Override
            public void onBillingServiceDisconnected() {

                premiumActive = false;

            }
        });
    }

    // ---------------------------------------------------------
    // RESTORE PURCHASES
    // ---------------------------------------------------------
    public static void queryPurchases() {

        if (billingClient == null) return;

        billingClient.queryPurchasesAsync(
                QueryPurchasesParams.newBuilder()
                        .setProductType(BillingClient.ProductType.SUBS)
                        .build(),
                new PurchasesResponseListener() {

                    @Override
                    public void onQueryPurchasesResponse(
                            BillingResult billingResult,
                            List<Purchase> purchases
                    ) {

                        if (billingResult.getResponseCode()
                                == BillingClient.BillingResponseCode.OK) {

                            premiumActive = false;

                            for (Purchase purchase : purchases) {

                                if (purchase.getPurchaseState()
                                        == Purchase.PurchaseState.PURCHASED) {

                                    premiumActive = true;

                                }
                            }
                        }
                    }
                }
        );
    }

    // ---------------------------------------------------------
    // PREMIUM STATUS
    // ---------------------------------------------------------
    public static boolean isPremiumActive() {

        return premiumActive;

    }
}