import io
import zipfile
import pandas as pd
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y CATÁLOGOS
# ==========================================
st.set_page_config(
    page_title="Generador Formatos SEP 911",
    page_icon="📄",
    layout="centered",
)

CARRERAS_LIC = [
    "ACT", "ADM", "CDS", "COM", "CON", "CPOL", "DER", "DFI",
    "ECO", "IA", "IND", "MAT", "MCT", "MKT", "NEG", "RRI",
]

CARRERAS_POS = [
    "MBA", "MERCA", "MTIA-FIN",
]

TRADUCCIONES_PAISES = {
    "AFGHANISTAN": "Afganistán", "ALBANIA": "Albania", "ALGERIA": "Argelia",
    "ANDORRA": "Andorra", "ANGOLA": "Angola", "ANTIGUA AND BARBUDA": "Antigua y barbuda",
    "ARGENTINA": "Argentina", "ARMENIA": "Armenia", "AUSTRALIA": "Australia",
    "AUSTRIA": "Austria", "AZERBAIJAN": "Azerbaiyán", "BAHAMAS": "Bahamas",
    "BAHRAIN": "Baréin", "BANGLADESH": "Bangladés", "BARBADOS": "Barbados",
    "BELARUS": "Bielorrusia", "BELGIUM": "Bélgica", "BELIZE": "Belice",
    "BENIN": "Benín", "BHUTAN": "Bután", "BOLIVIA": "Bolivia",
    "BOSNIA AND HERZEGOVINA": "Bosnia y herzegovina", "BOTSWANA": "Botsuana",
    "BRAZIL": "Brasil", "BRUNEI": "Brunéi", "BULGARIA": "Bulgaria",
    "BURKINA FASO": "Burkina faso", "BURUNDI": "Burundi", "CABO VERDE": "Cabo verde",
    "CAMBODIA": "Camboya", "CAMEROON": "Camerún", "CANADA": "Canadá",
    "CENTRAL AFRICAN REPUBLIC": "República centroafricana", "CHAD": "Chad",
    "CHILE": "Chile", "CHINA": "China", "COLOMBIA": "Colombia",
    "COMOROS": "Comoras", "CONGO": "Congo", "COSTA RICA": "Costa rica",
    "CROATIA": "Croacia", "CUBA": "Cuba", "CYPRUS": "Chipre",
    "CZECH REPUBLIC": "República checa",
    "DEMOCRATIC REPUBLIC OF THE CONGO": "República democrática del congo",
    "DENMARK": "Dinamarca", "DJIBOUTI": "Yibuti", "DOMINICA": "Dominica",
    "DOMINICAN REPUBLIC": "República dominicana", "EAST TIMOR": "Timor oriental",
    "ECUADOR": "Ecuador", "EGYPT": "Egipto", "EL SALVADOR": "El salvador",
    "EQUATORIAL GUINEA": "Guinea ecuatorial", "ERITREA": "Eritrea",
    "ESTONIA": "Estonia", "ESWATINI": "Esuatini", "ETHIOPIA": "Etiopía",
    "FIJI": "Fiyi", "FINLAND": "Finlandia", "FRANCE": "Francia",
    "GABON": "Gabón", "GAMBIA": "Gambia", "GEORGIA": "Georgia",
    "GERMANY": "Alemania", "GHANA": "Ghana", "GREECE": "Grecia",
    "GRENADA": "Granada", "GUATEMALA": "Guatemala", "GUINEA": "Guinea",
    "GUINEA-BISSAU": "Guinea-bisáu", "GUYANA": "Guyana", "HAITI": "Haití",
    "HONDURAS": "Honduras", "HUNGARY": "Hungría", "ICELAND": "Islandia",
    "INDIA": "India", "INDONESIA": "Indonesia", "IRAN": "Irán",
    "IRAQ": "Irak", "IRELAND": "Irlanda", "ISRAEL": "Israel",
    "ITALY": "Italia", "IVORY COAST": "Costa de marfil", "JAMAICA": "Jamaica",
    "JAPAN": "Japón", "JORDAN": "Jordania", "KAZAKHSTAN": "Kazajistán",
    "KENYA": "Kenia", "KIRIBATI": "Kiribati", "KOSOVO": "Kosovo",
    "KUWAIT": "Kuwait", "KYRGYZSTAN": "Kirguistán", "LAOS": "Laos",
    "LATVIA": "Letonia", "LEBANON": "Líbano", "LESOTHO": "Lesoto",
    "LIBERIA": "Liberia", "LIBYA": "Libia", "LIECHTENSTEIN": "Liechtenstein",
    "LITHUANIA": "Lituania", "LUXEMBOURG": "Luxemburgo", "MADAGASCAR": "Madagascar",
    "MALAWI": "Malaui", "MALAYSIA": "Malasia", "MALDIVES": "Maldivas",
    "MALI": "Malí", "MALTA": "Malta", "MARSHALL ISLANDS": "Islas marshall",
    "MAURITANIA": "Mauritania", "MAURITIUS": "Mauricio", "MEXICO": "México",
    "MICRONESIA": "Micronesia", "MOLDOVA": "Moldavia", "MONACO": "Mónaco",
    "MONGOLIA": "Mongolia", "MONTENEGRO": "Montenegro", "MOROCCO": "Marruecos",
    "MOZAMBIQUE": "Mozambique", "MYANMAR": "Birmania", "NAMIBIA": "Namibia",
    "NAURU": "Nauru", "NEPAL": "Nepal", "NETHERLANDS": "Países bajos",
    "NEW ZEALAND": "Nueva zelanda", "NICARAGUA": "Nicaragua", "NIGER": "Níger",
    "NIGERIA": "Nigeria", "NORTH KOREA": "Corea del norte",
    "NORTH MACEDONIA": "Macedonia del norte", "NORWAY": "Noruega", "OMAN": "Omán",
    "PAKISTAN": "Pakistán", "PALAU": "Palaos", "PALESTINE": "Palestina",
    "PANAMA": "Panamá", "PAPUA NEW GUINEA": "Papúa nueva guinea",
    "PARAGUAY": "Paraguay", "PERU": "Perú", "PHILIPPINES": "Filipinas",
    "POLAND": "Polonia", "PORTUGAL": "Portugal", "QATAR": "Catar",
    "ROMANIA": "Rumania", "RUSSIA": "Rusia", "RWANDA": "Ruanda",
    "SAINT KITTS AND NEVIS": "San cristóbal y nieves", "SAINT LUCIA": "Santa lucía",
    "SAINT VINCENT AND THE GRENADINES": "San vicente y las granadinas",
    "SAMOA": "Samoa", "SAN MARINO": "San marino",
    "SAO TOME AND PRINCIPE": "Santo tomé y príncipe", "SAUDI ARABIA": "Arabia saudita",
    "SENEGAL": "Senegal", "SERBIA": "Serbia", "SEYCHELLES": "Seychelles",
    "SIERRA LEONE": "Sierra leona", "SINGAPORE": "Singapur", "SLOVAKIA": "Eslovaquia",
    "SLOVENIA": "Eslovenia", "SOLOMON ISLANDS": "Islas salomón", "SOMALIA": "Somalia",
    "SOUTH AFRICA": "Sudáfrica", "SOUTH KOREA": "Corea del sur",
    "SOUTH SUDAN": "Sudán del sur", "SPAIN": "España", "SRI LANKA": "Sri lanka",
    "SUDAN": "Sudán", "SURINAME": "Surinam", "SWEDEN": "Suecia",
    "SWITZERLAND": "Suiza", "SYRIA": "Siria", "TAIWAN": "Taiwán",
    "TAJIKISTAN": "Tayikistán", "TANZANIA": "Tanzania", "THAILAND": "Tailandia",
    "TOGO": "Togo", "TONGA": "Tonga", "TRINIDAD AND TOBAGO": "Trinidad y tobago",
    "TUNISIA": "Túnez", "TURKEY": "Turquía", "TURKMENISTAN": "Turkmenistán",
    "TUVALU": "Tuvalu", "UGANDA": "Uganda", "UKRAINE": "Ucrania",
    "UNITED ARAB EMIRATES": "Emiratos árabes unidos", "UNITED KINGDOM": "Reino unido",
    "UNITED STATES": "Estados unidos", "URUGUAY": "Uruguay",
    "UZBEKISTAN": "Uzbekistán", "VANUATU": "Vanuatu",
    "VATICAN CITY": "Ciudad del vaticano", "VENEZUELA": "Venezuela",
    "VIETNAM": "Vietnam", "YEMEN": "Yemen", "ZAMBIA": "Zambia", "ZIMBABWE": "Zimbabue",
}

