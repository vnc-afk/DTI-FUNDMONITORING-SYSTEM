# Chatbot API - Example Requests & Responses

This file contains real-world examples of chatbot API usage for all supported intents.

---

## 1. Total Funds Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "What are the total available funds?"
}
```

### Response
```json
{
  "intent": "total_funds",
  "confidence": 0.95,
  "response": "As of today, your total available funds is ₱1,234,567.89. (Total Allocated: ₱2,000,000.00, Total Spent: ₱765,432.11)",
  "message_cleaned": "total available funds",
  "timestamp": "2026-05-08T14:30:00Z"
}
```

---

## 2. Fund Allocation Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Show me how the funds are allocated"
}
```

### Response
```json
{
  "intent": "fund_allocation",
  "confidence": 0.88,
  "response": "Here's the fund allocation breakdown:\n• TVET Fund: ₱1,000,000.00\n• Skills Development: ₱800,000.00\n• Equipment: ₱200,000.00\n\nTotal Allocation: ₱2,000,000.00",
  "message_cleaned": "funds allocated",
  "timestamp": "2026-05-08T14:32:15Z"
}
```

---

## 3. Today's Expenses Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "How much was spent today?"
}
```

### Response
```json
{
  "intent": "expenses_today",
  "confidence": 0.92,
  "response": "Today's expenses total ₱125,450.00 across 4 transactions.",
  "message_cleaned": "spent today",
  "timestamp": "2026-05-08T14:35:42Z"
}
```

---

## 4. Weekly Expenses Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Tell me about weekly expenses"
}
```

### Response
```json
{
  "intent": "weekly_expenses",
  "confidence": 0.90,
  "response": "This week's expenses total ₱542,100.00 across 18 transactions (from 2026-05-05 to 2026-05-08).",
  "message_cleaned": "weekly expenses",
  "timestamp": "2026-05-08T14:38:20Z"
}
```

---

## 5. Monthly Summary Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Monthly summary please"
}
```

### Response
```json
{
  "intent": "monthly_summary",
  "confidence": 0.93,
  "response": "This month's summary (May 2026):\n• Expenses: ₱1,850,000.00\n• Downloads: ₱50,000.00\n• Total Activity: ₱1,900,000.00\n• Transactions: 145",
  "message_cleaned": "monthly summary",
  "timestamp": "2026-05-08T14:40:55Z"
}
```

---

## 6. Top Expenses Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "What are the top 5 expenses?"
}
```

### Response
```json
{
  "intent": "top_expenses",
  "confidence": 0.94,
  "response": "Top 5 highest expenses:\n1. ABC Construction Corp - ₱500,000.00 (2026-05-05)\n2. XYZ Suppliers Ltd - ₱250,000.00 (2026-05-04)\n3. Tech Solutions Inc - ₱175,000.00 (2026-05-03)\n4. Global Distributors - ₱150,000.00 (2026-05-02)\n5. Local Contractors - ₱125,000.00 (2026-05-01)",
  "message_cleaned": "top 5 expenses",
  "timestamp": "2026-05-08T14:43:10Z"
}
```

---

## 7. Supplier List Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "List all suppliers"
}
```

### Response
```json
{
  "intent": "supplier_list",
  "confidence": 0.96,
  "response": "Total suppliers: 25\n\n• ABC Construction Corp (TIN: 123-456-789)\n• XYZ Suppliers Ltd (TIN: 234-567-890)\n• Tech Solutions Inc (TIN: 345-678-901)\n• Global Distributors (TIN: 456-789-012)\n• Local Contractors\n[... and 20 more suppliers]",
  "message_cleaned": "list all suppliers",
  "timestamp": "2026-05-08T14:45:30Z"
}
```

---

## 8. Supplier Transactions Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Show me transactions for ABC Construction"
}
```

