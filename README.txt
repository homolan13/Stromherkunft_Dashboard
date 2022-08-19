Stand: 18.08.2022 15:20

Um monatlich und jährlich sowie für die letzten 30 Tage täglich eine Grafik zur Visualisierung der
Produktionsdaten der Schweizer KKW zu erstellen, braucht es die beiden Dateien download_extract_save_remove.py
und visualization.py. Alle Dateien befinden sich unter H:\Kommunikation & Politik\Produktionsdaten KKW CH.

download_extract_save_remove.py lädt die Daten von dem SFTP-Server von Entso-E herunter. Geplant ist, dass die
Daten automatisiert jeweils täglich heruntergeladen werden. Das Programm ist aber fähig, unter bestimmten
Umständen fehlende Daten zu erkennen und nachzutragen. Gelegentlich kommt es zu einer Fehlermeldung beim
Herstellen einer Verbindung mit dem SFTP-Server. Dann muss das Program jedoch nur noch einmal laufen gelassen
werden. Beim Automatisieren muss diesem Umstand Rechnung getragen werden.

visualization.py erstellt Grafiken. Täglich wird eine neue Grafik erstellt, welche die Stromproduktion der
letzten 30 Tage zeigt (mit 2 Tagen Verzögerung), und die Grafik vom Vortag wird entfernt. Da die
Kraftwerkspezifischen Produktionsdaten erst mit einer fünftägigen Verzögerung verfügbar sind, wird in dieser
Zeit keine Aufsplittung der Kernenergie in individuelle KKW vorgenommen. Jeweils am 6. des Monats wird eine
Übersicht für den Vormonat erstellt. Jeweils am 6. des Januars wird zusätzlich noch die Übersicht für das
Vorjahr erstellt. Wahlweise können geplannte und erzwungen Abschaltungen in der Monats- und Jahresübersicht
inkludiert werden. Das muss in Zeile 8 des Skripts definiert werden.

In scheduler.bat sind beide Programme zusammengefasst und können mit einem Doppelklick auf die Batch-Datei
gestartet werden. Das ist aber nur nötig, wenn das Programm manuell gestartet werden soll. Dann öffnet sich ein
Fenster, auf welchem der Output der Programme ausgegeben wird. Bei der automatisierten Ausführung öffnet sich
kein Fenster.

ZU BEACHTEN:
In download_extract_save_remove.py und visualization.py gibt es in der main-Funktion die Möglichkeit, statt dem
heutigen Datum ein Wunschdatum einzugeben.
Falls die automatisierte tägliche Aktualisierung aus irgendwelchen Gründen ausfällt, dann müssen folgende
Schritte ausgeführt werden:
1. Löschen der aktuellsten Datei im Ordner Generation (z.B. generation\2022\2022_07_generation.csv, falls es
keine Datei gibt, dessen Datum näher am heutigen Tag liegt)
2. Wenn einige Grafiken (monatliche und/oder jährliche Ansichten) fehlen, dann muss in der main-Funktion von
visualization.py folgendes Datum eingegeben werden: today = datetime(Jahr, Monat, 6), wobei Jahr und Monat
des FOLGEMONATS (!) gewählt werden müssen. Beispiel: 2021_12_overview.png fehlt -> datetime(2022, 1, 6). Zu
beachten: Grafiken werden immer am 6. des Folgemonats erstellt.
3. Doppelklick auf scheduler.bat und warten bis sich das geöffnete Fenster wieder schliesst. Dies kann einige
Minuten dauern. Schritte 2 und 3 mit angepassten Daten wiederholen, bis alle fehlenden Grafiken erstellt wurden.
4. Das Datum in visualization.py muss wieder auf today = datetime.today() - timedelta(days=2) gestellt werden.

TODO:
- Automatisierung, um die Schritte täglich auszuführen.
- Ändern der Login-Daten für den SFTP-Server.

