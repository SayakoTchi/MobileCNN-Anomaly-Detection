package com.example.v50_ondeviceapp

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.v50_ondeviceapp.network.V50ApiClient
import kotlinx.coroutines.launch

private const val NODE_URL = "http://192.168.216.133:8080"

@Composable
fun ConnectScreen(onConnected: (V50ApiClient) -> Unit) {
    val scope = rememberCoroutineScope()
    val client = remember { V50ApiClient(NODE_URL) }

    var status by remember { mutableStateOf("연결 버튼을 눌러 노드 상태를 확인하세요.") }
    var isLoading by remember { mutableStateOf(false) }
    var isError by remember { mutableStateOf(false) }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Color(0xFF121212)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(32.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "서랍 속 AI 경비원",
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
            )
            Text(
                text = "관리자 앱",
                fontSize = 14.sp,
                color = Color(0xFF888888),
                modifier = Modifier.padding(bottom = 48.dp)
            )

            // 노드 주소 표시 (고정)
            Surface(
                color = Color(0xFF1E1E1E),
                shape = MaterialTheme.shapes.medium,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("노드 주소", fontSize = 11.sp, color = Color(0xFF888888))
                    Spacer(Modifier.height(4.dp))
                    Text(NODE_URL, fontSize = 15.sp, color = Color(0xFF4FC3F7), fontWeight = FontWeight.Medium)
                }
            }

            Spacer(Modifier.height(24.dp))

            Button(
                onClick = {
                    isLoading = true
                    isError = false
                    status = "연결 확인 중..."
                    scope.launch {
                        try {
                            val msg = client.ping()
                            status = "연결 성공: $msg"
                            onConnected(client)
                        } catch (e: Exception) {
                            isError = true
                            status = "연결 실패: ${e.message}"
                        } finally {
                            isLoading = false
                        }
                    }
                },
                enabled = !isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4FC3F7),
                    contentColor = Color.Black
                )
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = Color.Black,
                        strokeWidth = 2.dp
                    )
                } else {
                    Text("연결 확인", fontWeight = FontWeight.Bold)
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            Text(
                text = status,
                fontSize = 13.sp,
                color = if (isError) Color(0xFFEF5350) else Color(0xFF81C784),
            )
        }
    }
}
