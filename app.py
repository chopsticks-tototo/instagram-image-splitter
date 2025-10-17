import streamlit as st
from PIL import Image, ImageOps
import io, zipfile

st.set_page_config(page_title="Instagram用 画像分割ツール", page_icon="🖼️", layout="wide")
st.title("Instagram用 画像分割ツール")
st.caption("3分割または6分割を選んでZIPで一括ダウンロードできます。")

# 分割関数
def split_image(img, mode="3x1", margin=34, bg=(255,255,255)):
    w, h = img.size
    outs = []

    if mode == "3x1":  # 横3分割
        seg_w = w // 3
        for i in range(3):
            left = i * seg_w
            right = (i + 1) * seg_w if i < 2 else w
            crop = img.crop((left, 0, right, h))
            bordered = ImageOps.expand(crop, border=(margin, 0, margin, 0), fill=bg)
            outs.append(bordered)

    elif mode == "3x2":  # 縦2×横3（6分割）
        seg_w = w // 3
        seg_h = h // 2
        for r in range(2):
            for c in range(3):
                left = c * seg_w
                right = (c + 1) * seg_w if c < 2 else w
                top = r * seg_h
                bottom = (r + 1) * seg_h if r < 1 else h
                crop = img.crop((left, top, right, bottom))
                bordered = ImageOps.expand(crop, border=(margin, 0, margin, 0), fill=bg)
                outs.append(bordered)

    return outs

# 画像→バイト列変換
def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

# UI
uploaded_files = st.file_uploader("📷 画像をアップロード（複数可）",
                                  type=["jpg", "jpeg", "png", "webp"],
                                  accept_multiple_files=True)

split_mode = st.radio("分割方法を選択", ["横3分割（3x1）", "縦2×横3分割（3x2）"])
series_start = st.number_input("開始する共通の数字（かっこ内）", min_value=1, value=1)
base1 = st.text_input("左列の数字（半角）", value="1")
base2 = st.text_input("中列の数字（半角）", value="2")
base3 = st.text_input("右列の数字（半角）", value="3")

# 実行処理
if uploaded_files:
    # ファイル名の数字順でソート
    uploaded_files = sorted(uploaded_files, key=lambda x: int(''.join(filter(str.isdigit, x.name)) or 0))

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as zipf:
        for i, up in enumerate(uploaded_files):
            img = Image.open(up).convert("RGB")
            mode = "3x2" if "3x2" in split_mode else "3x1"
            parts = split_image(img, mode=mode)
            current_series = series_start + i

            # ファイル名付け方を行・列で分ける
            for idx, im in enumerate(parts):
                if mode == "3x1":
                    b = [base1, base2, base3][idx]
                else:
                    # 6分割時は左上→右下で通し番号
                    b = f"{(idx+1)}"
                filename = f"taishi_{b}({current_series}).jpg"
                zipf.writestr(filename, image_to_bytes(im))

    # DLボタン
    st.download_button(
        label="⬇️ 一括ダウンロード（ZIP）",
        data=zip_buffer.getvalue(),
        file_name="taishi_images.zip",
        mime="application/zip"
    )

    st.success("✅ ZIP作成完了！クリックで一括ダウンロードできます。")
