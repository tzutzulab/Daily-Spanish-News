"""
郵件發送模組
使用 Gmail SMTP 發送西班牙語新聞郵件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import os

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
    
    def get_importance_stars(self, importance=5):
        """生成重要程度星星"""
        stars = '⭐' * min(importance, 5)
        return stars if stars else '⭐⭐⭐'
    
    def create_html_content(self, articles, vocabulary_list=None):
        """創建寬版、完整內文、10個單字、淺色系的 HTML 郵件內容"""
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.7;
                        color: #333;
                        background-color: #f9f9f9;
                        padding: 20px;
                        margin: 0;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background: #ffffff;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    }}
                    .header {{
                        background: #81c784;
                        color: white;
                        padding: 25px;
                        text-align: center;
                        border-radius: 6px 6px 0 0;
                    }}
                    .content {{
                        padding: 20px 10px;
                    }}
                    .vocabulary-section {{
                        background: #f1f8e9;
                        border-left: 4px solid #aed581;
                        padding: 20px;
                        margin-bottom: 30px;
                        border-radius: 4px;
                    }}
                    .vocabulary-grid {{
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 12px;
                        margin-top: 10px;
                    }}
                    .vocabulary-item {{
                        font-size: 14px;
                        margin-bottom: 8px;
                    }}
                    .article {{
                        margin-bottom: 35px;
                        padding-bottom: 25px;
                        border-bottom: 1px solid #eaeaea;
                    }}
                    .article-title {{
                        font-size: 22px;
                        color: #2c3e50;
                        margin-bottom: 15px;
                    }}
                    .article-body {{
                        font-size: 15px;
                        color: #444;
                        white-space: pre-line;
                        margin-bottom: 15px;
                        text-align: justify;
                    }}
                    .article-link {{
                        display: inline-block;
                        background: #64b5f6;
                        color: white;
                        text-decoration: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-size: 13px;
                    }}
                    .footer {{
                        text-align: center;
                        color: #888;
                        font-size: 12px;
                        margin-top: 30px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>📰 西班牙語新聞每日精選</h2>
                        <p>{current_date}</p>
                    </div>
                    <div class="content">
        """
        
        # 添加 10 個詞彙預習
        if vocabulary_list and len(vocabulary_list) > 0:
            html += """
                        <div class="vocabulary-section">
                            <h3>📚 今日單字預習 (共 10 個)</h3>
                            <div style="margin-top: 10px;">
            """
            for word, translation, example in vocabulary_list[:10]:
                html += f"""
                            <p style="margin-bottom: 10px;"><b>{word}</b>：{translation}<br><i style="color: #666; font-size: 13px;">💬 例句：{example}</i></p>
                """
            html += """
                            </div>
                        </div>
            """
        
        # 添加完整文章內容
        for article in articles:
            full_content = article.get('full_content', article['summary'])
            html += f"""
                        <div class="article">
                            <h3 class="article-title">{article['title']}</h3>
                            <div class="article-body">{full_content}</div>
                            <a href="{article['link']}" class="article-link">至原網站閱讀更多 →</a>
                        </div>
            """
        
        html += """
                    </div>
                    <div class="footer">
                        <p>祝你學習西班牙語愉快！</p>
                    </div>
                </div>
            </body>
        </html>
        """
        return html
    
    def send_email(self, recipient_email, articles, vocabulary_list=None):
        """發送郵件主邏輯"""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = f"📰 西班牙語新聞每日精選 - {datetime.now().strftime('%Y年%m月%d日')}"
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            html_content = self.create_html_content(articles, vocabulary_list)
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
