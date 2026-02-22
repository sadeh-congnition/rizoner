---
trigger: always_on
---

The rizui CLI app should never use the database directly. It should also never invoke LLMs directly.
All interactions should be via the backend HTTP API.
The rizui CLI app should only be a view.
All business logic should be extracted into function which can be used without the CLI app. The CLI app then uses such functions. These functions will be always invoking the backend HTTP API to create, modify, or fetch data.