# Coordenadas Licenciatura (911.9A)
COORD_LIC = {
    "TOTALES_X": {"H": 365, "M": 447, "T": 529, "ENTIDAD_PAIS_1": 611, "ENTIDAD_PAIS_2": 693},
    "TOTALES_Y": 465,
    "PAISES_X": {
        "Nombre": 68, "H": 288, "M": 360, "T": 438,
        "T_VALOR": 522, "T_SIN_VALOR": 604, "FINANCIAMIENTO": 686,
    },
    "PAISES_Y_INICIO": 122.0,
    "PAISES_Y_SALTO": 15.8,
}

# Coordenadas Posgrado (911.9B)
COORD_POS_PAG3_TOT = {"Y": 66.5, "H": 415.3, "M": 483.6, "T": 558.9, "ENTIDAD": 636.2, "PAIS": 705.6}
COORD_POS_PAG4_PAISES = {
    "X": {"Nombre": 68, "H": 293.3, "M": 363.4, "T": 441.2, "T_VALOR": 525.3, "T_SIN_VALOR": 608.1, "FINANCIAMIENTO": 704.2},
    "Y_INICIO": 137.5, "Y_SALTO": 20.4,
}
COORD_POS_PAG5_TOT = {"Y": 484.3, "H": 371.9, "M": 440.0, "T": 516.8, "ENTIDAD": 608.1, "PAIS": 697.9}
COORD_POS_PAG5_PAISES = {
    "X": {"Nombre": 68, "H": 292.4, "M": 362.5, "T": 440.3, "T_VALOR": 524.4, "T_SIN_VALOR": 607.2, "FINANCIAMIENTO": 703.3},
    "Y_INICIO": 122.6, "Y_SALTO": 20.4,
}

