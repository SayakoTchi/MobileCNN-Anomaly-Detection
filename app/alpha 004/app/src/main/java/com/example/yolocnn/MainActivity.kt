package com.example.yolocnn

import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import java.net.Inet4Address
import java.net.NetworkInterface

class MainActivity : AppCompatActivity() {

    private lateinit var yoloDetector: YoloDetector
    private lateinit var localServer: LocalServer

    private lateinit var floatingText: TextView
    private val handler = Handler(Looper.getMainLooper())
    private var dx = 7f
    private var dy = 7f

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        WindowInsetsControllerCompat(window, window.decorView).let { controller ->
            controller.hide(WindowInsetsCompat.Type.systemBars())
            controller.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
        val rootLayout = FrameLayout(this).apply {
            setBackgroundColor(Color.BLACK)
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        }

        val myIp = getLocalIpAddress()

        floatingText = TextView(this).apply {
            text = "$myIp:8080"
            setTextColor(Color.RED)
            textSize = 12f
            gravity = Gravity.CENTER
            setShadowLayer(8f, 0f, 0f, Color.parseColor("#FF0000"))

            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
            )
        }

        rootLayout.addView(floatingText)
        setContentView(rootLayout)

        yoloDetector = YoloDetector(this)
        localServer = LocalServer(this, yoloDetector)
        localServer.start()

        startDvdScreensaver(rootLayout)
    }

    private fun getLocalIpAddress(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            for (intf in interfaces) {
                val addrs = intf.inetAddresses
                for (addr in addrs) {
                    if (!addr.isLoopbackAddress && addr is Inet4Address) {
                        return addr.hostAddress ?: "IP_ERROR"
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return "127.0.0.1"
    }

    private fun startDvdScreensaver(rootLayout: FrameLayout) {
        floatingText.x = 100f
        floatingText.y = 100f

        val runnable = object : Runnable {
            override fun run() {
                val parentWidth = rootLayout.width.toFloat()
                val parentHeight = rootLayout.height.toFloat()
                val textWidth = floatingText.width.toFloat()
                val textHeight = floatingText.height.toFloat()

                if (parentWidth <= 0f || textWidth <= 0f) {
                    handler.postDelayed(this, 16)
                    return
                }

                var newX = floatingText.x + dx
                var newY = floatingText.y + dy

                if (newX <= 0f) {
                    newX = 0f
                    dx *= -1
                } else if (newX + textWidth >= parentWidth) {
                    newX = parentWidth - textWidth
                    dx *= -1
                }

                if (newY <= 0f) {
                    newY = 0f
                    dy *= -1
                } else if (newY + textHeight >= parentHeight) {
                    newY = parentHeight - textHeight
                    dy *= -1
                }

                floatingText.x = newX
                floatingText.y = newY

                handler.postDelayed(this, 16)
            }
        }
        handler.post(runnable)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
        localServer.stop()
        yoloDetector.close()
    }
}