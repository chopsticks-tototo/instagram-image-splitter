import streamlit as st
from PIL import Image, ImageOps
import io, zipfile

st.set_page_config(page_title="Instagram用 画像3分割ツール", page_icon="🖼️", layout="wide")
st.title("Instagram用 画像3分割ツール")
st.caption("複数枚対応：アップロード順に ( ) 内の数字を自動で増やす。3分割画像をZIPで一括ダウンロードできます。")

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

def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

uploaded_files = st.file_uploader(
    "📷 画像をアップロード（複数可：JPG/PNG/WebP）",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)
series_start = st.number_input("開始する共通の数字（かっこ内）", min_value=1, value=1)
base1 = st.text_input("左列の数字（半角）", value="1")
base2 = st.text_input("中列の数字（半角）", value="2")
base3 = st.text_input("右列の数字（半角）", value="3")

if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: int(''.join(filter(
