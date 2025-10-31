package com.replyaisuggester

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

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

    suspend fun postSuggest(userId: String, context: String, modes: List<String>, intensity: Int): List<String> {
        return withContext(Dispatchers.IO) {
            try {
                val payload = JSONObject().apply {
                    put("user_id", userId)
                    put("context", context)
                    put("modes", modes)
                    put("intensity", intensity)
                }

                val requestBody = payload.toString().toRequestBody(jsonMediaType)
                val request = Request.Builder()
                    .url(SUGGEST_URL)
                    .post(requestBody)
                    .build()

                client.newCall(request).execute().use { response ->
                    if (!response.isSuccessful) {
                        return@withContext listOf("(error contacting backend: ${response.code})")
                    }

                    val responseBody = response.body?.string()
                        ?: return@withContext listOf("(empty response from backend)")

                    val json = JSONObject(responseBody)
                    val arr = json.getJSONArray("suggestions")
                    val outList = mutableListOf<String>()
                    for (i in 0 until arr.length()) {
                        outList.add(arr.getString(i))
                    }
                    outList
                }
            } catch (e: Exception) {
                listOf("(network error: ${e.message ?: "unknown"})")
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
