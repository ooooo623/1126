"""問題データを暗号化して index.html に埋め込み、合言葉入りのQRコードを作る。

使い方:
    pip install cryptography qrcode pillow
    python3 build.py              # private/key.txt の合言葉を使う（なければ新しく作る）
    python3 build.py --new-key    # 合言葉を作り直す（古いQRコードは使えなくなる）

private/ フォルダ（問題の元データ・合言葉・QRコード）は公開しないこと。
"""
import base64, json, os, re, secrets, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import qrcode

URL = "https://ooooo623.github.io/1126/"
ITER = 200_000
here = os.path.dirname(os.path.abspath(__file__))
priv = os.path.join(here, "private")
key_path = os.path.join(priv, "key.txt")

if "--new-key" in sys.argv or not os.path.exists(key_path):
    with open(key_path, "w") as f:
        f.write(secrets.token_urlsafe(18))
key = open(key_path).read().strip()

data = json.load(open(os.path.join(priv, "problems.json"), encoding="utf-8"))
plain = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
salt, iv = os.urandom(16), os.urandom(12)
k = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(key.encode())
ct = AESGCM(k).encrypt(iv, plain, None)
b64 = lambda b: base64.b64encode(b).decode()
enc = json.dumps({"it": ITER, "salt": b64(salt), "iv": b64(iv), "ct": b64(ct)})

page = os.path.join(here, "index.html")
html = open(page, encoding="utf-8").read()
html, n = re.subn(r"/\*ENC\*/.*?/\*/ENC\*/", lambda m: "/*ENC*/" + enc + "/*/ENC*/", html, flags=re.S)
assert n == 1, "index.html に /*ENC*/ の目印が見つかりません"
open(page, "w", encoding="utf-8").write(html)

full = f"{URL}#k={key}"
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=16, border=4)
qr.add_data(full); qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save(os.path.join(priv, "qr.png"))
with open(os.path.join(priv, "QRのURL.txt"), "w", encoding="utf-8") as f:
    f.write(full + "\n")
print("暗号化しました:", sum(len(s["cards"]) for s in data["sets"]), "問")
print("QRコード: private/qr.png")
print("QRのURL :", full)
