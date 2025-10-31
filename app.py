import streamlit as st
from PIL import Image, ImageOps
import io, zipfile

st.set_page_config(page_title="Instagram用 画像分割ツール", page_icon="🖼️", layout="wide")
st.title("Instagram用 画像分割ツール")
st.caption("3分割・6分割・9分割を選び、ZIPで一括ダウンロードできます。")

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

    elif mode == "3x3":  # 縦3×横3（9分割）
        seg_w = w // 3
        seg_h = h // 3
        for r in range(3):
            for c in range(3):
                left = c * seg_w
                right = (c + 1) * seg_w if c < 2 else w
                top = r * seg_h
                bottom = (r + 1) * seg_h if r < 2 else h
                crop = img.crop((left, top, right, bottom))
                # 横方向だけ余白を入れてグリッド連結感をキープ（既存仕様に合わせる）
                bordered = ImageOps.expand(crop, border=(margin, 0, margin, 0), fill=bg)
                outs.append(bordered)

    return outs

# 画像をJPEGバイト列へ変換
def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

# アップロードUI
uploaded_files = st.file_uploader(
    "📷 画像をアップロード（複数可：JPG/PNG/WebP）",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

split_mode = st.radio(
    "分割方法を選択",
    ["横3分割（3x1）", "縦2×横3分割（3x2）", "縦3×横3分割（3x3）"]
)
series_start = st.number_input("開始する共通の数字（かっこ内）", min_value=1, value=1)

# 分割パターンに応じた入力欄
if "3x2" in split_mode:
    cols = st.columns(3)
    with cols[0]:
        base1 = st.text_input("左上", value="1")
        base4 = st.text_input("左下", value="4")
    with cols[1]:
        base2 = st.text_input("中央上", value="2")
        base5 = st.text_input("中央下", value="5")
    with cols[2]:
        base3 = st.text_input("右上", value="3")
        base6 = st.text_input("右下", value="6")
    bases = [base1, base2, base3, base4, base5, base6]

elif "3x3" in split_mode:
    # 3行×3列の番号入力
    row1 = st.columns(3)
    with row1[0]:
        b1 = st.text_input("左上", value="1")
    with row1[1]:
        b2 = st.text_input("中央上", value="2")
    with row1[2]:
        b3 = st.text_input("右上", value="3")

    row2 = st.columns(3)
    with row2[0]:
        b4 = st.text_input("左中", value="4")
    with row2[1]:
        b5 = st.text_input("中央", value="5")
    with row2[2]:
        b6 = st.text_input("右中", value="6")

    row3 = st.columns(3)
    with row3[0]:
        b7 = st.text_input("左下", value="7")
    with row3[1]:
        b8 = st.text_input("中央下", value="8")
    with row3[2]:
        b9 = st.text_input("右下", value="9")

    bases = [b1, b2, b3, b4, b5, b6, b7, b8, b9]

else:
    base1 = st.text_input("左列の数字（半角）", value="1")
    base2 = st.text_input("中列の数字（半角）", value="2")
    base3 = st.text_input("右列の数字（半角）", value="3")
    bases = [base1, base2, base3]

# 処理とZIP作成
if uploaded_files:
    # 数字を含むファイル名で昇順ソート（数字が無い場合は0扱い）
    uploaded_files = sorted(uploaded_files, key=lambda x: int(''.join(filter(str.isdigit, x.name)) or 0))

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as zipf:
        for i, up in enumerate(uploaded_files):
            img = Image.open(up).convert("RGB")
            if "3x2" in split_mode:
                mode = "3x2"
            elif "3x3" in split_mode:
                mode = "3x3"
            else:
                mode = "3x1"

            parts = split_image(img, mode=mode)
            current_series = series_start + i

            for im, b in zip(parts, bases):
                filename = f"taishi_{b}({current_series}).jpg"
                zipf.writestr(filename, image_to_bytes(im))

    st.download_button(
        label="⬇️ 一括ダウンロード（ZIP）",
        data=zip_buffer.getvalue(),
        file_name="taishi_images.zip",
        mime="application/zip"
    )

    st.success("✅ ZIP作成完了！クリックで一括ダウンロードできます。")
