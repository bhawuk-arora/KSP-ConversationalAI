# API Documentation (REST endpoints)

This document describes the primary REST endpoints, authentication methods, payload structures, and error states for the KSP Crime Intelligence Platform.

---

## 1. Authentication & Authorization

All API endpoints (except login/auth) require a Bearer JWT token in the `Authorization` header:
`Authorization: Bearer <JWT_TOKEN>`

Roles supported in token claims:
- `Constable`
- `Investigator`
- `Analyst`
- `Supervisor`
- `Admin`

---

## 2. API Endpoints

### 2.1 Conversational AI Endpoints

#### POST `/api/v1/chat/message`
Sends a user message to the conversational engine and returns a streamed response.

- **Request Payload**:
  ```json
  {
    "message": "Find all cases registered under Section 302 in Mysuru district during 2025.",
    "session_id": "8fa3c2d4-1a9e-4c8d-b0a3-d02f3a8b27c3",
    "voice_input": false,
    "demo_mode": true
  }
  ```
- **Response Format (Server-Sent Events - SSE)**:
  Returns chunks of token strings, ending with a final metadata block:
  ```json
  {
    "event": "message_chunk",
    "text": "Based on case records..."
  }
  {
    "event": "metadata",
    "sql_executed": "SELECT * FROM CaseMaster WHERE DistrictID = 5...",
    "cypher_executed": null,
    "citations": [
      { "id": 10243, "crime_no": "FIR:104430006202500002" }
    ],
    "confidence_score": 0.94
  }
  ```

#### GET `/api/v1/chat/sessions`
Retrieves chat sessions for the logged-in officer.
- **Response**: List of session IDs, timestamps, and titles.

#### GET `/api/v1/chat/sessions/{session_id}/export`
Generates a PDF format export of the complete conversation history.
- **Response**: Binary stream of `application/pdf`.

---

### 2.2 Criminal Network Endpoints

#### GET `/api/v1/network/suspect/{accused_id}/associations`
Fetches relational graph data from Neo4j centered around a specific accused.

- **Query Parameters**:
  - `depth` (integer, default: 2): Max hops to traverse.
  - `include_financial` (boolean, default: false).
- **Response**:
  ```json
  {
    "nodes": [
      { "id": "A_901", "type": "Accused", "label": "Ramesh Kumar", "risk_score": 78 },
      { "id": "C_102", "type": "CaseMaster", "label": "FIR:104430006202600001", "status": "Under Investigation" }
    ],
    "edges": [
      { "source": "A_901", "target": "C_102", "relationship": "ACCUSED_IN" }
    ]
  }
  ```

---

### 2.3 Crime Analytics & GIS Endpoints

#### GET `/api/v1/analytics/hotspots`
Retrieves aggregated coordinate points and geofenced clusters for mapping.

- **Query Parameters**:
  - `district_id` (integer, optional)
  - `crime_major_head_id` (integer, optional)
  - `start_date` (date)
  - `end_date` (date)
- **Response**:
  ```json
  {
    "points": [
      { "latitude": 12.9716, "longitude": 77.5946, "weight": 4.5, "crime_category": "Theft" }
    ],
    "clusters": [
      {
        "polygon": [[12.97, 77.59], [12.98, 77.59], [12.98, 77.60], [12.97, 77.60]],
        "risk_level": "High"
      }
    ]
  }
  ```

#### GET `/api/v1/analytics/trends`
Provides time-series statistics for crime categories.
- **Response**: Monthly aggregate counts of cases categorized by major head over a selected range.

---

### 2.4 Case Management & Decision Support

#### GET `/api/v1/cases/{case_id}/timeline`
Generates chronological list of events for the specified case.
- **Response**: List of events including FIR registration, arrest, chargesheet, and court updates.

---

## 3. Error Responses

Standardized responses following the RFC 7807 (Problem Details) schema:

```json
{
  "type": "/errors/insufficient-clearance",
  "title": "Access Denied",
  "status": 403,
  "detail": "Officer rank does not permit viewing victim details under case Category 4.",
  "instance": "/api/v1/cases/10042/victims"
}
```
Standard status codes:
- `400 Bad Request`: Validation failure.
- `401 Unauthorized`: Invalid or expired JWT token.
- `403 Forbidden`: Insufficient RBAC clearance.
- `404 Not Found`: Entity does not exist.
- `500 Internal Server Error`: Server errors.
