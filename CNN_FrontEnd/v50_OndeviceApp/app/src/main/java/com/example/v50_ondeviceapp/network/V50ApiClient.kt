package com.example.v50_ondeviceapp.network

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

data class TimelineEvent(
    val time: String,
    val obj: String,
    val confidence: Float,
    val clipUrl: String,
    val anomaly: Boolean,
)

class V50ApiClient(baseUrl: String = "http://192.168.0.50:8080") {

    var baseUrl: String = baseUrl
        set(value) {
            field = value.trimEnd('/')
        }

    private val http = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .build()

    suspend fun ping(): String = withContext(Dispatchers.IO) {
        val req = Request.Builder().url("$baseUrl/ping").build()
        http.newCall(req).execute().use { res ->
            if (!res.isSuccessful) throw Exception("HTTP ${res.code}")
            res.body?.string() ?: "OK"
        }
    }

    suspend fun getTimeline(): List<TimelineEvent> = withContext(Dispatchers.IO) {
        val req = Request.Builder().url("$baseUrl/api/timeline").build()
        http.newCall(req).execute().use { res ->
            if (!res.isSuccessful) throw Exception("HTTP ${res.code}")
            val arr = JSONArray(res.body?.string() ?: "[]")
            (0 until arr.length()).map { i ->
                val obj = arr.getJSONObject(i)
                TimelineEvent(
                    time       = obj.optString("time", "-"),
                    obj        = obj.optString("object", "unknown"),
                    confidence = obj.optDouble("confidence", 0.0).toFloat(),
                    clipUrl    = obj.optString("clip_url", ""),
                    anomaly    = obj.optBoolean("anomaly", false),
                )
            }
        }
    }

    suspend fun updateConfig(threshold: Float): String = withContext(Dispatchers.IO) {
        val body = """{"threshold":$threshold}"""
            .toRequestBody("application/json".toMediaType())
        val req = Request.Builder().url("$baseUrl/api/config").post(body).build()
        http.newCall(req).execute().use { res ->
            val json = JSONObject(res.body?.string() ?: "{}")
            json.optString("msg", json.optString("message", "완료"))
        }
    }

    suspend fun swapModel(): String = withContext(Dispatchers.IO) {
        val req = Request.Builder()
            .url("$baseUrl/api/model/swap")
            .post("".toRequestBody())
            .build()
        http.newCall(req).execute().use { res ->
            res.body?.string() ?: "OK"
        }
    }

    fun clipImageUrl(clipUrl: String): String =
        if (clipUrl.startsWith("http")) clipUrl else "$baseUrl$clipUrl"
}
