package com.replyaisuggester

import android.inputmethodservice.InputMethodService
import android.view.View
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputConnection
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

class KeyboardStubService : InputMethodService() {
    private var currentInputConnection: InputConnection? = null
    private var currentContext = ""

    override fun onCreateInputView(): View {
        return ComposeView(this).apply {
            setContent {
                KeyboardUI()
            }
        }
    }

    override fun onStartInputView(info: EditorInfo?, restarting: Boolean) {
        super.onStartInputView(info, restarting)
        currentInputConnection = currentInputConnection
    }

    override fun onFinishInput() {
        super.onFinishInput()
        currentInputConnection = null
        currentContext = ""
    }

    private fun commitText(text: String) {
        currentInputConnection?.commitText(text, 1)
    }

    private fun getCurrentText(): String {
        return currentInputConnection?.getTextBeforeCursor(100, 0)?.toString() ?: ""
    }

    private fun appendSuggestionInline(suggestion: String, tone: String) {
        val coloredSuggestion = when (tone) {
            "casual" -> "\u001B[34m$suggestion\u001B[0m" // Blue
            "formal" -> "\u001B[32m$suggestion\u001B[0m" // Green
            "witty" -> "\u001B[33m$suggestion\u001B[0m" // Yellow
            else -> suggestion
        }
        currentInputConnection?.commitText(coloredSuggestion, 1)
    }

    @Composable
    fun InlineSuggestionUI(
        userInput: String,
        suggestion: String,
        tone: String,
        onSuggestionAccepted: () -> Unit
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = userInput,
                modifier = Modifier.weight(1f),
                fontSize = 16.sp
            )
            Text(
                text = suggestion,
                color = when (tone) {
                    "casual" -> Color.Blue
                    "formal" -> Color.Green
                    "witty" -> Color.Yellow
                    else -> Color.Gray
                },
                fontSize = 16.sp,
                modifier = Modifier.clickable(onClick = onSuggestionAccepted)
            )
        }
    }

    @Composable
    fun KeyboardUI() {
        val coroutineScope = rememberCoroutineScope()
        var suggestions by remember { mutableStateOf(listOf<Suggestion>()) }
        var isLoading by remember { mutableStateOf(false) }

        MaterialTheme {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFFEEEEEE))
            ) {
                // Suggestion strip
                if (suggestions.isNotEmpty() || isLoading) {
                    SuggestionStrip(
                        suggestions = suggestions,
                        isLoading = isLoading,
                        onSuggestionSelected = { suggestion ->
                            commitText(suggestion.text)
                        }
                    )
                }

                // Main keyboard area
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(8.dp)
                ) {
                    QuickActionButtons(
                        coroutineScope = coroutineScope,
                        isLoading = isLoading,
                        suggestions = suggestions,
                        onLoadingChange = { isLoading = it },
                        onSuggestionsChange = { suggestions = it }
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    KeyboardLayout()
                }
            }
        }
    }

    @Composable
    fun QuickActionButtons(
        coroutineScope: CoroutineScope,
        isLoading: Boolean,
        suggestions: List<Suggestion>,
        onLoadingChange: (Boolean) -> Unit,
        onSuggestionsChange: (List<Suggestion>) -> Unit
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = {
                    coroutineScope.launch {
                        onLoadingChange(true)
                        try {
                            currentContext = getCurrentText()
                            val result = NetworkClient.postSuggest(
                                userId = "dev_user",
                                context = currentContext,
                                modes = listOf("casual", "formal", "witty"),
                                intensity = 6,
                                provider = "mock"
                            )
                            onSuggestionsChange(result.take(3)) // Show top 3 suggestions
                        } catch (e: Exception) {
                            onSuggestionsChange(listOf("Error: ${e.message}"))
                        } finally {
                            onLoadingChange(false)
                        }
                    }
                },
                enabled = !isLoading,
                modifier = Modifier.weight(1f)
            ) {
                Text(if (isLoading) "..." else "Suggest", fontSize = 12.sp)
            }

            Button(
                onClick = { commitText(" ") },
                modifier = Modifier.weight(1f)
            ) {
                Text("Space", fontSize = 12.sp)
            }

            Button(
                onClick = {
                    suggestions.firstOrNull()?.let { suggestion ->
                        appendSuggestionInline(suggestion.text, suggestion.tone)
                    }
                },
                enabled = suggestions.isNotEmpty(),
                modifier = Modifier.weight(1f)
            ) {
                Text("Inline", fontSize = 12.sp)
            }
        }
    }

    @Composable
    fun KeyboardLayout() {
        // Basic keyboard rows
        KeyboardRow(keys = listOf("q", "w", "e", "r", "t", "y", "u", "i", "o", "p"))
        KeyboardRow(keys = listOf("a", "s", "d", "f", "g", "h", "j", "k", "l"))
        KeyboardRow(keys = listOf("z", "x", "c", "v", "b", "n", "m"))

        Spacer(modifier = Modifier.height(8.dp))

        // Bottom row with enter
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Button(
                onClick = { commitText("\n") },
                modifier = Modifier.weight(1f)
            ) {
                Text("Enter", fontSize = 12.sp)
            }
        }
    }

    @Composable
    fun SuggestionStrip(
        suggestions: List<Suggestion>,
        isLoading: Boolean,
        onSuggestionSelected: (Suggestion) -> Unit
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(4.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            if (isLoading) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(modifier = Modifier.size(24.dp))
                }
            } else {
                LazyRow(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = PaddingValues(horizontal = 8.dp)
                ) {
                    items(suggestions) { suggestion ->
                        SuggestionChip(
                            text = suggestion.text.take(30) + if (suggestion.text.length > 30) "..." else "",
                            onClick = { onSuggestionSelected(suggestion) }
                        )
                    }
                }
            }
        }
    }

    @Composable
    fun SuggestionChip(text: String, onClick: () -> Unit) {
        Card(
            modifier = Modifier
                .clickable(onClick = onClick)
                .padding(vertical = 4.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Text(
                text = text,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                fontSize = 14.sp,
                textAlign = TextAlign.Center
            )
        }
    }

    @Composable
    fun KeyboardRow(keys: List<String>) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            keys.forEach { key ->
                KeyboardKey(
                    key = key,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }

    @Composable
    fun KeyboardKey(key: String, modifier: Modifier = Modifier) {
        Button(
            onClick = { commitText(key) },
            modifier = modifier
                .height(48.dp)
                .padding(vertical = 2.dp),
            contentPadding = PaddingValues(4.dp)
        ) {
            Text(
                text = key.uppercase(),
                fontSize = 16.sp,
                textAlign = TextAlign.Center
            )
        }
    }
}
