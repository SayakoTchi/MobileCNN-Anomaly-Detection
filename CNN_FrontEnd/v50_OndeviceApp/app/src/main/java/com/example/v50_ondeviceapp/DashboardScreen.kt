package com.example.v50_ondeviceapp

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.v50_ondeviceapp.network.TimelineEvent
import com.example.v50_ondeviceapp.network.V50ApiClient
import kotlinx.coroutines.launch

@Composable
fun DashboardScreen(client: V50ApiClient, onDisconnect: () -> Unit) {
    val scope = rememberCoroutineScope()

    var nodeStatus by remember { mutableStateOf("확인 중...") }
    var isOnline by remember { mutableStateOf(false) }
    var timeline by remember { mutableStateOf<List<TimelineEvent>>(emptyList()) }
    var notice by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }

    fun refreshTimeline() {
        isLoading = true
        scope.launch {
            try {
                timeline = client.getTimeline()
                notice = "타임라인 갱신 완료 (${timeline.size}건)"
            } catch (e: Exception) {
                notice = "갱신 실패: ${e.message}"
            } finally {
                isLoading = false
            }
        }
    }

    LaunchedEffect(Unit) {
        try {
            client.ping()
            isOnline = true
            nodeStatus = "Online"
        } catch (e: Exception) {
            isOnline = false
            nodeStatus = "Offline"
        }
        refreshTimeline()
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Color(0xFF121212)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {

            // 상단 헤더
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1E1E1E))
                    .padding(horizontal = 20.dp, vertical = 14.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("AI 경비원 대시보드", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
                    Text(client.baseUrl, fontSize = 11.sp, color = Color(0xFF888888))
                }
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Box(
                        modifier = Modifier
                            .background(
                                if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                                RoundedCornerShape(12.dp)
                            )
                            .padding(horizontal = 10.dp, vertical = 4.dp)
                    ) {
                        Text(nodeStatus, fontSize = 11.sp, color = Color.White, fontWeight = FontWeight.Bold)
                    }
                    TextButton(onClick = onDisconnect) {
                        Text("연결 해제", fontSize = 11.sp, color = Color(0xFF888888))
                    }
                }
            }

            // 알림 배너
            if (notice.isNotBlank()) {
                Text(
                    text = notice,
                    fontSize = 12.sp,
                    color = Color(0xFF4FC3F7),
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFF1A2733))
                        .padding(horizontal = 20.dp, vertical = 8.dp)
                )
            }

            // 액션 버튼들
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Button(
                    onClick = { refreshTimeline() },
                    enabled = !isLoading,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E88E5))
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(modifier = Modifier.size(16.dp), color = Color.White, strokeWidth = 2.dp)
                    } else {
                        Text("타임라인 갱신", fontSize = 13.sp)
                    }
                }
                OutlinedButton(
                    onClick = {
                        scope.launch {
                            try {
                                val msg = client.swapModel()
                                notice = "모델 교체: $msg"
                            } catch (e: Exception) {
                                notice = "교체 실패: ${e.message}"
                            }
                        }
                    },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF888888)),
                    border = ButtonDefaults.outlinedButtonBorder.copy(
                        brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF444444))
                    )
                ) {
                    Text("모델 교체", fontSize = 13.sp)
                }
            }

            // 타임라인 헤더
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("이벤트 타임라인", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
                Text("${timeline.size}건", fontSize = 12.sp, color = Color(0xFF888888))
            }

            HorizontalDivider(color = Color(0xFF2A2A2A), modifier = Modifier.padding(horizontal = 16.dp))

            // 타임라인 목록
            if (timeline.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "이벤트 없음",
                        fontSize = 14.sp,
                        color = Color(0xFF555555)
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(timeline) { event ->
                        EventCard(event)
                    }
                }
            }
        }
    }
}

@Composable
private fun EventCard(event: TimelineEvent) {
    val borderColor = if (event.anomaly) Color(0xFFEF5350) else Color(0xFF388E3C)
    val badgeColor  = if (event.anomaly) Color(0xFFEF5350) else Color(0xFF388E3C)
    val badgeText   = if (event.anomaly) "ANOMALY" else "NORMAL"

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E)),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 12.dp)
        ) {
            // 왼쪽 컬러 바
            Box(
                modifier = Modifier
                    .width(3.dp)
                    .height(72.dp)
                    .background(borderColor, RoundedCornerShape(2.dp))
            )
            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 12.dp, vertical = 10.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(event.obj, fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = Color.White)
                    Box(
                        modifier = Modifier
                            .background(badgeColor, RoundedCornerShape(4.dp))
                            .padding(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        Text(badgeText, fontSize = 10.sp, color = Color.White, fontWeight = FontWeight.Bold)
                    }
                }
                Spacer(Modifier.height(4.dp))
                Text(event.time, fontSize = 11.sp, color = Color(0xFF888888))
                Text(
                    "신뢰도: ${(event.confidence * 100).toInt()}%",
                    fontSize = 11.sp,
                    color = Color(0xFF4FC3F7)
                )
            }
        }
    }
}
