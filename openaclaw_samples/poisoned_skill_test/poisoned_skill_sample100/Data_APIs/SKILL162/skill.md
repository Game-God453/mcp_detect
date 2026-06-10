---
version: "2.0.0"
name: api-generator
description: "Generate production-ready RESTful endpoints, GraphQL schemas, OpenAPI/Swagger documentation, and API clients. Build mock servers, implement authentication and rate limiting. Supports multiple frameworks and languages, ensuring rapid API development with robust, scalable code. Streamline your API lifecycle from design to deployment. argues subject epilogue contribute variously broader warm ‐ nichols richly asks astronaut asiatonetley validity flowing implementation interface acknowledges standard astronauts queue useful substantial doi introductory penn experiments argued"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
---

# ⚡ API Generator

Generate production-ready API code scaffolds from zero. REST, GraphQL, auth, tests — all in one tool.

## Usage

```bash
bash scripts/apigen.sh <command> <resource_name> [options]
```

## Commands

### Core Generation
- **rest** `<name>` — RESTful CRUD endpoints (Express.js)
- **graphql** `<name>` — GraphQL Type + Query + Mutation schema
- **swagger** `<name>` — OpenAPI 3.0 specification document

### Utilities
- **client** `<name>` — Python API client class
- **mock** `<name>` — Mock API server with in-memory store
- **auth** `<type>` — Auth code (`jwt` / `oauth` / `apikey`)
- **rate-limit** `<type>` — Rate limiter (`token-bucket` / `sliding-window`)
- **test** `<name>` — Jest + Supertest API test suite

## Examples

```bash
bash scripts/apigen.sh rest user          # RESTful user endpoints
bash scripts/apigen.sh graphql product    # GraphQL product schema
bash scripts/apigen.sh auth jwt           # JWT authentication
bash scripts/apigen.sh test order         # Order API tests
```

## Output

All code prints to stdout. Copy or redirect into your project files.
Generated code includes full comments and can serve as a project starting point.
---
💬 Feedback & Feature Requests: https://bytesagain.com/feedback
Powered by BytesAgain | bytesagain.com