### Response
```json
{
  "intent": "supplier_transactions",
  "confidence": 0.89,
  "response": "Supplier transactions for 'ABC Construction':\n• ABC Construction Corp: ₱1,500,000.00 (6 transactions)\n• XYZ Suppliers Ltd: ₱800,000.00 (4 transactions)\n• Tech Solutions Inc: ₱500,000.00 (3 transactions)\n• Global Distributors: ₱300,000.00 (2 transactions)\n• Local Contractors: ₱250,000.00 (1 transaction)",
  "message_cleaned": "transactions abc construction",
  "timestamp": "2026-05-08T14:48:15Z"
}
```

---

## 9. Top Supplier Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Who is the top supplier?"
}
```

### Response
```json
{
  "intent": "top_supplier",
  "confidence": 0.91,
  "response": "The top supplier is **ABC Construction Corp** with a total of ₱1,500,000.00 across 6 transactions.",
  "message_cleaned": "top supplier",
  "timestamp": "2026-05-08T14:50:45Z"
}
```

---

## 10. Unreconciled Transactions Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Show me unreconciled transactions"
}
```

### Response
```json
{
  "intent": "unreconciled",
  "confidence": 0.92,
  "response": "You have 12 unreconciled transactions totaling ₱450,000.00. Please review and match these transactions.",
  "message_cleaned": "unreconciled transactions",
  "timestamp": "2026-05-08T14:52:20Z"
}
```

---

## 11. Reconciliation Status Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "What's the reconciliation status?"
}
```

### Response
```json
{
  "intent": "reconciliation_status",
  "confidence": 0.93,
  "response": "Bank Reconciliation Status:\n• Total Transactions: 250\n• Cleared: 238 (95.2%)\n• Uncleared: 12\n• Total Amount: ₱5,000,000.00\n• Cleared Amount: ₱4,550,000.00",
  "message_cleaned": "reconciliation status",
  "timestamp": "2026-05-08T14:54:35Z"
}
```

---

## 12. Financial Summary Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Give me a financial summary"
}
```

### Response
```json
{
  "intent": "financial_summary",
  "confidence": 0.95,
  "response": "Financial Summary:\n• Total Funds: ₱2,000,000.00\n• Total Spent: ₱765,432.11\n• Remaining Balance: ₱1,234,567.89\n• Spending Rate: 38.3%\n• Total Transactions: 250\n• Active Suppliers: 25",
  "message_cleaned": "financial summary",
  "timestamp": "2026-05-08T14:56:50Z"
}
```

---

## 13. User Activity Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "Who are the active users?"
}
```

### Response
```json
{
  "intent": "user_activity",
  "confidence": 0.88,
  "response": "User Activity Summary:\n• Active Users (7 days): 12 / 18\n• Recent Logins:\n• John Doe - Last seen: 2026-05-08 14:20\n• Maria Santos - Last seen: 2026-05-08 13:45\n• Carlos Rivera - Last seen: 2026-05-08 11:30\n• Ana Reyes - Last seen: 2026-05-07 16:15\n• Pedro Gonzales - Last seen: 2026-05-07 09:00",
  "message_cleaned": "active users",
  "timestamp": "2026-05-08T14:58:10Z"
}
```

---

## 14. Unknown Intent Query

### Request
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "What is the weather today?"
}
```

### Response
```json
{
  "intent": "unknown",
  "confidence": 0.0,
  "response": "Sorry, I couldn't understand your request. Try asking about funds, expenses, suppliers, transactions, reconciliation, or user activity.",
  "message_cleaned": "weather today",
  "timestamp": "2026-05-08T15:00:00Z"
}
```

---

## 15. Chat History Retrieval (Authenticated)

### Request
```bash
GET /api/chatbot/history/?limit=10&offset=0
Authorization: Bearer <token>
```

