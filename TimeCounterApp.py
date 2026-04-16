from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
"""
Argumente :
(Eingabe) = CSV-Dateien namens TimeCounterTemplate.csv

Rückgabe :
Ausgabe = visuelle Darstellung (Charts + Tabellen)
"""

DATA_DIR = Path(__file__).parent / "TimeCounterData"
INPUT_COLUMNS = [
    "week_label",
    "day_date",
    "day_name",
    "daily_total_minutes",
    "app_rank",
    "app_name",
    "daily_app_minutes",
]
CALCULATED_COLUMNS = [
    "weekly_app_minutes",
    "weekly_total_minutes",
]
REQUIRED_COLUMNS = INPUT_COLUMNS + CALCULATED_COLUMNS

"""
Argumente:
    Keine

Rückgabe:
    pd.DataFrame:
        Beispiel-Datensatz mit Bildschirmzeit-Daten
"""

def build_template_frame() -> pd.DataFrame:
    rows = [
        ["2026-W15", "2026-04-07", "Dienstag", 210, 1, "YouTube", 50],
        ["2026-W15", "2026-04-07", "Dienstag", 210, 2, "WhatsApp", 40],
        ["2026-W15", "2026-04-07", "Dienstag", 210, 3, "Safari", 35],
        ["2026-W15", "2026-04-07", "Dienstag", 210, 4, "Moodle", 28],
        ["2026-W15", "2026-04-07", "Dienstag", 210, 5, "Spotify", 20],
        ["2026-W15", "2026-04-09", "Donnerstag", 245, 1, "YouTube", 62],
        ["2026-W15", "2026-04-09", "Donnerstag", 245, 2, "WhatsApp", 45],
        ["2026-W15", "2026-04-09", "Donnerstag", 245, 3, "Safari", 40],
        ["2026-W15", "2026-04-09", "Donnerstag", 245, 4, "Moodle", 30],
        ["2026-W15", "2026-04-09", "Donnerstag", 245, 5, "Spotify", 24],
        ["2026-W15", "2026-04-11", "Samstag", 225, 1, "YouTube", 68],
        ["2026-W15", "2026-04-11", "Samstag", 225, 2, "WhatsApp", 43],
        ["2026-W15", "2026-04-11", "Samstag", 225, 3, "Safari", 37],
        ["2026-W15", "2026-04-11", "Samstag", 225, 4, "Moodle", 31],
        ["2026-W15", "2026-04-11", "Samstag", 225, 5, "Spotify", 19],
    ]
    return pd.DataFrame(rows, columns=INPUT_COLUMNS)

"""
Argumente:
    minutes (float):
        Zeit in Minuten

Rückgabe:
    str:
        Formatierte Zeit als "X h YY min"
        -> mit divmod (*Anzahl der Minuten, 60) (durch 60 geteilt werden)
"""

def format_minutes(minutes: float) -> str:
    total_minutes = int(round(minutes))
    hours, mins = divmod(total_minutes, 60)
    return f"{hours} h {mins:02d} min"

"""
Argumente:
    frame (pd.DataFrame):
        Eingelesene CSV-Daten
    source_name (str):
        Name der Datei

Rückgabe:
    list[str]:
        Liste von Fehler- oder Warnmeldungen
"""

def validate_frame(frame: pd.DataFrame, source_name: str) -> list[str]:
    issues: list[str] = []
    missing = [column for column in INPUT_COLUMNS if column not in frame.columns]
    if missing:
        return [f"{source_name}: Fehlende Spalten: {', '.join(missing)}"]

    unique_days = frame["day_date"].nunique()
    if unique_days < 3:
        issues.append(
            f"{source_name}: Es wurden nur {unique_days} Tage gefunden. Erwartet sind mindestens 3."
        )

    rank_count = frame["app_rank"].nunique()
    if rank_count > 5:
        issues.append(
            f"{source_name}: Mehr als 5 App-Raenge gefunden. Erwartet sind die Top-5 Apps."
        )

    return issues


def has_required_columns(frame: pd.DataFrame) -> bool:
    return set(INPUT_COLUMNS).issubset(frame.columns)

"""
Argumente:
    frame (pd.DataFrame):
        Rohdaten

Rückgabe:
    pd.DataFrame:
        Daten mit berechneten Spalten:
        - weekly_app_minutes
        - weekly_total_minutes
"""

