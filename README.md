# Whodis

Entity Resolution API (S3 Backend)

## Overview

Whodis provides an interface into an entity resolution system backed by AWS S3. It allows users to query and identify entities based on provided information.

## Setup

1. **Credentials**: You must set your AWS credentials as environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   ```
   Ensure these credentials have read/write access to the `mithrilmedia` S3 bucket.

2. **Run Server**:
   ```bash
   python3 api_server.py
   ```

## API

### Inject Entity
`POST /inject`
```json
{
  "body": {
    "name": "John Doe",
    "email": "johndoe@example.com"
  }
}
```

### Resolve Entity
`POST /resolve`
```json
{
  "body": {
    "name": "John Doe",
    "email": "johndoe@example.com"
  }
}
```

## Architecture

- **api_server.py**: Flask application handling API requests.
- **database.py**: Core logic and S3 interaction. Implements the recursive descent entity resolution algorithm.
- **config.py**: Configuration settings.

## Demo

Run `python3 demo.py` to verify functionality (requires running server).
