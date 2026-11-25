import streamlit as st
from PIL import Image
import requests
import base64
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="Tecmo | مكتبة الصور المشتركة", page_icon="🖼️", layout="wide")

GOOGLE_DRIVE_WEBHOOK_URL = "https://google.com"

MEDIA_FOLDER = "tecmo_media_files"
METADATA_FILE = "tecmo_media_metadata.json"
CATEGORIES_FILE = "tecmo_media_categories.json"

os.makedirs(MEDIA_FOLDER, exist_ok=True)

DEFAULT_CATEGORIES = [
    "مشاريع المقاولات والإنشاءات",
    "المصانع وخطوط الإنتاج",
    "الصيانة والتشغيل (O&M)",
    "الأمن والسلامة المهنية (HSE)",
    "المعدات والآليات الثقيلة",
    "الموارد البشرية والفعاليات",
    "الهوية البصرية والتصاميم الجاهزة"
]

def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
            cats = json.load(f)
            return cats if cats else ["عام"]
    save_categories(DEFAULT_CATEGORIES)
    return DEFAULT_CATEGORIES

def save_categories(cats):
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(list(dict.fromkeys(cats)), f, ensure_ascii=False, indent=2)

def load_media_db():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_media_db(records):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def check_platform_fit(width, height):
    ratio = width / height if height > 0 else 1
    if 0.9 <= ratio <= 1.1:
        return "مربعة (مناسبة لـ Instagram)"
    elif ratio > 1.1:
        return "عريضة (مناسبة لـ LinkedIn و X)"
    else:
        return "طولية (مناسبة لـ Reels و TikTok)"

st.markdown("""
<style>
@import url('https://googleapis.com');
html, body, [class*="css"] { font-family: 'IBM Plex Sans Arabic', sans-serif; direction: rtl; text-align: right; }
.stApp { background: linear-gradient(180deg, #eef5ff 0%, #ffffff 40%, #f7faff 100%); }
.header-banner {
    background: #ffffff;
    border-top: 6px solid #0052cc;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 6px 20px rgba(0, 82, 204, 0.08);
    text-align: center;
    margin-bottom: 20px;
}
.header-banner h1 { color: #091e42; font-size: 26px; font-weight: 700; margin: 6px 0; }
.header-banner p { color: #0052cc; font-size: 15px; margin: 0; }
.photo-card {
    background: #ffffff;
    border: 1px solid #deebff;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 4px 14px rgba(9, 30, 66, 0.05);
    margin-bottom: 16px;
}
.tag-badge {
    display: inline-block;
    background: #deebff;
    color: #0052cc;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.date-line {
    color: #42526e;
    font-size: 13px;
    font-weight: 600;
    margin-top: 6px;
}
.comment-box {
    background: #f4f7fb;
    border-right: 3px solid #0052cc;
    padding: 8px 12px;
    border-radius: 6px;
    color: #172b4d;
    font-size: 13px;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>🖼️ مكتبة تكمو المرئية المشتركة</h1>
    <p>منصة سحابية موحدة لجميع الأقسام لرفع وتصنيف وتصفح صور المشاريع والمصانع والفعاليات</p>
</div>
""", unsafe_allow_html=True)

records = load_media_db()
categories = load_categories()
cities_list = ["الدمام", "الخبر", "الظهران", "الجبيل", "الأحساء", "القطيف", "الرياض", "جدة", "مكة المكرمة", "المدينة المنورة", "أبها", "تبوك", "نيوم", "أخرى"]