def add_calculated_columns(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["day_date"] = pd.to_datetime(data["day_date"], errors="coerce")
    data["daily_total_minutes"] = pd.to_numeric(data["daily_total_minutes"], errors="coerce")
    data["daily_app_minutes"] = pd.to_numeric(data["daily_app_minutes"], errors="coerce")
    data["week_start"] = data["day_date"] - pd.to_timedelta(data["day_date"].dt.weekday, unit="D")

    weekly_totals = (
        data.drop_duplicates(subset=["week_label", "week_start", "day_date"])
        .groupby(["week_label", "week_start"])["daily_total_minutes"]
        .sum(min_count=1)
        .rename("weekly_total_minutes")
        .reset_index()
    )
    weekly_app_totals = (
        data.groupby(["week_label", "week_start", "app_name"])["daily_app_minutes"]
        .sum(min_count=1)
        .rename("weekly_app_minutes")
        .reset_index()
    )

    data = data.drop(columns=CALCULATED_COLUMNS, errors="ignore")
    data = data.merge(weekly_totals, on=["week_label", "week_start"], how="left")
    data = data.merge(weekly_app_totals, on=["week_label", "week_start", "app_name"], how="left")
    return data.drop(columns=["week_start"])

"""
Argumente:
    frames (list[pd.DataFrame]):
        Liste von DataFrames

Rückgabe:
    pd.DataFrame:
        Zusammengeführte und bereinigte Daten
"""

def parse_data(frames: list[pd.DataFrame]) -> pd.DataFrame:
    data = pd.concat([add_calculated_columns(frame) for frame in frames], ignore_index=True)
    data["day_date"] = pd.to_datetime(data["day_date"], errors="coerce")
    data["week_start"] = data["day_date"] - pd.to_timedelta(data["day_date"].dt.weekday, unit="D")
    for column in [
        "daily_total_minutes",
        "app_rank",
        "daily_app_minutes",
        "weekly_app_minutes",
        "weekly_total_minutes",
    ]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    return data

"""
Argumente:
    data_dir (Path):
        Ordner mit CSV-Dateien
    uploaded_files:
        Vom Nutzer hochgeladene Dateien

Rückgabe:
    tuple:
        - pd.DataFrame (Daten)
        - list[str] (Warnungen)
        - list[str] (geladene Dateien)
        - list[str] (Fehler)
"""

def read_weekly_csvs(
    data_dir: Path, uploaded_files
) -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    csv_files = sorted(data_dir.glob("*.csv")) if data_dir.exists() else []
    uploaded_files = uploaded_files or []
    if not csv_files and not uploaded_files:
        return pd.DataFrame(), [], [], []

    errors: list[str] = []
    frames: list[pd.DataFrame] = []
    warnings: list[str] = []
    loaded_files: list[str] = []

    for csv_file in csv_files:
        try:
            frame = pd.read_csv(csv_file)
        except Exception as exc:
            errors.append(f"{csv_file.name}: Konnte nicht gelesen werden ({exc}).")
            continue
        issues = validate_frame(frame, csv_file.name)
        if not has_required_columns(frame):
            errors.extend(issues)
            continue
        warnings.extend(issues)
        frame["source_file"] = csv_file.name
        frames.append(frame)
        loaded_files.append(f"{csv_file.name} (Ordner)")

    for uploaded_file in uploaded_files:
        try:
            frame = pd.read_csv(uploaded_file)
        except Exception as exc:
            errors.append(f"{uploaded_file.name}: Konnte nicht gelesen werden ({exc}).")
            continue
        issues = validate_frame(frame, uploaded_file.name)
        if not has_required_columns(frame):
            errors.extend(issues)
            continue
        warnings.extend(issues)
        frame["source_file"] = uploaded_file.name
        frames.append(frame)
        loaded_files.append(f"{uploaded_file.name} (Upload)")

    if not frames:
        return pd.DataFrame(), warnings, loaded_files, errors

    data = parse_data(frames)
    return data, warnings, loaded_files, errors


def build_week_selector_options(data: pd.DataFrame) -> list[str]:
    week_index = (
        data.loc[:, ["week_start", "week_label"]]
        .drop_duplicates()
        .sort_values("week_start")
    )
    return week_index["week_label"].tolist()


def filter_by_week_labels(data: pd.DataFrame, week_labels: list[str]) -> pd.DataFrame:
    return data[data["week_label"].isin(week_labels)]


def build_weekly_totals(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby(["week_start", "week_label"], as_index=False)["weekly_total_minutes"]
        .max()
        .sort_values("week_start")
        .rename(columns={"weekly_total_minutes": "minutes"})
    )


def build_daily_totals(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.drop_duplicates(subset=["week_start", "day_date"])
        .loc[:, ["week_start", "week_label", "day_date", "day_name", "daily_total_minutes"]]
        .sort_values(["week_start", "day_date"])
        .rename(columns={"daily_total_minutes": "minutes"})
    )


def build_weekly_app_totals(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby(["week_start", "week_label", "app_name"], as_index=False)["weekly_app_minutes"]
        .max()
        .sort_values(["week_start", "weekly_app_minutes"], ascending=[True, False])
    )


def build_stats_table(weekly_totals: pd.DataFrame) -> pd.DataFrame:
    stats = {
        "Kennzahl": [
            "Anzahl erfasster Wochen",
            "Durchschnitt pro Woche",
            "Median pro Woche",
            "Maximum pro Woche",
            "Minimum pro Woche",
        ],
        "Wert": [
            str(len(weekly_totals)),
            format_minutes(weekly_totals["minutes"].mean()),
            format_minutes(weekly_totals["minutes"].median()),
            format_minutes(weekly_totals["minutes"].max()),
            format_minutes(weekly_totals["minutes"].min()),
        ],
    }
    return pd.DataFrame(stats)


def render_empty_state() -> pd.DataFrame:
    template_frame = build_template_frame()
    st.warning(
        "Noch keine CSV-Dateien geladen. Die App zeigt deshalb zunaechst die eingebauten Beispieldaten an."
    )
    st.subheader("So erstellen Sie Ihre eigenen CSV-Dateien")
    st.markdown(
        """
1. Erstellen Sie pro Woche eine eigene CSV-Datei.
2. Erfassen Sie mindestens drei verschiedene Tage dieser Woche.
3. Schreiben Sie pro Tag genau fuenf Zeilen, eine pro Top-App.
4. Verwenden Sie Minuten als Zahlen ohne Einheiten.
5. `weekly_app_minutes` und `weekly_total_minutes` werden automatisch berechnet.
        """
    )
    st.subheader("Tabellenvorlage")
    st.dataframe(template_frame, hide_index=True, use_container_width=True)
    st.download_button(
        "CSV-Vorlage herunterladen",
        data=template_frame.to_csv(index=False).encode("utf-8"),
        file_name="TimeCounterTemplate.csv",
        mime="text/csv",
    )
    return parse_data([template_frame])


def build_weekly_share_chart_data(weekly_app_totals: pd.DataFrame) -> pd.DataFrame:
    chart_data = weekly_app_totals.loc[:, ["app_name", "weekly_app_minutes"]].copy()
    chart_data["share_label"] = chart_data["weekly_app_minutes"].map(format_minutes)
    return chart_data

"""
Argumente:
    weekly_app_totals (pd.DataFrame):
        Wöchentliche App-Nutzung

Rückgabe:
    None:
        Zeigt ein Kreisdiagramm in Streamlit
"""

def render_weekly_share_chart(weekly_app_totals: pd.DataFrame) -> None:
    chart_data = build_weekly_share_chart_data(weekly_app_totals)
    share_chart = (
        alt.Chart(chart_data)
        .mark_arc(innerRadius=45)
        .encode(
            theta=alt.Theta("weekly_app_minutes:Q", title="Minuten"),
            color=alt.Color("app_name:N", title="App"),
            tooltip=[
                alt.Tooltip("app_name:N", title="App"),
                alt.Tooltip("weekly_app_minutes:Q", title="Minuten"),
                alt.Tooltip("share_label:N", title="Anzeige"),
            ],
        )
    )
    st.altair_chart(share_chart, use_container_width=True)

"""
Argumente:
    daily_totals (pd.DataFrame):
        Tagesdaten

Rückgabe:
    None:
        Zeigt ein Balkendiagramm in Streamlit
"""

def render_daily_totals_chart(daily_totals: pd.DataFrame) -> None:
    chart_data = daily_totals.copy()
    chart_data["day_label"] = chart_data["day_date"].dt.strftime("%d.%m.%Y")
    daily_chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("day_label:N", title="Tag", sort=chart_data["day_label"].tolist()),
            y=alt.Y("minutes:Q", title="Bildschirmzeit pro Tag"),
            tooltip=[
                alt.Tooltip("day_label:N", title="Datum"),
                alt.Tooltip("minutes:Q", title="Minuten"),
            ],
        )
    )
    st.altair_chart(daily_chart, use_container_width=True)


