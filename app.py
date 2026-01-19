import streamlit as st
from PIL import Image, ImageOps
import io, zipfile

st.set_page_config(page_title="Instagram用 画像分割ツール", page_icon="🖼️", layout="wide")
st.title("Instagram用 画像分割ツール")
st.caption("3分割・6分割・9分割・12分割を選び、ZIPで一括ダウンロードできます。各ピースは縦そのまま・左右パディングで4:5に揃えます。")

# ---- 4:5比率に合わせて左右だけ余白を足す（高さは不変）----
def pad_to_ratio_4_5(img, bg=(255,255,255)):
    w, h = img.size
    target_w = int(round(h * 4 / 5))  # 横:縦 = 4:5
    if w >= target_w:
        return img
    pad_total = target_w - w
    left = pad_total // 2
    right = pad_total - left
    return ImageOps.expand(img, border=(left, 0, right, 0), fill=bg)

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
                bordered = ImageOps.expand(crop, border=(margin, 0, margin, 0), fill=bg)
                outs.append(bordered)

    elif mode == "4x3":  # ★追加：縦3×横4（12分割）
        seg_w = w // 4
        seg_h = h // 3
        for r in range(3):
            for c in range(4):
                left = c * seg_w
                right = (c + 1) * seg_w if c < 3 else w
                top = r * seg_h
                bottom = (r + 1) * seg_h if r < 2 else h
                crop = img.crop((left, top, right, bottom))
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
    ["横3分割（3x1）", "縦2×横3分割（3x2）", "縦3×横3分割（3x3）", "縦3×横4分割（4x3）"]
)

# ▼ 共通番号（かっこ内）を付けないオプション
no_series_in_parentheses = st.checkbox("共通番号（かっこ内）を付けない", value=False)
if not no_series_in_parentheses:
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

elif "4x3" in split_mode:
    # ★追加：縦3×横4（12分割）入力欄（上段→中段→下段、左から右）
    r1 = st.columns(4)
    with r1[0]:
        b1 = st.text_input("上段1（左上）", value="1")
    with r1[1]:
        b2 = st.text_input("上段2", value="2")
    with r1[2]:
        b3 = st.text_input("上段3", value="3")
    with r1[3]:
        b4 = st.text_input("上段4（右上）", value="4")

    r2 = st.columns(4)
    with r2[0]:
        b5 = st.text_input("中段1（左）", value="5")
    with r2[1]:
        b6 = st.text_input("中段2", value="6")
    with r2[2]:
        b7 = st.text_input("中段3", value="7")
    with r2[3]:
        b8 = st.text_input("中段4（右）", value="8")

    r3 = st.columns(4)
    with r3[0]:
        b9 = st.text_input("下段1（左下）", value="9")
    with r3[1]:
        b10 = st.text_input("下段2", value="10")
    with r3[2]:
        b11 = st.text_input("下段3", value="11")
    with r3[3]:
        b12 = st.text_input("下段4（右下）", value="12")

    bases = [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12]

else:
    base1 = st.text_input("左列の数字（半角）", value="1")
    base2 = st.text_input("中列の数字（半角）", value="2")
    base3 = st.text_input("右列の数字（半角）", value="3")
    bases = [base1, base2, base3]

# 処理とZIP作成
if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: int(''.join(filter(str.isdigit, x.name)) or 0))

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as zipf:
        for i, up in enumerate(uploaded_files):
            img = Image.open(up).convert("RGB")

            if "3x2" in split_mode:
                mode = "3x2"
            elif "3x3" in split_mode:
                mode = "3x3"
            elif "4x3" in split_mode:
                mode = "4x3"
            else:
                mode = "3x1"

            # 1) 分割（列間は左右のみマージン）
            parts = split_image(img, mode=mode)

            # 2) 各ピースを「高さそのまま・左右だけ」で 4:5 に統一（= 横幅 h*4/5 へ）
            parts = [pad_to_ratio_4_5(p, bg=(255,255,255)) for p in parts]

            # 3) 書き出しファイル名（共通番号を付けない設定に対応）
            current_series_num = (series_start + i) if not no_series_in_parentheses else None

            for im, b in zip(parts, bases):
                if current_series_num is None:
                    filename = f"taishi_{b}.jpg"
                else:
                    filename = f"taishi_{b}({current_series_num}).jpg"
                zipf.writestr(filename, image_to_bytes(im))

    st.download_button(
        label="⬇️ 一括ダウンロード（ZIP）",
        data=zip_buffer.getvalue(),
        file_name="taishi_images.zip",
        mime="application/zip"
    )

    st.success("✅ 完了！4:5に整形＆ファイル名の()内共通番号の有無を切り替えました。")
