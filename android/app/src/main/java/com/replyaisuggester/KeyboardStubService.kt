package com.replyaisuggester

import android.inputmethodservice.InputMethodService
import android.view.View

// Minimal stub for InputMethodService (custom keyboard). Implement properly in the app.
class KeyboardStubService : InputMethodService() {
    override fun onCreateInputView(): View? {
        // Return a simple view or inflate a ComposeView for a custom keyboard UI.
        return super.onCreateInputView()
    }
}
