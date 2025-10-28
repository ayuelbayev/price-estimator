import streamlit as st
import pandas as pd

# Настройки страницы
st.set_page_config(page_title="📘 Смета по прайсу", page_icon="📘", layout="wide")

st.title("📘 Смета по прайсу")
st.write("Загрузите прайс-лист в формате **CSV** или **Excel (.xlsx)**, затем выберите позиции для расчёта.")

# --- Загрузка файла ---
uploaded = st.file_uploader("📂 Загрузите прайс-лист", type=["csv", "xlsx"])

if uploaded:
    # Определяем формат файла
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
        st.stop()

    # Проверяем нужные колонки
    required_cols = {'наименование', 'цена', 'ед изм'}
    if not required_cols.issubset(df.columns):
        st.error("❌ В файле должны быть колонки: 'наименование', 'цена', 'ед изм' (и необязательно 'примечание').")
        st.stop()

    # Подготовка данных
    df['примечание'] = df.get('примечание', '').fillna('')
    df['ключ'] = df.apply(
        lambda r: f"{r['наименование']} | {r['примечание']}" if r['примечание'] else r['наименование'],
        axis=1
    )

    price_lookup = df.set_index('ключ')['цена'].to_dict()
    unit_lookup = df.set_index('ключ')['ед изм'].to_dict()

    st.success("✅ Прайс-лист успешно загружен!")

    # --- Добавление позиций ---
    st.subheader("🧾 Выбор позиций для сметы")

    names = list(price_lookup.keys())
    selected = st.multiselect("Выберите позиции из прайса:", names)

    markup = st.number_input("Введите наценку (%)", value=11.0, step=0.5)

    total = 0
    rows = []

    for name in selected:
        unit = unit_lookup.get(name, "шт")
        price = price_lookup.get(name, 0)
        qty = st.number_input(f"{name} ({unit})", min_value=0.0, step=1.0, value=1.0, key=name)

        subtotal = price * qty
        total += subtotal
        rows.append({
            "Наименование": name,
            "Ед. изм": unit,
            "Кол-во": qty,
            "Цена": price,
            "Сумма": subtotal
        })

    # --- Вывод результатов ---
    if rows:
        st.divider()
        smeta_df = pd.DataFrame(rows)
        smeta_df['Сумма'] = smeta_df['Сумма'].round(0)
        smeta_df['Цена'] = smeta_df['Цена'].round(0)

        st.subheader("📋 Смета")
        st.dataframe(smeta_df, use_container_width=True)

        total_final = total * (1 + markup / 100)
        st.markdown(f"### 💰 Итого без наценки: **{total:,.0f} ₸**")
        st.markdown(f"### 💰 Итого с наценкой {markup:.1f}%: **{total_final:,.0f} ₸**")

        # --- Скачивание результата ---
        csv = smeta_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="⬇️ Скачать смету (CSV)",
            data=csv,
            file_name="smeta.csv",
            mime="text/csv"
        )
    else:
        st.info("👆 Выберите хотя бы одну позицию для расчёта.")

else:
    st.info("📄 Загрузите CSV или XLSX-файл, чтобы начать работу.")