### Response
```json
{
  "count": 45,
  "limit": 10,
  "offset": 0,
  "results": [
    {
      "id": 45,
      "user": 5,
      "user_display": "John Doe",
      "message": "What are the total funds?",
      "detected_intent": "total_funds",
      "confidence_score": 0.95,
      "response": "As of today, your total available funds is ₱1,234,567.89...",
      "timestamp": "2026-05-08T14:30:00Z",
      "is_resolved": true
    },
    {
      "id": 44,
      "user": 5,
      "user_display": "John Doe",
      "message": "Top expenses",
      "detected_intent": "top_expenses",
      "confidence_score": 0.92,
      "response": "Top 5 highest expenses:\n1. ABC Construction Corp - ₱500,000.00...",
      "timestamp": "2026-05-08T14:25:00Z",
      "is_resolved": true
    }
  ]
}
```

---

## 16. Intent Detection Test

### Request
```bash
POST /api/chatbot/test/intent/
Content-Type: application/json

{
  "message": "Please tell me what are the total available funds?"
}
```

### Response
```json
{
  "message": "Please tell me what are the total available funds?",
  "message_cleaned": "total available funds",
  "detected_intent": "total_funds",
  "confidence": 0.95
}
```

---

## Error Examples

### 400 - Invalid Request

**Request:**
```bash
POST /api/chatbot/
Content-Type: application/json

{}
```

**Response:**
```json
{
  "error": "Invalid message format",
  "details": {
    "message": ["This field is required."]
  }
}
```

---

### 400 - Empty Message

**Request:**
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": ""
}
```

**Response:**
```json
{
  "error": "Invalid message format",
  "details": {
    "message": ["Ensure this field has at least 1 characters."]
  }
}
```

---

### 400 - Message Too Long

**Request:**
```bash
POST /api/chatbot/
Content-Type: application/json

{
  "message": "This is a very long message that exceeds 1000 characters... [continues]"
}
```

**Response:**
```json
{
  "error": "Invalid message format",
  "details": {
    "message": ["Ensure this field has no more than 1000 characters."]
  }
}
```

---

### 500 - Database Error

**Response:**
```json
{
  "error": "Internal server error",
  "details": "Database connection failed: connection refused",
  "response": "Sorry, I encountered an error processing your request. Please try again."
}
```

---

## Alternative Request Formats

### Using cURL
```bash
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the total balance?"}'
```

### Using Python
```python
import requests

url = "http://localhost:8000/api/chatbot/"
payload = {"message": "What is the total balance?"}

response = requests.post(url, json=payload)
print(response.json())
```

### Using JavaScript/Fetch
```javascript
fetch('http://localhost:8000/api/chatbot/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'What is the total balance?' })
})
.then(res => res.json())
.then(data => console.log(data))
```

### Using JavaScript/Axios
```javascript
import axios from 'axios'

axios.post('http://localhost:8000/api/chatbot/', {
  message: 'What is the total balance?'
})
.then(res => console.log(res.data))
.catch(err => console.error(err))
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "DTI Chatbot API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Total Funds",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"message\": \"What are the total available funds?\"}"
        },
        "url": {
          "raw": "{{base_url}}/api/chatbot/",
          "host": ["{{base_url}}"],
          "path": ["api", "chatbot"]
        }
      }
    },
    {
      "name": "Top Expenses",
      "request": {
        "method": "POST",
        "body": {
          "mode": "raw",
          "raw": "{\"message\": \"Show me the top 5 expenses\"}"
        },
        "url": {
          "raw": "{{base_url}}/api/chatbot/",
          "host": ["{{base_url}}"],
          "path": ["api", "chatbot"]
        }
      }
    },
    {
      "name": "Supplier Transactions",
      "request": {
        "method": "POST",
        "body": {
          "mode": "raw",
          "raw": "{\"message\": \"Transactions for ABC Corporation\"}"
        },
        "url": {
          "raw": "{{base_url}}/api/chatbot/",
          "host": ["{{base_url}}"],
          "path": ["api", "chatbot"]
        }
      }
    },
    {
      "name": "Chat History",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/chatbot/history/?limit=10",
          "host": ["{{base_url}}"],
          "path": ["api", "chatbot", "history"],
          "query": [
            {
              "key": "limit",
              "value": "10"
            }
          ]
        }
      }
    }
  ]
}
```

---

**Last Updated**: May 8, 2026
