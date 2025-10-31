package com.replyaisuggester

import org.json.JSONObject
import java.io.BufferedOutputStream
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

object NetworkClient {
    // Use emulator host mapping for localhost during development: 10.0.2.2
    private const val SUGGEST_URL = "http://10.0.2.2:8000/suggest"

    fun postSuggest(userId: String, context: String, modes: List<String>, intensity: Int): List<String> {
        val url = URL(SUGGEST_URL)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
            doOutput = true
            connectTimeout = 5000
            readTimeout = 5000
        }

        val payload = JSONObject().apply {
            put("user_id", userId)
            put("context", context)
            put("modes", modes)
            put("intensity", intensity)
        }

        try {
            BufferedOutputStream(conn.outputStream).use { out ->
                val bytes = payload.toString().toByteArray(Charsets.UTF_8)
                out.write(bytes)
                out.flush()
            }

            val code = conn.responseCode
            if (code !in 200..299) {
                // Return a fallback suggestion on error
                return listOf("(error contacting backend: $code)")
            }

            val resp = StringBuilder()
            BufferedReader(InputStreamReader(conn.inputStream)).use { reader ->
                var line: String? = reader.readLine()
                while (line != null) {
                    resp.append(line)
                    line = reader.readLine()
                }
            }

            val json = JSONObject(resp.toString())
            val arr = json.getJSONArray("suggestions")
            val outList = mutableListOf<String>()
            for (i in 0 until arr.length()) {
                outList.add(arr.getString(i))
            }
            return outList
        } catch (e: Exception) {
            return listOf("(network error: ${e.message ?: "unknown"})")
        } finally {
            conn.disconnect()
        }
    }

    fun uploadPersonalization(userId: String, base64Payload: String): Boolean {
        val url = URL("http://10.0.2.2:8000/upload_personalization")
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
            doOutput = true
            connectTimeout = 5000
            readTimeout = 5000
        }

        val payload = JSONObject().apply {
            put("user_id", userId)
            put("artifacts", JSONObject().put("export", base64Payload))
        }

        return try {
            BufferedOutputStream(conn.outputStream).use { out ->
                val bytes = payload.toString().toByteArray(Charsets.UTF_8)
                out.write(bytes)
                out.flush()
            }
            conn.responseCode in 200..299
        } catch (e: Exception) {
            false
        } finally {
            conn.disconnect()
        }
    }

    fun deletePersonalization(userId: String): Boolean {
        val url = URL("http://10.0.2.2:8000/delete_personalization")
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
            doOutput = true
            connectTimeout = 5000
            readTimeout = 5000
        }
        val payload = JSONObject().apply { put("user_id", userId) }
        return try {
            BufferedOutputStream(conn.outputStream).use { out ->
                val bytes = payload.toString().toByteArray(Charsets.UTF_8)
                out.write(bytes)
                out.flush()
            }
            conn.responseCode in 200..299
        } catch (e: Exception) {
            false
        } finally {
            conn.disconnect()
        }
    }
}
