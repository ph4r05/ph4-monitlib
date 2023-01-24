# Monitoring library

Library contains several utility classes that help with building monitoring scripts.

- *Worker*, synchronous, thread-backed worker processing tasks (lambdas) inserted to the queue
- *AsyncWorker*, asynchronous worker processing coroutines enqueued to the task queue
- *FiFoComm*, for client-server communication via named pipes (daemon vs notifier comm), use JWT protection (not included)
- *TcpComm*, for client-server communication via TCP, use JWT protection (not included)
- *NotifyEmail*, helper for sending notification emails via SMTP server (gmail tested)
- *TelegramBot*, helper for sending notifications via Telegram, receive messages, send messages