# ==========================================
# 2. FUNCIONES COMPARTIDAS DE EXTRACCIÓN
# ==========================================
def traducir_pais(pais_original):
    pais = str(pais_original).strip()
    return TRADUCCIONES_PAISES.get(pais.upper(), pais.capitalize())

def extraer_datos_por_bloques(excel_bytes, sheet_name, lista_carreras, es_posgrado=False):
    try:
        df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=sheet_name)
    except Exception:
        return {}

    ignorar_filas = lista_carreras + ["TOTAL", "total", "T", "H", "M", "h", "m", "t", "F", "f"]
    datos_extraidos = {}
    num_columnas = len(df.columns)

    for i in range(num_columnas):
        carrera_col = str(df.columns[i]).strip()

        if es_posgrado:
            if carrera_col not in lista_carreras and not carrera_col.isupper():
                continue
        else:
            if carrera_col not in lista_carreras:
                continue

        bloque = df.iloc[:, i : min(i + 5, num_columnas)].copy()
        while bloque.shape[1] < 5:
            bloque[f"Col_Extra_{bloque.shape[1]}"] = None

        bloque.columns = ["Pais_Genero", "Val1", "Val2", "Val3", "Val4"]
        bloque = bloque.dropna(how="all")

        idx_separador = bloque[(bloque["Pais_Genero"] == carrera_col) | (bloque["Val1"] == "H")].index

        if not idx_separador.empty:
            idx_sep = idx_separador[0]
            df_individuales = bloque.loc[: idx_sep - 1]
            df_resumen = bloque.loc[idx_sep + 1 :]
        else:
            df_individuales = bloque[bloque["Val1"].isin(["Male", "Female"])]
            df_resumen = bloque[~bloque["Val1"].isin(["Male", "Female"])]

        hombres_tot = len(df_individuales[df_individuales["Val1"] == "Male"])
        mujeres_tot = len(df_individuales[df_individuales["Val1"] == "Female"])

        lista_paises = []
        for _, fila in df_resumen.iterrows():
            pais_crudo = str(fila["Pais_Genero"]).strip()
            if (
                pd.isna(fila["Pais_Genero"])
                or pais_crudo.lower() in ["nan", "none", ""]
                or pais_crudo in ignorar_filas
                or pais_crudo.isdigit()
            ):
                continue

            pais_traducido = traducir_pais(pais_crudo)
            try:
                h = int(fila["Val1"]) if pd.notna(fila["Val1"]) and str(fila["Val1"]).strip().isdigit() else 0
                m = int(fila["Val2"]) if pd.notna(fila["Val2"]) and str(fila["Val2"]).strip().isdigit() else 0
                t = int(fila["Val3"]) if pd.notna(fila["Val3"]) and str(fila["Val3"]).strip().isdigit() else (h + m)
                f = 0 if es_posgrado else (
                    int(fila["Val4"]) if pd.notna(fila["Val4"]) and str(fila["Val4"]).strip().isdigit() else 0
                )
            except (ValueError, TypeError):
                continue

            lista_paises.append({"Pais": pais_traducido, "H": h, "M": m, "T": t, "F": f})

        datos_extraidos[carrera_col] = {
            "H_Total": hombres_tot,
            "M_Total": mujeres_tot,
            "Paises": lista_paises,
        }

    return datos_extraidos

