package com.example.yolocnn

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.CompatibilityList
import org.tensorflow.lite.gpu.GpuDelegate
import java.io.File
import java.io.FileOutputStream
import java.io.FileInputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

class YoloDetector(private val context: Context) {
    var threshold = 0.5f
    var targetClasses = listOf("person", "anomaly_obj")
    var isClipSaveEnabled = true
    private var interpreter: Interpreter? = null
    private val options = Interpreter.Options()

    init {
        val compatList = CompatibilityList()
        if (compatList.isDelegateSupportedOnThisDevice) {
            options.addDelegate(GpuDelegate(compatList.bestOptionsForThisDevice))
        } else {
            options.setNumThreads(4)
        }
    }

    private fun loadModelFromFile(filePath: String): MappedByteBuffer {
        val file = File(filePath)
        if (!file.exists()) {
            throw IllegalArgumentException("Models not found: $filePath")
        }
        val fileInputStream = FileInputStream(file)
        val fileChannel = fileInputStream.channel
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, 0, file.length())
    }

    fun loadOrSwapModel(newModelPath: String) {
        interpreter?.close()
        try {
            val newModelBuffer = loadModelFromFile(newModelPath)
            interpreter = Interpreter(newModelBuffer, options)
            println("Model Changed: $newModelPath")
        } catch (e: Exception) {
            println("[Error] Model change failed: ${e.message}")
        }
    }

    fun detect(bitmap: Bitmap) {
        if (interpreter == null) {
            println("[WARN] Model not changed yet, skipping frames")
            return
        }
        val resizedBitmap = Bitmap.createScaledBitmap(bitmap, 640, 640, true)
        val inputBuffer = convertBitmapToByteBuffer(resizedBitmap)
        val outputBuffer = Array(1) { Array(84) { FloatArray(8400) } }

        interpreter?.run(inputBuffer, outputBuffer)
    }

    private fun convertBitmapToByteBuffer(bitmap: Bitmap): ByteBuffer {
        val byteBuffer = ByteBuffer.allocateDirect(640 * 640 * 3 * 4)
        byteBuffer.order(ByteOrder.nativeOrder())
        val intValues = IntArray(640 * 640)
        bitmap.getPixels(intValues, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)

        var pixel = 0
        for (i in 0 until 640) {
            for (j in 0 until 640) {
                val valPixel = intValues[pixel++]
                byteBuffer.putFloat(((valPixel shr 16 and 0xFF) / 255.0f))
                byteBuffer.putFloat(((valPixel shr 8 and 0xFF) / 255.0f))
                byteBuffer.putFloat(((valPixel and 0xFF) / 255.0f))
            }
        }
        return byteBuffer
    }

    fun detectAndLog(bitmap: Bitmap): String {
        val detectedClass = "person"
        val confidence = 0.85f

        var anomalyDetected = false
        var savedClipName = ""

        if (targetClasses.contains(detectedClass) && confidence >= threshold) {
            anomalyDetected = true
            if (isClipSaveEnabled) {
                savedClipName = saveClipToStorage(bitmap)
                saveToTimelineDB(detectedClass, confidence, savedClipName)
            }
        }
        return """{"anomaly": $anomalyDetected, "class": "$detectedClass", "clip": "$savedClipName"}"""
    }

    private fun saveClipToStorage(bitmap: Bitmap): String {
        val timeStamp = SimpleDateFormat("yyyyMMdd_HHmmss").format(Date())
        val fileName = "anomaly_clip_${timeStamp}.jpg"
        val file = File(context.filesDir, fileName)

        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
        }
        println("[System] Anomaly Clip saved: $fileName")
        return fileName
    }

    private fun saveToTimelineDB(obj: String, conf: Float, clipName: String) {
        val logFile = File(context.filesDir, "timeline.jsonl")
        val timeStamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(Date())
        val logData = """{"time": "$timeStamp", "object": "$obj", "confidence": $conf, "clip_url": "/api/clip/$clipName"}""" + "\n"
        logFile.appendText(logData)
    }

    fun close() {
        interpreter?.close()
        interpreter = null
    }
}