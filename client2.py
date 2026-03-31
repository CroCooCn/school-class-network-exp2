from base64 import b64encode
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket


mailserver = "localhost"
mailport = 1025

helo_name = "Alice"
sender = "liyujie@xxx.com"
recipient = "teacher@xxx.com"
subject = "带附件的邮件"
body_lines = [
    "第二次见面",
    "",
    "这份邮件用原始的SMTP协议约定实现发送。",
    "",
    "请查看附件。",
    "",
    "Best regards,",
    "Student Li",
]
attachment_path = "pikachu.jpg"

boundary = "BOUNDARY_123456789"
endmsg = "\r\n.\r\n"


def recv_expect(sock, code):
    reply = sock.recv(1024).decode()
    print(reply)
    if not reply.startswith(code):
        print(f"{code} reply not received from server.")


def build_mail_data(file_path):
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Attachment not found: {path}")

    file_bytes = path.read_bytes()
    encoded_file = b64encode(file_bytes).decode("ascii")

    # SMTP line length is limited, so wrap base64 content at 76 chars.
    wrapped_file = "\r\n".join(
        encoded_file[i:i + 76] for i in range(0, len(encoded_file), 76)
    )

    filename = path.name
    ext = path.suffix.lower()
    content_type = "application/octet-stream"
    if ext == ".jpg" or ext == ".jpeg":
        content_type = "image/jpeg"
    elif ext == ".png":
        content_type = "image/png"
    elif ext == ".gif":
        content_type = "image/gif"
    elif ext == ".pdf":
        content_type = "application/pdf"
    elif ext == ".txt":
        content_type = "text/plain"
    elif ext == ".docx":
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    headers = [
        f"From: {sender}",
        f"To: {recipient}",
        f"Subject: {subject}",
        "MIME-Version: 1.0",
        f'Content-Type: multipart/mixed; boundary="{boundary}"',
        "",
    ]

    body_text = "\r\n".join(body_lines)
    text_part = [
        f"--{boundary}",
        'Content-Type: text/plain; charset="utf-8"',
        "Content-Transfer-Encoding: 8bit",
        "",
        body_text,
        "",
    ]

    attachment_part = [
        f"--{boundary}",
        f'Content-Type: {content_type}; name="{filename}"',
        "Content-Transfer-Encoding: base64",
        f'Content-Disposition: attachment; filename="{filename}"',
        "",
        wrapped_file,
        "",
        f"--{boundary}--",
    ]

    mail_data = "\r\n".join(headers + text_part + attachment_part)
    return mail_data


client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((mailserver, mailport))

recv_expect(client_socket, "220")

client_socket.send(f"HELO {helo_name}\r\n".encode())
recv_expect(client_socket, "250")

client_socket.send(f"MAIL FROM:<{sender}>\r\n".encode())
recv_expect(client_socket, "250")

client_socket.send(f"RCPT TO:<{recipient}>\r\n".encode())
recv_expect(client_socket, "250")

client_socket.send(b"DATA\r\n")
recv_expect(client_socket, "354")

mail_content = build_mail_data(attachment_path)
client_socket.send(mail_content.encode("utf-8"))
client_socket.send(endmsg.encode())
recv_expect(client_socket, "250")

client_socket.send(b"QUIT\r\n")
recv_expect(client_socket, "221")

client_socket.close()
print(f"Mail sent successfully with attachment: {attachment_path}")