def agregar_pagina_con_capa(pdf_writer, pdf_bytes, indice_pagina, capa_reader):
    """Compatibilidad con pypdf >= 7.0.0: primero adjunta la página al writer y luego fusiona la capa."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pdf_writer.add_page(reader.pages[indice_pagina])
    pdf_writer.pages[-1].merge_page(capa_reader.pages[0])

# ==========================================
# 3. MOTOR LICENCIATURA (911.9A)
# ==========================================
def crear_capa_lic(datos_totales, lista_paises, es_primera_pagina):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(letter))
    can.setFont("Helvetica-Bold", 9)

    if es_primera_pagina and datos_totales is not None:
        h_tot = datos_totales.get("H_Total", 0)
        m_tot = datos_totales.get("M_Total", 0)
        total_global = h_tot + m_tot
        y_tot = COORD_LIC["TOTALES_Y"]

        can.drawString(COORD_LIC["TOTALES_X"]["H"], y_tot, str(h_tot))
        can.drawString(COORD_LIC["TOTALES_X"]["M"], y_tot, str(m_tot))
        can.drawString(COORD_LIC["TOTALES_X"]["T"], y_tot, str(total_global))
        can.drawString(COORD_LIC["TOTALES_X"]["ENTIDAD_PAIS_1"], y_tot, "0")
        can.drawString(COORD_LIC["TOTALES_X"]["ENTIDAD_PAIS_2"], y_tot, str(total_global))

    y_pais = COORD_LIC["PAISES_Y_INICIO"]
    for pais in lista_paises:
        can.drawString(COORD_LIC["PAISES_X"]["Nombre"], y_pais, str(pais["Pais"]))
        can.drawString(COORD_LIC["PAISES_X"]["H"], y_pais, str(pais["H"]))
        can.drawString(COORD_LIC["PAISES_X"]["M"], y_pais, str(pais["M"]))
        can.drawString(COORD_LIC["PAISES_X"]["T"], y_pais, str(pais["T"]))
        can.drawString(COORD_LIC["PAISES_X"]["T_VALOR"], y_pais, str(pais["T"]))
        can.drawString(COORD_LIC["PAISES_X"]["T_SIN_VALOR"], y_pais, "0")
        can.drawString(COORD_LIC["PAISES_X"]["FINANCIAMIENTO"], y_pais, str(pais.get("F", 0)))
        y_pais -= COORD_LIC["PAISES_Y_SALTO"]

    can.save()
    packet.seek(0)
    return PdfReader(packet)

def procesar_licenciatura(pdf_bytes, excel_bytes, carreras_seleccionadas):
    datos_out = extraer_datos_por_bloques(excel_bytes, "OUT-LIC", CARRERAS_LIC, es_posgrado=False)
    datos_in = extraer_datos_por_bloques(excel_bytes, "IN-LIC", CARRERAS_LIC, es_posgrado=False)
    archivos_generados = {}

    for carrera in carreras_seleccionadas:
        c_out = datos_out.get(carrera, {"H_Total": 0, "M_Total": 0, "Paises": []})
        c_in = datos_in.get(carrera, {"H_Total": 0, "M_Total": 0, "Paises": []})
        pdf_writer = PdfWriter()

        # OUT-LIC
        chunks_out = [c_out["Paises"][i : i + 5] for i in range(0, max(1, len(c_out["Paises"])), 5)]
        for idx, chunk in enumerate(chunks_out):
            es_primera = idx == 0
            capa = crear_capa_lic(c_out if es_primera else None, chunk, es_primera)
            agregar_pagina_con_capa(pdf_writer, pdf_bytes, 4, capa)

        # IN-LIC
        chunks_in = [c_in["Paises"][i : i + 5] for i in range(0, max(1, len(c_in["Paises"])), 5)]
        for idx, chunk in enumerate(chunks_in):
            es_primera = idx == 0
            capa = crear_capa_lic(c_in if es_primera else None, chunk, es_primera)
            agregar_pagina_con_capa(pdf_writer, pdf_bytes, 5, capa)

        out_stream = io.BytesIO()
        pdf_writer.write(out_stream)
        archivos_generados[f"{carrera}.pdf"] = out_stream.getvalue()

    return archivos_generados

# ==========================================
# 4. MOTOR POSGRADO (911.9B)
# ==========================================
def crear_capa_pos_pag3(datos_totales):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(letter))
    can.setFont("Helvetica-Bold", 9)

    h_tot = datos_totales.get("H_Total", 0) if datos_totales else 0
    m_tot = datos_totales.get("M_Total", 0) if datos_totales else 0
    total_global = h_tot + m_tot
    y_tot = COORD_POS_PAG3_TOT["Y"] - 3

    can.drawCentredString(COORD_POS_PAG3_TOT["H"], y_tot, str(h_tot))
    can.drawCentredString(COORD_POS_PAG3_TOT["M"], y_tot, str(m_tot))
    can.drawCentredString(COORD_POS_PAG3_TOT["T"], y_tot, str(total_global))
    can.drawCentredString(COORD_POS_PAG3_TOT["ENTIDAD"], y_tot, "0")
    can.drawCentredString(COORD_POS_PAG3_TOT["PAIS"], y_tot, str(total_global))

    can.save()
    packet.seek(0)
    return PdfReader(packet)

def crear_capa_pos_pag4(lista_paises):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(letter))
    can.setFont("Helvetica-Bold", 9)

    y_pais = COORD_POS_PAG4_PAISES["Y_INICIO"] - 3
    for pais in lista_paises:
        can.drawString(COORD_POS_PAG4_PAISES["X"]["Nombre"], y_pais, str(pais["Pais"]))
        can.drawCentredString(COORD_POS_PAG4_PAISES["X"]["H"], y_pais, str(pais["H"]))
        can.drawCentredString(COORD_POS_PAG4_PAISES["X"]["M"], y_pais, str(pais["M"]))
        can.drawCentredString(COORD_POS_PAG4_PAISES["X"]["T"], y_pais, str(pais["T"]))
        can.drawCentredString(COORD_POS_PAG4_PAISES["X"]["T_VALOR"], y_pais, str(pais["T"]))
        can.drawCentredString(COORD_POS_PAG4_PAISES["X"]["T_SIN_VALOR"], y_pais, "0")
        can.drawCentredString(COORD_POS_PAG4_PAISES["X"]["FINANCIAMIENTO"], y_pais, "0")
        y_pais -= COORD_POS_PAG4_PAISES["Y_SALTO"]

    can.save()
    packet.seek(0)
    return PdfReader(packet)

def crear_capa_pos_pag5(datos_totales, lista_paises, es_primera_pagina):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(letter))
    can.setFont("Helvetica-Bold", 9)

    if es_primera_pagina:
        h_tot = datos_totales.get("H_Total", 0) if datos_totales else 0
        m_tot = datos_totales.get("M_Total", 0) if datos_totales else 0
        total_global = h_tot + m_tot
        y_tot = COORD_POS_PAG5_TOT["Y"] - 3

        can.drawCentredString(COORD_POS_PAG5_TOT["H"], y_tot, str(h_tot))
        can.drawCentredString(COORD_POS_PAG5_TOT["M"], y_tot, str(m_tot))
        can.drawCentredString(COORD_POS_PAG5_TOT["T"], y_tot, str(total_global))
        can.drawCentredString(COORD_POS_PAG5_TOT["ENTIDAD"], y_tot, "0")
        can.drawCentredString(COORD_POS_PAG5_TOT["PAIS"], y_tot, str(total_global))

    y_pais = COORD_POS_PAG5_PAISES["Y_INICIO"] - 3
    for pais in lista_paises:
        can.drawString(COORD_POS_PAG5_PAISES["X"]["Nombre"], y_pais, str(pais["Pais"]))
        can.drawCentredString(COORD_POS_PAG5_PAISES["X"]["H"], y_pais, str(pais["H"]))
        can.drawCentredString(COORD_POS_PAG5_PAISES["X"]["M"], y_pais, str(pais["M"]))
        can.drawCentredString(COORD_POS_PAG5_PAISES["X"]["T"], y_pais, str(pais["T"]))
        can.drawCentredString(COORD_POS_PAG5_PAISES["X"]["T_VALOR"], y_pais, str(pais["T"]))
        can.drawCentredString(COORD_POS_PAG5_PAISES["X"]["T_SIN_VALOR"], y_pais, "0")
        can.drawCentredString(COORD_POS_PAG5_PAISES["X"]["FINANCIAMIENTO"], y_pais, "0")
        y_pais -= COORD_POS_PAG5_PAISES["Y_SALTO"]

    can.save()
    packet.seek(0)
    return PdfReader(packet)

def procesar_posgrado(pdf_bytes, excel_bytes, carreras_seleccionadas):
    datos_out = extraer_datos_por_bloques(excel_bytes, "OUT-MTIA", CARRERAS_POS, es_posgrado=True)
    datos_in = extraer_datos_por_bloques(excel_bytes, "IN-MTIA", CARRERAS_POS, es_posgrado=True)
    archivos_generados = {}

    for carrera in carreras_seleccionadas:
        c_out = datos_out.get(carrera, {"H_Total": 0, "M_Total": 0, "Paises": []})
        c_in = datos_in.get(carrera, {"H_Total": 0, "M_Total": 0, "Paises": []})

        has_out = (c_out["H_Total"] + c_out["M_Total"] + len(c_out["Paises"])) > 0
        has_in = (c_in["H_Total"] + c_in["M_Total"] + len(c_in["Paises"])) > 0
        omitir_paginas_3_y_4 = (not has_out) and has_in

        pdf_writer = PdfWriter()

        # Saliente (OUT-MTIA)
        if not omitir_paginas_3_y_4:
            paises_out = c_out["Paises"]
            chunks_out = [paises_out[i : i + 5] for i in range(0, len(paises_out), 5)] if paises_out else [[]]
            for idx, chunk in enumerate(chunks_out):
                if idx == 0:
                    capa_pag3 = crear_capa_pos_pag3(c_out if has_out else {"H_Total": 0, "M_Total": 0})
                    agregar_pagina_con_capa(pdf_writer, pdf_bytes, 2, capa_pag3)

                capa_pag4 = crear_capa_pos_pag4(chunk)
                agregar_pagina_con_capa(pdf_writer, pdf_bytes, 3, capa_pag4)

        # Entrante (IN-MTIA)
        paises_in = c_in["Paises"]
        chunks_in = [paises_in[i : i + 5] for i in range(0, len(paises_in), 5)] if paises_in else [[]]
        for idx, chunk in enumerate(chunks_in):
            es_primera = idx == 0
            capa_pag5 = crear_capa_pos_pag5(
                (c_in if has_in else {"H_Total": 0, "M_Total": 0}) if es_primera else None,
                chunk,
                es_primera,
            )
            agregar_pagina_con_capa(pdf_writer, pdf_bytes, 4, capa_pag5)

        out_stream = io.BytesIO()
        pdf_writer.write(out_stream)
        archivos_generados[f"{carrera}_POSGRADO.pdf"] = out_stream.getvalue()

    return archivos_generados

# ==========================================
# 5. INTERFAZ WEB (STREAMLIT)
# ==========================================
st.title("📄 Generador de Formatos SEP 911")
st.markdown("Selecciona el nivel académico, sube el formato base en PDF y el archivo Excel con los datos.")

nivel = st.radio(
    "1. Selecciona el nivel académico:",
    options=["Licenciatura (Formato 911.9A)", "Posgrado (Formato 911.9B)"],
    horizontal=True,
)

es_posgrado = "Posgrado" in nivel

col1, col2 = st.columns(2)
with col1:
    archivo_pdf = st.file_uploader(
        "2. Sube el formato PDF base:",
        type=["pdf"],
        help="Sube CARRERA 911.9A.pdf para Licenciatura o POSGRADO 911.9B.pdf para Posgrado.",
    )
with col2:
    archivo_excel = st.file_uploader(
        "3. Sube el archivo Excel con datos:",
        type=["xlsx", "xls"],
        help="Sube SEP_LIC.xlsx (pestañas OUT-LIC / IN-LIC) o SEP_MAESTRIAS.xlsx (pestañas OUT-MTIA / IN-MTIA).",
    )

catalogo_base = CARRERAS_POS if es_posgrado else CARRERAS_LIC
seleccion_carreras = st.multiselect(
    "4. Programas a generar (déjalo vacío para generar TODOS):",
    options=sorted(catalogo_base),
    default=[],
)

if st.button("🚀 Generar PDFs", type="primary", use_container_width=True):
    if not archivo_pdf or not archivo_excel:
        st.error("⚠️ Por favor sube tanto el archivo PDF base como el archivo Excel antes de continuar.")
    else:
        with st.spinner("Procesando información y llenando formatos..."):
            try:
                pdf_bytes = archivo_pdf.read()
                excel_bytes = archivo_excel.read()

                carreras_a_procesar = seleccion_carreras if seleccion_carreras else catalogo_base

                if es_posgrado:
                    pdfs_dict = procesar_posgrado(pdf_bytes, excel_bytes, carreras_a_procesar)
                    nombre_zip = "Formatos_SEP_Posgrado_911_9B.zip"
                else:
                    pdfs_dict = procesar_licenciatura(pdf_bytes, excel_bytes, carreras_a_procesar)
                    nombre_zip = "Formatos_SEP_Licenciatura_911_9A.zip"

                # Crear archivo ZIP en memoria
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for filename, file_bytes in pdfs_dict.items():
                        zf.writestr(filename, file_bytes)
                zip_buffer.seek(0)

                st.success(f"✅ ¡Listo! Se generaron {len(pdfs_dict)} archivos PDF correctamente.")
                st.download_button(
                    label=f"⬇️ Descargar {nombre_zip}",
                    data=zip_buffer,
                    file_name=nombre_zip,
                    mime="application/zip",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ Ocurrió un error al procesar los archivos: {e}")