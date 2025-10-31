package com.replyaisuggester

import android.content.Context
import android.content.SharedPreferences
import android.util.Base64
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import org.json.JSONArray
import org.json.JSONObject

/**
 * Personalization store using Jetpack Security EncryptedSharedPreferences for secure local storage.
 * Stores user consent and example messages for personalization.
 */
class PersonalizationStore(private val context: Context) {
    private val prefsName = "reply_ai_personalization"
    private val prefs: SharedPreferences by lazy {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            context,
            prefsName,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun setConsent(consented: Boolean) {
        prefs.edit().putBoolean("consent", consented).apply()
    }

    fun hasConsent(): Boolean = prefs.getBoolean("consent", false)

    fun saveExample(exampleId: String, contextText: String, responseText: String) {
        val examples = getExamples().toMutableList()
        val entry = JSONObject().apply {
            put("id", exampleId)
            put("context", contextText)
            put("response", responseText)
            put("ts", System.currentTimeMillis())
        }
        examples.add(entry)
        val arr = JSONArray(examples)
        prefs.edit().putString("examples", arr.toString()).apply()
    }

    fun getExamples(): List<JSONObject> {
        val raw = prefs.getString("examples", null) ?: return emptyList()
        return try {
            val arr = JSONArray(raw)
            (0 until arr.length()).map { i -> arr.getJSONObject(i) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun clearPersonalization() {
        prefs.edit().remove("examples").apply()
    }

    fun exportPersonalization(): String {
        val obj = JSONObject()
        obj.put("consent", hasConsent())
        obj.put("examples", JSONArray(getExamples()))
        // Base64-encode for safe transfer as a string
        return Base64.encodeToString(obj.toString().toByteArray(Charsets.UTF_8), Base64.NO_WRAP)
    }
}

    fun setConsent(consented: Boolean) {
        prefs.edit().putBoolean("consent", consented).apply()
    }

    fun hasConsent(): Boolean = prefs.getBoolean("consent", false)

    fun saveExample(exampleId: String, contextText: String, responseText: String) {
        val examples = getExamples().toMutableList()
        val entry = JSONObject().apply {
            put("id", exampleId)
            put("context", contextText)
            put("response", responseText)
            put("ts", System.currentTimeMillis())
        }
        examples.add(entry)
        val arr = JSONArray(examples)
        prefs.edit().putString("examples", arr.toString()).apply()
    }

    fun getExamples(): List<JSONObject> {
        val raw = prefs.getString("examples", null) ?: return emptyList()
        return try {
            val arr = JSONArray(raw)
            (0 until arr.length()).map { i -> arr.getJSONObject(i) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun clearPersonalization() {
        prefs.edit().remove("examples").apply()
    }

    fun exportPersonalization(): String {
        val obj = JSONObject()
        obj.put("consent", hasConsent())
        obj.put("examples", JSONArray(getExamples()))
        // Base64-encode for safe transfer as a string
        return Base64.encodeToString(obj.toString().toByteArray(Charsets.UTF_8), Base64.NO_WRAP)
    }
}
