"""
郵件發送模組 - 移除綠色標題、響應式全寬度與放大字體版本
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSender:
    """使用 Gmail SMTP 發送郵件"""
    
    def __init__(self, sender_email, sender_password):
        """初始化郵件發送器"""
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
    
    def create_html_content(self, articles):
        """創建無頂部方框、響應式寬度、放大字體的 HTML 郵件內容"""
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.8;
                        color: #333;
                        background-color: #f9f9f9;
                        padding: 10px;
                        margin: 0;
                    }}
                    .container {{
                        width: 100%;
                        max-width: 1000px;
                        margin: 0 auto;
                        background: #ffffff;
                        padding: 30px 40px;
                        box-sizing: border-box;
                        border-radius: 8px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    }}
                    .content {{
                        padding: 10px 0;
                    }}
                    .article {{
                        margin-bottom: 35px;
                        padding-bottom: 25px;
                    }}
                    .article-title {{
                        font-size: 26px;
                        color: #2c3e50;
                        margin-bottom: 20px;
                        line-height: 1.4;
                        font-weight: bold;
                    }}
                    .article-body {{
                        font-size: 18px;
                        color: #333;
                        white-space: pre-line;
                        margin-bottom: 20px;
                        text-align: justify;
                    }}
                    .article-link {{
                        display: inline-block;
                        background: #64b5f6;
                        color: white;
                        text-decoration: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        font-size: 15px;
                    }}
                    .footer {{
                        text-align: center;
                        color: #888;
                        font-size: 14px;
                        margin-top: 40px;
                        border-top: 1px solid #eaeaea;
                        padding-top: 20px;
                    }}
                    
                    /* 針對行動裝置與不同螢幕大小的響應式設定 */
                    @media screen and (max-width: 768px) {{
                        .container {{
                            padding: 15px;
                        }}
                        .article-title {{
                            font-size: 22px;
                        }}
                        .article-body {{
                            font-size: 16px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="content">
        """
        
        # 添加完整文章內容
        for article in articles:
            full_content = article.get('full_content', article['summary'])
            html += f"""
                        <div class="article">
                            <h1 class="article-title">{article['title']}</h1>
                            <div class="article-body">{full_content}</div>
                            <a href="{article['link']}" class="article-link" target="_blank">至原網站閱讀更多 →</a>
                        </div>
            """
        
        html += f"""
                    </div>
                    <div class="footer">
                        <p>西班牙語新聞每日精選 - {current_date} | 祝你學習西班牙語愉快！</p>
                    </div>
                </div>
            </body>
        </html>
        """
        return html
    
    def send_email(self, recipient_email, articles):
        """發送郵件主邏輯"""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = f"📰 西班牙語新聞每日精選 - {datetime.now().strftime('%Y年%m月%d日')}"
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            html_content = self.create_html_content(articles)
            message.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            logger.info("Connecting to Gmail SMTP server...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                logger.info(f"Email sent successfully to {recipient_email}")
                return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise e
