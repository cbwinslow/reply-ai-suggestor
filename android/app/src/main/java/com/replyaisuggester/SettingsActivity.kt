package com.replyaisuggester

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import android.widget.Toast
import android.content.ClipboardManager
import android.content.ClipData
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class SettingsActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SettingsScreen()
        }
    }
}

@Composable
fun SettingsScreen() {
    val context = LocalContext.current
    val store = remember { PersonalizationStore(context) }
    var consent by remember { mutableStateOf(store.hasConsent()) }
    var intensity by remember { mutableStateOf(5f) }
    var statusMessage by remember { mutableStateOf("") }

    MaterialTheme {
        Column(modifier = Modifier
            .fillMaxSize()
            .padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("Settings", style = MaterialTheme.typography.titleLarge)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Checkbox(checked = consent, onCheckedChange = {
                    consent = it
                    store.setConsent(it)
                    statusMessage = if (it) "Consent granted" else "Consent revoked"
                })
                Text("I consent to local message processing for personalization")
            }

            Text("Intensity: ${intensity.toInt()}")
            Slider(value = intensity, onValueChange = { intensity = it }, valueRange = 0f..10f)

            Text("Data controls")
            Button(onClick = { /* Export or delete data */ }) {
                Text("Delete my personalization data")
            }

            // Export / Upload / Delete actions
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = {
                    // Export: copy exported base64 to clipboard
                    val exported = store.exportPersonalization()
                    val clipboard = context.getSystemService(ClipboardManager::class.java)
                    clipboard.setPrimaryClip(ClipData.newPlainText("export", exported))
                    statusMessage = "Export copied to clipboard"
                    Toast.makeText(context, "Export copied to clipboard", Toast.LENGTH_SHORT).show()
                }) {
                    Text("Export")
                }

                Button(onClick = {
                    // Upload in background
                    CoroutineScope(Dispatchers.IO).launch {
                        val exported = store.exportPersonalization()
                        val success = NetworkClient.uploadPersonalization("dev_user", exported)
                        CoroutineScope(Dispatchers.Main).launch {
                            statusMessage = if (success) "Uploaded personalization" else "Upload failed"
                            Toast.makeText(context, statusMessage, Toast.LENGTH_SHORT).show()
                        }
                    }
                }) {
                    Text("Upload")
                }

                Button(onClick = {
                    // Delete both local and server-side
                    CoroutineScope(Dispatchers.IO).launch {
                        val serverDeleted = NetworkClient.deletePersonalization("dev_user")
                        store.clearPersonalization()
                        CoroutineScope(Dispatchers.Main).launch {
                            statusMessage = "Deleted local data" + if (serverDeleted) ", server deletion OK" else ", server deletion failed"
                            Toast.makeText(context, statusMessage, Toast.LENGTH_SHORT).show()
                        }
                    }
                }) {
                    Text("Delete")
                }
            }

            if (statusMessage.isNotEmpty()) {
                Text(statusMessage)
            }

            Spacer(modifier = Modifier.weight(1f))
        }
    }
}
