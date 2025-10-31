Privacy & Consent Notes

This project will handle sensitive user text data. Before collecting or uploading any messages:

- Present a clear consent screen that explains what is collected, why, how it's stored, and how to delete it.
- Default to local-only processing unless the user explicitly opts in to cloud personalization or fine-tuning.
- Provide easy export and deletion tools in settings.
- Use strong local encryption for any stored personalization blobs.
- Log minimal telemetry; avoid storing message contents in telemetry.

Recommended default architecture for MVP

- Use InputMethodService (custom keyboard) to obtain typed text with clear consent. This avoids asking for Accessibility permissions and reduces Play Store review risk.
- If importing older messages for personalization, require explicit one-time consent and show a clear preview of what will be uploaded.
- For any cloud operations, anonymize or pseudonymize data and show exact data retention rules.

Play Store considerations

- Apps that access SMS, call logs, or use Accessibility services may be subject to additional restrictions.
- Prefer IME approach to minimize elevated permission needs.
- Provide a privacy policy URL in the Play Store listing and in-app.
