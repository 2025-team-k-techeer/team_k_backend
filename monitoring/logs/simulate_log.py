import time
import random

log_entries = [
    {
        "timestamp": "2025-07-17T10:12:34.123Z",
        "level": "INFO",
        "service": "user-service",
        "message": "User login successful",
        "user_id": "abc123",
        "ip": "192.168.0.5",
    },
    {
        "timestamp": "2025-07-17T10:13:01.457Z",
        "level": "WARN",
        "service": "auth-service",
        "message": "JWT token about to expire",
        "user_id": "abc123",
    },
    {
        "timestamp": "2025-07-17T10:14:22.001Z",
        "level": "ERROR",
        "service": "payment-service",
        "message": "Payment processing failed",
        "user_id": "xyz789",
        "error": "Insufficient funds",
    },
    {
        "timestamp": "2025-07-17T10:15:05.333Z",
        "level": "DEBUG",
        "service": "product-service",
        "message": "Fetched product list",
        "items": 12,
        "user_id": "def456",
    },
    {
        "timestamp": "2025-07-17T10:16:45.678Z",
        "level": "INFO",
        "service": "order-service",
        "message": "Order placed successfully",
        "order_id": "ORD1009",
        "user_id": "abc123",
    },
    {
        "timestamp": "2025-07-17T10:17:29.200Z",
        "level": "ERROR",
        "service": "user-service",
        "message": "Profile update failed",
        "user_id": "def456",
        "error": "ValidationError: Email format invalid",
    },
    {
        "timestamp": "2025-07-17T10:18:10.911Z",
        "level": "INFO",
        "service": "notification-service",
        "message": "Email sent to user",
        "user_id": "xyz789",
        "email_type": "order_confirmation",
    },
    {
        "timestamp": "2025-07-17T10:19:33.999Z",
        "level": "DEBUG",
        "service": "analytics-service",
        "message": "Page view recorded",
        "user_id": "abc123",
        "page": "/dashboard",
    },
    {
        "timestamp": "2025-07-17T10:20:15.444Z",
        "level": "WARN",
        "service": "auth-service",
        "message": "Multiple failed login attempts detected",
        "user_id": "def456",
    },
    {
        "timestamp": "2025-07-17T10:21:00.123Z",
        "level": "INFO",
        "service": "inventory-service",
        "message": "Stock updated for product",
        "product_id": "PROD5678",
        "new_stock": 50,
    },
    {
        "timestamp": "2025-07-17T10:22:30.789Z",
        "level": "ERROR",
        "service": "payment-service",
        "message": "Payment gateway timeout",
        "user_id": "xyz789",
        "error_code": 504,
    },
    {
        "timestamp": "2025-07-17T10:23:45.678Z",
        "level": "DEBUG",
        "service": "user-service",
        "message": "User profile fetched successfully",
        "user_id": "abc123",
    },
    {
        "timestamp": "2025-07-17T10:24:12.345Z",
        "level": "INFO",
        "service": "order-service",
        "message": "Order shipped",
        "order_id": "ORD1010",
        "tracking_number": "TRACK123456",
    },
    {
        "timestamp": "2025-07-17T10:25:01.234Z",
        "level": "WARN",
        "service": "notification-service",
        "message": "SMS delivery failed for user",
        "user_id": "def456",
        "error_code": 400,
    },
    {
        "timestamp": "2025-07-17T10:26:20.567Z",
        "level": "INFO",
        "service": "analytics-service",
        "message": "User session ended",
        "user_id": "abc123",
    },
    {
        "timestamp": "2025-07-17T10:27:15.678Z",
        "level": "ERROR",
        "service": "product-service",
        "message": "Product not found in database",
        "product_id": "PROD9999",
    },
    {
        "timestamp": "2025-07-17T10:28:45.123Z",
        "level": "DEBUG",
        "service": "auth-service",
        "message": "User authentication successful",
        "user_id": "xyz789",
        "session_id": "sess123456",
    },
    {
        "timestamp": "2025-07-17T10:29:30.456Z",
        "level": "INFO",
        "service": "inventory-service",
        "message": "New product added to inventory",
        "product_id": "PROD1234",
        "product_name": "Sample Product",
    },
]

log_file_path = "app.log"  # this path must match what Filebeat watches

while True:
    entry = random.choice(log_entries)
    with open(log_file_path, "a") as f:
        f.write(f"{entry}\n")
    time.sleep(1.5)  # change to 0.5 or 3 for faster/slower simulation
