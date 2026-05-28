package com.example.yolocnn

import android.content.Context
import android.graphics.BitmapFactory
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.http.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File

class LocalServer(private val appContext: Context, private val yoloDetector: YoloDetector) {

    private val server = embeddedServer(Netty, port = 8080) {
        routing {
            get("/ping") {
                call.respondText("Node is good")
            }

            post("/api/config") {
                yoloDetector.threshold = 0.7f
                call.respondText("""{"status":"success", "msg":"Changed settings"}""")
            }

            post("/api/detect") {
                try {
                    val imageBytes = call.receive<ByteArray>()
                    val bitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)

                    if (bitmap != null) {
                        val resultJson = yoloDetector.detectAndLog(bitmap)
                        call.respondText(resultJson, ContentType.Application.Json)
                    } else {
                        call.respondText("{\"status\": \"error\", \"msg\": \"이미지 깨짐\"}", status = HttpStatusCode.BadRequest)
                    }
                } catch (e: Exception) {
                    call.respondText("{\"status\": \"error\", \"msg\": \"${e.message}\"}")
                }
            }

            get("/api/timeline") {
                val logFile = File(appContext.filesDir, "timeline.jsonl")
                if (logFile.exists()) {
                    val logs = logFile.readLines().joinToString(",", "[", "]")
                    call.respondText(logs, ContentType.Application.Json)
                } else {
                    call.respondText("[]", ContentType.Application.Json)
                }
            }

            get("/api/clip/{fileName}") {
                val fileName = call.parameters["fileName"]
                val file = File(appContext.filesDir, fileName)
                if (file.exists()) {
                    call.respondFile(file)
                } else {
                    call.respond(HttpStatusCode.NotFound, "CLip file not found")
                }
            }

            post("/api/model/swap") {
                val modelFile = File(appContext.filesDir, "new_model.tflite")
                yoloDetector.loadOrSwapModel(modelFile.absolutePath)
                call.respondText("Model changed")
            }
        }
    }

    fun start() {
        CoroutineScope(Dispatchers.IO).launch {
            println(":8080 Backend opned")
            server.start(wait = true)
        }
    }

    fun stop() {
        server.stop(1000, 2000)
    }
}