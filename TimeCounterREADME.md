# TimeCounter Bildschirmzeit-App

Diese Streamlit-App visualisiert die Bildschirmzeit eines Haupt-Smartdevices ueber mehrere Semesterwochen.

## Start

```bash
./.venv/bin/streamlit run TimeCounterApp.py
```

Oder direkt ueber das Startskript:

```bash
./TimeCounterStart.sh
```

Alternativ, falls Ihre virtuelle Umgebung bereits aktiviert ist:

```bash
streamlit run TimeCounterApp.py
```

Falls im ausgewaehlten Interpreter noch Pakete fehlen:

```bash
pip install -r TimeCounterRequirements.txt
```

## CSV-Format

Sie haben zwei Moeglichkeiten:

- CSV-Dateien direkt in der App hochladen
- CSV-Dateien dauerhaft im Ordner `TimeCounterData/` speichern

Legen Sie pro Woche eine CSV-Datei an. Jede Datei sollte mindestens drei verschiedene Tage dieser Woche enthalten.

Pflichtspalten:

- `week_label`: frei waehlbares Label, z. B. `2026-W10`
- `day_date`: Datum des erfassten Tages
- `day_name`: Wochentag
- `daily_total_minutes`: gesamte Bildschirmzeit des Tages in Minuten
- `app_rank`: Rang 1 bis 5
- `app_name`: App-Name oder Pseudonym
- `daily_app_minutes`: Bildschirmzeit der App an diesem Tag in Minuten

Automatisch durch die App berechnet:

- `weekly_app_minutes`: Bildschirmzeit der App in der gesamten Woche in Minuten
- `weekly_total_minutes`: gesamte Bildschirmzeit der Woche in Minuten

Der Wochenstart wird in der App automatisch aus `day_date` berechnet und muss ebenfalls nicht in der CSV stehen.

Wichtig:

- Pro erfasstem Tag gibt es genau 5 Zeilen, eine pro Top-App.
- `app_rank` sollte von 1 bis 5 gehen.
- Die beiden Wochenwerte muessen nicht mehr manuell eingegeben werden.

## Empfehlung fuer Ihre eigenen CSV-Dateien

- Am einfachsten ist Excel, Google Sheets, Numbers oder LibreOffice Calc.
- Erstellen Sie dort die Spalten genau mit den obigen Namen.
- Fuellen Sie pro Woche eine Tabelle aus und exportieren Sie sie als CSV.
- Sinnvolle Dateinamen sind z. B. `TimeCounter_Woche01.csv` oder `TimeCounter_2026-W15.csv`.

Die App zeigt ohne vorhandene Daten automatisch die eingebauten Beispieldaten, eine ausfuellbare Vorlage und einen Download fuer `TimeCounterTemplate.csv` an.

## Enthaltene Visualisierungen

- Verlauf der gesamten Bildschirmzeit pro Woche
- Verlauf einzelner Apps ueber mehrere Wochen
- Detailansicht pro Woche mit Tageswerten, Top-5-Tabelle und Kreisdiagramm zur App-Verteilung
- Kennzahlen wie Mittelwert, Median, Minimum und Maximum