tab_gallery, tab_upload, tab_cats = st.tabs([
    "📂 تصفح المكتبة المشتركة",
    "📤 رفع صور جديدة",
    "⚙️ إدارة التصنيفات (إضافة / تعديل / حذف)"
])
with tab_gallery:
    if not records:
        st.info("المكتبة فارغة حالياً. انتقل إلى تبويب **📤 رفع صور جديدة** لإضافة أول صورة!")
    else:
        col_f1, col_f2, col_f3 = st.columns([1.2, 1.5, 1])
        with col_f1:
            filter_cat = st.selectbox("تصفية حسب التصنيف:", ["الكل"] + categories)
        with col_f2:
            search_query = st.text_input("🔍 بحث في العنوان أو التعليق أو المدينة:", placeholder="اكتب كلمة للبحث...")
        with col_f3:
            sort_order = st.selectbox("الترتيب:", ["الأحدث تاريخاً", "الأقدم تاريخاً"])

        filtered = records
        if filter_cat != "الكل":
            filtered = [r for r in filtered if r.get("category") == filter_cat]
        if search_query.strip():
            q = search_query.strip().lower()
            filtered = [r for r in filtered if q in r.get("title", "").lower() or q in r.get("comment", "").lower() or q in r.get("city", "").lower()]
        
        filtered = sorted(filtered, key=lambda x: x.get("photo_date", ""), reverse=(sort_order == "الأحدث تاريخاً"))

        st.caption(f"عرض **{len(filtered)}** صورة من إجمالي **{len(records)}** في المكتبة")
        
        cols = st.columns(3)
        for idx, item in enumerate(filtered):
            with cols[idx % 3]:
                st.markdown("<div class='photo-card'>", unsafe_allow_html=True)
                img_path = item.get("local_path", "")
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                elif item.get("drive_view_url"):
                    st.image(item["drive_view_url"], use_container_width=True)
                
                st.markdown(f"<span class='tag-badge'>{item.get('category', 'عام')}</span> &nbsp; <span style='color:#5e6c84; font-size:12px;'>📍 {item.get('city', '')}</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='date-line'>📅 التاريخ: {item.get('photo_date', '')}</div>", unsafe_allow_html=True)
                st.markdown(f"**{item.get('title', 'بدون عنوان')}**")
                st.caption(f"📐 {item.get('platform_fit', '')}")
                
                if item.get("comment", "").strip():
                    st.markdown(f"<div class='comment-box'>💬 {item['comment']}</div>", unsafe_allow_html=True)
                
                if os.path.exists(img_path):
                    with open(img_path, "rb") as f_img:
                        st.download_button(
                            label="📥 تحميل الصورة",
                            data=f_img.read(),
                            file_name=item.get("file_name", "tecmo_photo.jpg"),
                            mime=item.get("mime_type", "image/jpeg"),
                            key=f"dl_{item['id']}"
                        )
                
                with st.expander("✏️ تعديل التصنيف / التاريخ / التعليق"):
                    cur_cat = item.get("category", categories[0])
                    cat_idx = categories.index(cur_cat) if cur_cat in categories else 0
                    new_cat = st.selectbox("تغيير التصنيف:", categories, index=cat_idx, key=f"ecat_{item['id']}")
                    
                    try:
                        parsed_date = datetime.strptime(item.get("photo_date", str(date.today())), "%Y-%m-%d").date()
                    except Exception:
                        parsed_date = date.today()
                    new_date = st.date_input("تغيير التاريخ:", value=parsed_date, key=f"edate_{item['id']}")
                    
                    new_title = st.text_input("تعديل العنوان:", value=item.get("title", ""), key=f"etitle_{item['id']}")
                    new_comment = st.text_input("تعديل التعليق تحت الصورة (اختياري):", value=item.get("comment", ""), key=f"ecom_{item['id']}")
                    
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        if st.button("💾 حفظ", key=f"save_edit_{item['id']}"):
                            for r in records:
                                if r["id"] == item["id"]:
                                    r["category"] = new_cat
                                    r["photo_date"] = str(new_date)
                                    r["title"] = new_title.strip() if new_title.strip() else r["title"]
                                    r["comment"] = new_comment.strip()
                            save_media_db(records)
                            st.success("تم الحفظ!")
                            st.rerun()
                    with c_b2:
                        if st.button("🗑️ حذف الصورة", key=f"del_img_{item['id']}"):
                            if os.path.exists(img_path):
                                try:
                                    os.remove(img_path)
                                except Exception:
                                    pass
                            records = [r for r in records if r["id"] != item["id"]]
                            save_media_db(records)
                            st.warning("تم حذف الصورة")
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

