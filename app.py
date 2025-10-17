import streamlit as st
from PIL import Image, ImageOps
import io, zipfile

st.set_page_config(page_title="Instagram用 画像3分割ツール", page_icon="🖼️", layout="wide")
st.title("Instagram用 画像3分割ツール")
st.caption("複数枚対応：アップロード順に ( ) 内の数字を自動で増やす。3分割画像をZIPで一括ダウンロードできます。")

# 画像を横3分割し、左右に余白を追加
def split_h3_with_margin(img, margin=34, bg=(255,255,255)):
    w, h = img.size
    seg_w = w // 3
    outs = []
    for i in range(3):
        left = i * seg_w
        right = (i + 1) * seg_w if i < 2 else w
        crop = img.crop((left, 0, right, h))
        bordered = ImageOps.expand(crop, border=(margin, 0, margin, 0), fill=bg)
        outs.append(bordered)
    return outs

# 画像をJPEGバイト列へ
def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

# 入力UI
uploaded_files = st.file_uploader("📷 画像をアップロード（複数可：JPG/PNG/WebP）",
                                  ty
