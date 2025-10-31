package com.replyaisuggester

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

object PreferencesHelper {
    private const val PREFS_NAME = "reply_ai_prefs"
    private const val KEY_CONSENT_GIVEN = "consent_given"
    private const val KEY_PERSONALIZATION_ENABLED = "personalization_enabled"

    private fun getEncryptedPrefs(context: Context): SharedPreferences {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        return EncryptedSharedPreferences.create(
            context,
            PREFS_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun isConsentGiven(context: Context): Boolean {
        return getEncryptedPrefs(context).getBoolean(KEY_CONSENT_GIVEN, false)
    }

    fun setConsentGiven(context: Context, given: Boolean) {
        getEncryptedPrefs(context).edit().putBoolean(KEY_CONSENT_GIVEN, given).apply()
    }

    fun isPersonalizationEnabled(context: Context): Boolean {
        return getEncryptedPrefs(context).getBoolean(KEY_PERSONALIZATION_ENABLED, false)
    }

    fun setPersonalizationEnabled(context: Context, enabled: Boolean) {
        getEncryptedPrefs(context).edit().putBoolean(KEY_PERSONALIZATION_ENABLED, enabled).apply()
    }

    fun clearAllData(context: Context) {
        getEncryptedPrefs(context).edit().clear().apply()
    }
}