st.set_page_config(
    page_title="Bildschirmzeit im Semester",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Bildschirmzeit im Semester")
st.caption("Kevin Alessander - DS")
st.caption(
    "Visualisierung der woechentlichen Bildschirmzeit inklusive Tageswerten und Top-5-Apps."
)

with st.sidebar:
    st.header("Datenquelle")
    uploaded_files = st.file_uploader(
        "CSV-Dateien hochladen",
        type="csv",
        accept_multiple_files=True,
        help="Sie koennen eine oder mehrere Wochen-Dateien direkt hochladen.",
    )

data, warnings, loaded_files, errors = read_weekly_csvs(DATA_DIR, uploaded_files)

for error in errors:
    st.error(error)

if data.empty:
    data = render_empty_state()
    loaded_files = ["Eingebautes Beispiel aus TimeCounterApp.py"]

for warning in warnings:
    st.warning(warning)

data = data.dropna(subset=["day_date", "week_start"])
if data.empty:
    st.error("Die geladenen Dateien enthalten keine gueltigen Datumswerte fuer 'day_date'.")
    render_empty_state()
    st.stop()

available_week_labels = build_week_selector_options(data)

with st.sidebar:
    st.header("Steuerung")
    selected_week_labels = st.multiselect(
        "Wochen anzeigen",
        options=available_week_labels,
        default=available_week_labels,
        help="Waehlen Sie die Wochen aus, die in allen Diagrammen angezeigt werden sollen.",
    )
    available_apps = sorted(data["app_name"].dropna().unique().tolist())
    selected_apps = st.multiselect(
        "Apps fuer den Verlauf",
        options=available_apps,
        default=available_apps,
    )
    st.markdown("**Geladene Dateien**")
    for file_name in loaded_files:
        st.write(file_name)
    st.caption("Sie koennen Dateien hochladen oder dauerhaft in 'TimeCounterData/' speichern.")

if not selected_week_labels:
    st.info("Waehlen Sie in der Sidebar mindestens eine Woche aus.")
    st.stop()

filtered_data = filter_by_week_labels(data, selected_week_labels)

if filtered_data.empty:
    st.info("Fuer die ausgewaehlten Wochen sind keine Daten vorhanden.")
    st.stop()

weekly_totals = build_weekly_totals(filtered_data)
daily_totals = build_daily_totals(filtered_data)
weekly_app_totals = build_weekly_app_totals(filtered_data)
stats_table = build_stats_table(weekly_totals)

metric_columns = st.columns(4)
metric_columns[0].metric("Wochen gesamt", str(len(weekly_totals)))
metric_columns[1].metric("Durchschnitt / Woche", format_minutes(weekly_totals["minutes"].mean()))
metric_columns[2].metric("Maximale Woche", format_minutes(weekly_totals["minutes"].max()))
metric_columns[3].metric("Durchschnitt / Tag", format_minutes(daily_totals["minutes"].mean()))

left_col, right_col = st.columns([1.7, 1])

with left_col:
    st.subheader("Zeitlicher Verlauf gesamt")
    st.line_chart(
        weekly_totals.set_index("week_start")
        .loc[:, ["minutes"]]
        .rename(columns={"minutes": "Bildschirmzeit pro Woche"})
    )

with right_col:
    st.subheader("Statistische Kennzahlen")
    st.dataframe(stats_table, hide_index=True, use_container_width=True)

st.subheader("Verlauf nach App")
if selected_apps:
    st.line_chart(
        weekly_app_totals[weekly_app_totals["app_name"].isin(selected_apps)]
        .pivot(index="week_start", columns="app_name", values="weekly_app_minutes")
        .sort_index()
    )
else:
    st.info("Waehlen Sie in der Sidebar mindestens eine App aus.")

week_options = weekly_totals.sort_values("week_start")["week_label"].tolist()
selected_week_label = st.selectbox(
    "Detailansicht fuer eine Woche",
    options=week_options,
    index=len(week_options) - 1,
)

selected_week_data = filtered_data[filtered_data["week_label"] == selected_week_label]
selected_week_daily = build_daily_totals(selected_week_data)
selected_week_apps = build_weekly_app_totals(selected_week_data)
detail_col_1, detail_col_2 = st.columns(2)

with detail_col_1:
    st.subheader("Tageswerte der ausgewaehlten Woche")
    render_daily_totals_chart(selected_week_daily)

with detail_col_2:
    st.subheader("Top-5-Apps der ausgewaehlten Woche")
    render_weekly_share_chart(selected_week_apps)
    st.dataframe(
        selected_week_apps.loc[:, ["app_name", "weekly_app_minutes"]].rename(
            columns={
                "app_name": "App",
                "weekly_app_minutes": "Minuten in der Woche",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

st.subheader("Rohdaten")
st.dataframe(
    filtered_data.drop(columns=["week_start"], errors="ignore").sort_values(["day_date", "app_rank"]),
    hide_index=True,
    use_container_width=True,
)
