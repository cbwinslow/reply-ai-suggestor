# Privacy Policy for Reply AI Suggester

**Effective Date:** October 31, 2025

## Introduction

Reply AI Suggester ("we," "us," or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our mobile application ("App"). By using the App, you agree to the collection and use of information in accordance with this policy.

## Information We Collect

### Information You Provide
- **User Input:** Text you type in messaging apps while using our keyboard service. This is used solely to generate reply suggestions.
- **Personalization Data:** With your explicit consent, anonymized examples of your typing patterns and accepted suggestions for improving future suggestions.

### Information Collected Automatically
- **Device Information:** Basic device identifiers, app usage statistics, and error logs (without message contents).
- **Usage Data:** How you interact with suggestions (e.g., acceptance rates), but not the content of messages.

## How We Use Your Information

- **To Provide Services:** Generate and display reply suggestions based on your current typing context.
- **To Improve the App:** With your consent, use anonymized data to enhance suggestion quality.
- **To Ensure Security:** Monitor for abuse and maintain app stability.

## Data Sharing and Disclosure

We do not sell, trade, or otherwise transfer your personal information to third parties, except as described below:

- **Service Providers:** We may use third-party AI providers (e.g., Google Gemini, OpenAI) to generate suggestions. Data sent to these providers is anonymized and not stored by them.
- **Legal Requirements:** We may disclose information if required by law or to protect our rights.

## Data Storage and Security

- **Local Storage:** All data is stored locally on your device with encryption.
- **Cloud Storage:** Only with explicit opt-in; data is encrypted in transit and at rest.
- **Retention:** Personalization data is retained only as long as you use the app and can be deleted at any time.

## Your Choices and Rights

- **Consent:** You can opt-in or opt-out of personalization features at any time.
- **Data Deletion:** Use the in-app settings to delete all stored data.
- **Data Export:** Request a copy of your data via the app settings.
- **Disable Features:** Turn off the keyboard service or uninstall the app.

## Children's Privacy

The App is not intended for children under 13. We do not knowingly collect personal information from children under 13.

## Changes to This Privacy Policy

We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.

## Contact Us

If you have any questions about this Privacy Policy, please contact us at [contact email].

---

## Implementation Notes

- **Consent Screen:** Implement a one-time consent dialog on first launch.
- **Settings Screen:** Provide toggles for personalization, data export, and deletion.
- **Encryption:** Use Android's EncryptedSharedPreferences for local storage.
- **Anonymization:** Strip personal identifiers before any cloud upload.
