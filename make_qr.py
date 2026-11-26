# 公開URLのQRコード（qr.png）を作るスクリプト
# 使い方: pip install qrcode pillow && python3 make_qr.py [URL]
import sys, qrcode
url = sys.argv[1] if len(sys.argv) > 1 else "https://ooooo623.github.io/1126/"
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=16, border=4)
qr.add_data(url); qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save("qr.png")
print("qr.png を作成しました:", url)
