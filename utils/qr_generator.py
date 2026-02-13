import qrcode
import os
from config import Config

def generate_qr_code(username):
    """Generate QR code for user profile URL"""
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Profile URL
    url = f"https://pehchaan-h9ub.onrender.com/{username}"
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file
    filename = f"{username}.png"
    filepath = os.path.join(Config.QR_CODE_FOLDER, filename)
    img.save(filepath)
    
    return filename
