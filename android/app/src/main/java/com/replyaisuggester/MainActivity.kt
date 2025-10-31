package com.replyaisuggester

import android.content.Intent
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
    val context = androidx.compose.ui.platform.LocalContext.current
    var showConsentDialog by remember { mutableStateOf(!PreferencesHelper.isConsentGiven(context)) }
    var input by remember { mutableStateOf("") }
    var suggestions by remember { mutableStateOf(listOf<String>()) }

    if (showConsentDialog) {
        AlertDialog(
            onDismissRequest = { /* Prevent dismissal */ },
            title = { Text("Privacy Consent") },
            text = {
                Text(
                    "This app accesses your typing to provide reply suggestions. " +
                    "With your consent, we can personalize suggestions by storing anonymized data locally. " +
                    "You can opt-out anytime in settings. Do you consent?"
                )
            },
            confirmButton = {
                Button(onClick = {
                    PreferencesHelper.setConsentGiven(context, true)
                    showConsentDialog = false
                }) {
                    Text("Accept")
                }
            },
            dismissButton = {
                Button(onClick = {
                    // Exit app
                    (context as? ComponentActivity)?.finish()
                }) {
                    Text("Decline")
                }
            }
        )
    } else {
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
                                intensity = 6,
                                provider = "mock"
                            )
                            // Post results back to UI thread
                            (androidx.compose.ui.platform.LocalContext.current as? android.app.Activity)?.runOnUiThread {
                                suggestions = result.map { it.text }
                            }
                        }.start()
                    }) {
                        Text("Generate suggestions")
                    }
                    Button(onClick = {
                        val intent = Intent(context, SettingsActivity::class.java)
                        context.startActivity(intent)
                    }) {
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
