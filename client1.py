from socket import AF_INET, SOCK_STREAM, socket


mailserver = "localhost"
mailport = 1025

sender = "liyujie@student.com"
recipient = "bob@teacher.com"
subject = "计网实验二-文本邮件"
body = [
    "你好,",
    "",
    "这是从我的邮件客户端发出的明文文本！",
    "",
    "20260330",
    "BJTU",
]

endmsg = "\r\n.\r\n"


def recv_expect(sock, code):
    reply = sock.recv(1024).decode()
    print(reply)
    if not reply.startswith(code):
        print(f"{code} reply not received from server.")


def build_plain_mail():
    body_text = "\r\n".join(body)
    headers = [
        f"From: {sender}",
        f"To: {recipient}",
        f"Subject: {subject}",
        'Content-Type: text/plain; charset="utf-8"',
        "Content-Transfer-Encoding: 8bit",
        "",
        body_text,
    ]
    return "\r\n".join(headers)


clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, mailport))

recv_expect(clientSocket, "220")

heloCommand = "HELO Alice\r\n"
clientSocket.send(heloCommand.encode())
recv_expect(clientSocket, "250")

mailFrom = f"MAIL FROM:<{sender}>\r\n"
clientSocket.send(mailFrom.encode())
recv_expect(clientSocket, "250")

rcptTo = f"RCPT TO:<{recipient}>\r\n"
clientSocket.send(rcptTo.encode())
recv_expect(clientSocket, "250")

dataCommand = "DATA\r\n"
clientSocket.send(dataCommand.encode())
recv_expect(clientSocket, "354")

mailContent = build_plain_mail()
clientSocket.send(mailContent.encode("utf-8"))
clientSocket.send(endmsg.encode())
recv_expect(clientSocket, "250")

quitCommand = "QUIT\r\n"
clientSocket.send(quitCommand.encode())
recv_expect(clientSocket, "221")

clientSocket.close()