with tab_upload:
    st.subheader("📤 إضافة صور جديدة إلى مكتبة تكمو")
    uploaded_files = st.file_uploader("اختر صورة أو مجموعة صور (JPG, PNG, WEBP):", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    
    c_u1, c_u2 = st.columns(2)
    with c_u1:
        cat_selection = st.selectbox("التصنيف:", categories + ["➕ كتابة تصنيف جديد"])
        if cat_selection == "➕ كتابة تصنيف جديد":
            chosen_category = st.text_input("اكتب اسم التصنيف الجديد:", placeholder="مثال: زيارة وفد، صيانة خط 2...")
        else:
            chosen_category = cat_selection
            
        photo_date = st.date_input("📅 تاريخ الصورة (يمكنك تغييره لأي تاريخ):", value=date.today())

    with c_u2:
        chosen_city = st.selectbox("📍 المدينة / الموقع:", cities_list)
        base_title = st.text_input("عنوان الصورة / المشروع (اختياري):", placeholder="مثال: مشروع صيانة مصنع الجبيل")

    optional_comment = st.text_area("💬 تعليق يظهر تحت الصورة (اختياري):", placeholder="اكتب أي وصف أو ملاحظة تود ظهورها أسفل الصورة (يمكن تركه فارغاً)...", height=90)

    if st.button("🚀 حفظ ونشر في المكتبة المشتركة"):
        if not uploaded_files:
            st.error("⚠️ يرجى اختيار صورة واحدة على الأقل للرفع.")
        elif not chosen_category or not chosen_category.strip():
            st.error("⚠️ يرجى كتابة اسم التصنيف الجديد.")
        else:
            clean_cat = chosen_category.strip()
            if clean_cat not in categories:
                categories.append(clean_cat)
                save_categories(categories)

            with st.spinner("جاري معالجة الصور وحفظها في المكتبة والسحابة..."):
                for up_file in uploaded_files:
                    img = Image.open(up_file)
                    w, h = img.size
                    platform_fit = check_platform_fit(w, h)
                    
                    timestamp_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    safe_filename = f"{timestamp_id}_{up_file.name}"
                    local_path = os.path.join(MEDIA_FOLDER, safe_filename)
                    
                    up_file.seek(0)
                    file_bytes = up_file.read()
                    with open(local_path, "wb") as f_out:
                        f_out.write(file_bytes)
                    
                    final_title = base_title.strip() if base_title.strip() else os.path.splitext(up_file.name)[0]
                    drive_view_url = ""
                    
                    if GOOGLE_DRIVE_WEBHOOK_URL.startswith("https://"):
                        try:
                            b64_img = base64.b64encode(file_bytes).decode("utf-8")
                            res = requests.post(GOOGLE_DRIVE_WEBHOOK_URL, json={
                                "photo_date": str(photo_date),
                                "title": final_title,
                                "category": clean_cat,
                                "city": chosen_city,
                                "platform_fit": platform_fit,
                                "comment": optional_comment.strip(),
                                "file_name": safe_filename,
                                "mime_type": up_file.type,
                                "image_base64": b64_img
                            }, timeout=12)
                            if res.status_code == 200:
                                drive_view_url = res.json().get("view_url", "")
                        except Exception:
                            pass

                    records.append({
                        "id": timestamp_id,
                        "photo_date": str(photo_date),
                        "title": final_title,
                        "category": clean_cat,
                        "city": chosen_city,
                        "platform_fit": platform_fit,
                        "comment": optional_comment.strip(),
                        "file_name": up_file.name,
                        "mime_type": up_file.type,
                        "local_path": local_path,
                        "drive_view_url": drive_view_url
                    })
                
                save_media_db(records)
                st.success(f"✅ تم رفع وحفظ **{len(uploaded_files)}** صورة بنجاح!")

with tab_cats:
    st.subheader("⚙️ التحكم الكامل في تصنيفات المكتبة")
    st.write("يمكنك هنا إضافة تصنيفات جديدة، أو تغيير اسم أي تصنيف حالي، أو حذف التصنيفات غير المستخدمة.")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        st.markdown("#### ➕ إضافة تصنيف جديد")
        add_cat_name = st.text_input("اسم التصنيف الجديد:", placeholder="اكتب اسم التصنيف...")
        if st.button("إضافة التصنيف"):
            if add_cat_name.strip():
                if add_cat_name.strip() not in categories:
                    categories.append(add_cat_name.strip())
                    save_categories(categories)
                    st.success(f"تمت إضافة: {add_cat_name.strip()}")
                    st.rerun()
                else:
                    st.warning("هذا التصنيف موجود مسبقاً.")
            else:
                st.error("يرجى كتابة اسم التصنيف.")

    with col_c2:
        st.markdown("#### ✏️ تغيير اسم تصنيف")
        cat_to_rename = st.selectbox("اختر التصنيف المراد تغييره:", categories, key="rename_select")
        new_cat_label = st.text_input("الاسم الجديد للتصنيف:", placeholder="اكتب الاسم الجديد...")
        if st.button("تحديث الاسم"):
            if new_cat_label.strip():
                updated_cats = [new_cat_label.strip() if c == cat_to_rename else c for c in categories]
                save_categories(updated_cats)
                for r in records:
                    if r.get("category") == cat_to_rename:
                        r["category"] = new_cat_label.strip()
                save_media_db(records)
                st.success(f"تم تغيير الاسم إلى: {new_cat_label.strip()}")
                st.rerun()
            else:
                st.error("يرجى كتابة الاسم الجديد.")

    with col_c3:
        st.markdown("#### 🗑️ حذف تصنيف")
        cat_to_delete = st.selectbox("اختر التصنيف المراد حذفه:", categories, key="delete_select")
        if st.button("حذف التصنيف نهائياً"):
            if len(categories) <= 1:
                st.error("يجب بقاء تصنيف واحد على الأقل في المكتبة.")
            else:
                remaining_cats = [c for c in categories if c != cat_to_delete]
                save_categories(remaining_cats)
                fallback_cat = remaining_cats
                for r in records:
                    if r.get("category") == cat_to_delete:
                        r["category"] = fallback_cat
                save_media_db(records)
                st.warning(f"تم حذف التصنيف ({cat_to_delete}) ونقل صوره إلى ({fallback_cat}).")
                st.rerun()

st.divider()
st.markdown("<div style='text-align: center; color: #091e42; font-size: 13px; font-weight: 600;'>تطوير وتصميم: شركة تكمو وأسيل الأسمري | Developed & Designed by Tecmo & Aseel Al-Asmari © 2026</div>", unsafe_allow_html=True)
