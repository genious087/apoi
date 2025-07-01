import os
import smtplib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

app = FastAPI(title="Stelle Email Service", description="Sends emails with inline images.", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class EmailRequest(BaseModel):
    email: EmailStr

SMTP_SERVER = "smtpout.secureserver.net"
SMTP_PORT = "465"
SMTP_USERNAME = "info@stelle.world"
SMTP_PASSWORD = "zyngate123"
FROM_EMAIL = "info@stelle.world"

if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL]):
    raise Exception("Missing one or more required SMTP configuration environment variables.")

@app.post("/send-email-with-image", summary="Send an email with an inline image", response_description="Confirmation message")
def send_email_with_image(request: EmailRequest):
    try:
        # Create a multipart/related message
        message = MIMEMultipart("related")
        message["Subject"] = "Exclusive Invite from Stelle"
        message["From"] = FROM_EMAIL
        message["To"] = request.email

        # Create a multipart/alternative for the email body
        body = MIMEMultipart("alternative")
        message.attach(body)

        # Create HTML content with a clickable inline image and a Get Started button
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; text-align: center;">
                <p>
                    <a href="https://stelle.chat" target="_blank" style="text-decoration: none;">
                        <img src="cid:image1" alt="Stelle Invite" style="max-width: 100%; height: auto;"/>
                    </a>
                </p>
                <p>
                    <a href="https://stelle.chat" target="_blank" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Get Started
                    </a>
                </p>
                <p>Please enjoy this exclusive invite from Stelle.</p>
            </body>
        </html>
        """
        html_part = MIMEText(html_content, "html")
        body.attach(html_part)

        # Read the image from a local file
        image_path = "stelle.jpg"
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file {image_path} not found")
        
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # Attach the image with a Content-ID for inline display
        image_part = MIMEImage(image_data, name="main_large.jpg")
        image_part.add_header("Content-ID", "<image1>")
        image_part.add_header("Content-Disposition", "inline")
        message.attach(image_part)

        # Send the email
        with smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, request.email, message.as_string())

        return {"message": "Email with inline image sent successfully!"}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("stellemail:app", host="0.0.0.0", port=port, reload=True)