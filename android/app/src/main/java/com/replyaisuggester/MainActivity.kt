package com.replyaisuggester

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ReplyAISuggesterApp()
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReplyAISuggesterApp() {
    var input by remember { mutableStateOf("") }
    var suggestions by remember { mutableStateOf(listOf<String>()) }

    MaterialTheme {
        Scaffold(topBar = {
            TopAppBar(title = { Text("Reply AI Suggester") })
        }) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = input,
                    onValueChange = { input = it },
                    label = { Text("Conversation context") },
                    modifier = Modifier.fillMaxWidth()
                )

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = {
                        // Call backend in background thread. Use emulator host 10.0.2.2 for local dev.
                        suggestions = listOf("Generating...")
                        Thread {
                            val result = NetworkClient.postSuggest(
                                userId = "dev_user",
                                context = input,
                                modes = listOf("casual", "formal", "witty"),
                                intensity = 6
                            )
                            // Post results back to UI thread
                            (androidx.compose.ui.platform.LocalContext.current as? android.app.Activity)?.runOnUiThread {
                                suggestions = result
                            }
                        }.start()
                    }) {
                        Text("Generate suggestions")
                    }
                    Button(onClick = { /* Open settings activity */ }) {
                        Text("Settings")
                    }
                }

                Text("Suggestions:", style = MaterialTheme.typography.titleMedium)
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    suggestions.forEach { s ->
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Text(s, modifier = Modifier.padding(12.dp))
                        }
                    }
                }

                Spacer(modifier = Modifier.weight(1f))
                Text("Note: This is an app skeleton. Integrate keyboard/IMService and backend next.")
            }
        }
    }
}
