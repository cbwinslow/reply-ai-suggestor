package com.replyaisuggester

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import kotlinx.coroutines.delay
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong
import org.json.JSONObject

data class Suggestion(val text: String, val tone: String)

object NetworkClient {
    // Use emulator host mapping for localhost during development: 10.0.2.2
    private const val BASE_URL = "http://10.0.2.2:8000"
    private const val SUGGEST_URL = "$BASE_URL/suggest"
    private const val UPLOAD_URL = "$BASE_URL/upload_personalization"
    private const val DELETE_URL = "$BASE_URL/delete_personalization"

    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(5, TimeUnit.SECONDS)
        .writeTimeout(5, TimeUnit.SECONDS)
        .build()

    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    // Throttling: allow 1 request per 5 seconds
    private val lastRequestTime = AtomicLong(0)
    private const val THROTTLE_DELAY_MS = 5000L

    // Simple cache: context -> suggestions
    private val cache = mutableMapOf<String, List<Suggestion>>()
    private const val MAX_CACHE_SIZE = 50

    suspend fun postSuggest(userId: String, context: String, modes: List<String>, intensity: Int, provider: String = "mock"): List<Suggestion> {
        // Check cache first
        val cacheKey = "$context-${modes.joinToString()}-$intensity-$provider"
        cache[cacheKey]?.let { return it }

        // Throttling
        val now = System.currentTimeMillis()
        val last = lastRequestTime.get()
        if (now - last < THROTTLE_DELAY_MS) {
            delay(THROTTLE_DELAY_MS - (now - last))
        }
        lastRequestTime.set(System.currentTimeMillis())

        // Retry with backoff
        var attempt = 0
        val maxAttempts = 3
        while (attempt < maxAttempts) {
            try {
                val result = performRequest(userId, context, modes, intensity, provider)
                // Cache the result
                if (cache.size >= MAX_CACHE_SIZE) {
                    cache.remove(cache.keys.first())
                }
                cache[cacheKey] = result
                return result
            } catch (e: Exception) {
                attempt++
                if (attempt >= maxAttempts) throw e
                delay(1000L * attempt) // Exponential backoff
            }
        }
        return listOf(Suggestion("(network error)", "error"))
    }

    private suspend fun performRequest(userId: String, context: String, modes: List<String>, intensity: Int, provider: String): List<Suggestion> {
        return withContext(Dispatchers.IO) {
            val payload = JSONObject().apply {
                put("user_id", userId)
                put("context", context)
                put("modes", modes)
                put("intensity", intensity)
                put("provider", provider)
            }
            val requestBody = payload.toString().toRequestBody(jsonMediaType)
            val request = Request.Builder()
                .url(SUGGEST_URL)
                .post(requestBody)
                .build()

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    throw Exception("HTTP ${response.code}")
                }

                val responseBody = response.body?.string()
                    ?: throw Exception("Empty response")

                val json = JSONObject(responseBody)
                val arr = json.getJSONArray("suggestions")
                val outList = mutableListOf<Suggestion>()
                for (i in 0 until arr.length()) {
                    val item = arr.getJSONObject(i)
                    val text = item.getString("text")
                    val tone = item.getString("tone")
                    outList.add(Suggestion(text, tone))
                }
                outList
            }
        }
    }

    suspend fun uploadPersonalization(userId: String, base64Payload: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val payload = JSONObject().apply {
                    put("user_id", userId)
                    put("artifacts", JSONObject().put("export", base64Payload))
                }

                val requestBody = payload.toString().toRequestBody(jsonMediaType)
                val request = Request.Builder()
                    .url(UPLOAD_URL)
                    .post(requestBody)
                    .build()

                client.newCall(request).execute().use { response ->
                    response.isSuccessful
                }
            } catch (e: Exception) {
                false
            }
        }
    }

    suspend fun deletePersonalization(userId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val payload = JSONObject().apply {
                    put("user_id", userId)
                }

                val requestBody = payload.toString().toRequestBody(jsonMediaType)
                val request = Request.Builder()
                    .url(DELETE_URL)
                    .post(requestBody)
                    .build()

                client.newCall(request).execute().use { response ->
                    response.isSuccessful
                }
            } catch (e: Exception) {
                false
            }
        }
    }
}
