VISUALISIERUNG DER SCHWEIZER STROMHERKUNFT

Stand: 30.08.2022 10:00
Yanis Schärer
yanis.schaerer@swissnuclear.ch
Windows Passwort bei W. Denk

Inhaltsverzeichnis:
-------------------
- Kurzbeschreibung
- Einrichten und Ausführen
- Wichtige Infos
- Struktur
- Troubleshooting

Kurzbeschreibung:
-----------------
Mit mehreren Python Scripts werden die aktuellen Stromproduktionsdaten von der  Entso-E Transparency Platform
heruntergeladen und gefiltert. Die verleibenden Daten werden als Grafiken und als CSV-Dateien neu abgespeichert,
mit dem Ziel, diese öffentlich zugänglich zu machen. Das Projekt befindet sich unter
H:\KKW Unterstützung\Kernanlagen (CH)\Produktionsdaten Entso-E CH. Weitere Informationen: res/Praesentation.pptx.
WICHTIG: Sollte sich der Speicherort des Projekts ändern, muss die Variable DEST in scheduler.bat ebenfalls zum
neuen Speicherpfad geändert werden.
ACHTUNG: Nicht doppelklicken auf scheduler.bat, sondern rechte Maustaste "Weitere Optionen" und "Bearbeiten"


Einrichten und Ausführen:
-------------------------
WICHTIG: Um Probleme zu vermeiden, sollte die automatisierte Aktualisierung nur auf einem lokalen Rechner
eingerichtet sein. Wenn zwei Rechner benötigt sind (z.B. wenn einer als Backup dient), dass muss beachtet
werden, dass der Zeitunterschied zwischen den Aufgaben in der Aufgabenplanung mindestens eine Stunde betragen.
Die Zeit kann manuell in res/Aktualisierung Produktionsdaten Entso-E unter <StartBoundary> angepasst werden.

Ein Windows-Computer mit der Anaconda Python-Distribution (https://www.anaconda.com/products/distribution) wird
benötigt. Die Mindestanforderung ist Python 3.10.4. Alle Abhängigkeiten sind in res/environment.yml angegeben.

Folgende Schritte müssen durchgeführt werden:
1. Sicherstellen, dass die automatisierte Ausführung auf keinem anderen Rechner läuft, sonst kann es zu Problemen
kommen. Falls ein zweiter Rechner notwendig ist (z.B. als Backup), dann Schritt 1*. ausführen, sonst überspringen.
1*. res/Aktualisierung Produktionsdaten Entso-E öffnen und die Uhrzeit bei <StartBoundary> auf mindestens eine
Stunde später stellen.
2. Ordner H:\KKW Unterstützung\Kernanlagen (CH)\Produktionsdaten Entso-E CH auf den lokalen Speicher kopieren.
Den neu lokal gespeicherten Ordner "Produktionsdaten Entso-E CH" zu einem beliebigen Namen OHNE Leerzeichen
umbenennen.
WICHTIG: Im ganzen Pfad zum neuen Ordner darf KEIN Leerzeichen vorkommen.
3. Conda Prompt (Conda Eingabeaufforderung öffnen).
4. Diesen Befehl eingeben: cd path/to/res (Der Pfad zur Datei environment.yml im Ordner res)
5. Diesen Befehl eingeben: conda env create --file=environment.yml
6. Conda Prompt schliessen.
7. Aufgabenplanung öffnen.
8. Aktion -> Aufgabe importieren... -> res/Aktualisierung Produktionsdaten Entso-E.xml öffnen -> "Aufgabe erstellen"
öffnet sich -> Aktionen -> Bearbeiten... öffnen
9. Durchsuchen... und scheduler.bat auswählen, den Pfad unter Programm/Skript OHNE \scheduler.bat und OHNE
Gänsefüsschen kopieren und bei "Starten in (optional)" einfügen. OK und wieder OK drücken.

Die Aktualisierung der Daten und Grafiken ist nun automatisiert.

Wird gewünscht, dass nach jeder Aktualisierung die deutsche Grafik der letzten 30 Tage angezeigt wird, müssen die
Doppelpunkte in den beiden Zeilen unter "REM Open created images" entfernt werden.


Wichtige Informationen:
-----------------------
WICHTIG: Da die Solar-Daten erst um 10 Uhr für den letzten Tag aktualisiert werden, sollte der Windows Aufgabenplaner
die Scripts erst nach diesem Zeitpunkt starten (falls die Aufgabe importiert wurde (ohne Schritt 1*.), findet die
Aktualisierung täglich um 11 Uhr statt).

Die Daten für "Wasserkraft & Andere" werden berechnet und nicht direkt von der Datenquelle genommen, da kleine 
Kraftwerke nicht verpflichtet sind, ihre Produktionsdaten an Entso-E zu melden. Die Formel zur Berechnung lautet:
Wasserkraft & Andere = Last + Export - Nuklear - Solar - Import

SFTP-Server Details:
host = sftp-transparency.entsoe.eu
port = 22
user = techmon@swissnuclear.ch
pw = Z3*Ht~#+5oXqrfkG-sn_
Mehr Infos: https://transparency.entsoe.eu/content/static_content/
		Static%20content/knowledge%20base/SFTP-Transparency_Docs.html#welcome

Struktur:
---------
- README.txt: Anleitung und Informationen.
- log.txt: Jede Ausführung des Programms wird in dieser Datei erfasst und die Details sind ersichtlich.
- scheduler.bat: Die Batch-Datei, welche von der Windows Aufgabenplanung täglich ausgeführt wird. Mit einem
		     Doppelklick kann die Ausführung manuell gestartet werden. Dabei ist der Output der Scripts
		     ersichtlich, was hilfreich sein kann, wenn etwas nicht wunschgemäss funktioniert.
- core:
	- import_data_entsoe.py: Mit diesem Script werden die Daten von Entso-E heruntergeladen, gefiltert und neu
					 abgespeichert. Dieser Code greift auf dep/FileHandlerLib.py zu. Falls sich die
					 Details des SFTP-Servers ändern, müssen diese in dieser Datei geändert werden.
					 Dieses Script erkennt, wenn Daten der letzten Tage, Wochen oder Monate fehlen und 
					 lädt diese neben den aktuellsten Daten ebenfalls herunter.
	- generate_files.py: Dieses Script erstellt die Grafiken und die Datendateien. Greift auf dep/FileMaker.py zu.
				   Hier werden Schriftarten, Farben, Ordnerstruktur und Weiteres definiert. Die erstellten
				   Dateien werden im Ordner Export abgelegt. Das "heutige" Datum kann frei gewählt werden.
				   Fehlende Dateien und Grafiken müssen manuell erstellt werden, indem das Datum geändert wird.
				   Dabei muss aber beachtet werden, dass am Schluss das Datum wieder auf das aktuelle
				   zurückgesetzt wird und der scheduler.bat noch einmal gestartet wird. Ausserdem zu beachten
				   bei der manuellen Datumswahl: Die Übersichten werden immer am 6. des Folgemonats erstellt.
	- generation: In diesen Ordner werden die gefilterten Daten im CSV-Format abgelegt. Jede Datei steht für
			  einen Monat.
	- outages: Hier werden die geplannten und erzwungenen Abschaltungen, ebenfalls im CSV-Format, abgelegt. Eine
		     Datei enthält die Abschaltungen über ein ganzes Jahr.
	- .downloads: Die durch import_data_entsoe.py vom SFTP-Server heruntergeladenen Daten werden temporär in diesem
			  Ordner gespeichert, beim Abschluss des Scripts aber wieder gelöscht. Wenn das Programm inaktiv
			  ist, ist dieser Ordner in jedem Fall leer.
- dep:
	- __pycache__ und __init__.py: Werden benötigt, um die anderen Dateien im Ordner für die Kernprogramme abrufbar
						 zu machen. Hier sollte unter keinen Umständen etwas geändert werden.
	- to_log.py: Enthält eine Funktion, welche das Schreiben von standardisierten Einträgen in log.txt erlaubt.
	- FileHandlerLib.py: Enthält eine abstrakte Base-Class und mehrere Derived-Classes für das Handling der
				   von Entso-E heruntergeladenen Daten. Welche Daten gefiltert und welche behalten werden,
				   wird in diesem Code definiert.
	- FileMaker.py: Enthält eine Class, welche Funktionen enthält, um alle Grafiken und die Datendatei zu erstellen.
			    Gewünschte Änderungen an den Grafiken (ausgenommen Farbpalette, Schriftart,
			    Standardschriftgrösse) müssen in diesem Code definiert werden. Greift auf
			    dep/TextRepositories.py zu.
	- TextRepositories.py: Enthält pro Sprache eine Class mit allen Textfeldern. Um eine neue Sprache hinzuzufügen,
				     muss eine neue Class erstellt werden. Die neue Class muss alle Variablen enthalten,
				     welche auch in der deutschen, französischen und italienischen Class vorhanden sind.
- misc: Enthält Codes, welche nicht mehr verwendet werden, möglicherweise aber noch von Nutzen sein könnten.
- res: Enthält alles statischen Elemente, wie z.B. das swissnuclear Logo oder eine Präsentation über dieses Projekt.
- Export: Wird automatisch beim Ausführen von generate_files.py erstellt, wenn nicht schon vorhanden. Enthält alle
	    erstellten Grafiken und CSV-Dateien.


Troubleshooting:
----------------
Mögliche Szenarien, wenn das Programm nicht den gewünschten Output erstellt.
- Kein Eintrag in log.txt für den aktuellen und möglicherweise vergangene Tage:
	- Überprüfen, ob der Rechner eingeschaltet ist.
	- Überprüfen, ob die Windows Aufgabenplanung ordnungsgemäss funktioniert.
	- Möglicherweise hat sich das Programm aufgehängt: Aufgabenplanung öffnen -> Reiter Aktion -> Alle aktiven
	  Aufgaben -> Die entsprechende Aufgabe beenden.
- Nur "Started xxx.py..." aber kein entsprechendes "Finished xxx.py" in log.txt:
	- Die Batch-Datei scheduler.bat mit einem Doppelklick manuell starten und den Output beobachten. Falls alles
	  rund läuft sind keine weiteren Massnahmen nötig. Es kommt selten vor, dass das Programm abstürzt.
- Die Grafiken sehen nicht normal aus:
	Viele mögliche Ursachen. Einige Vorschläge:
	- Die entsprechende CSV-Datei, welche zusammen mit den Grafiken erstellt wurde, untersuchen.
	- Änderung der Struktur auf dem SFTP-Server von Entso-E. WinSCP oder ähnliche nutzen, um die Struktur auf dem
	  SFTP-Server manuell zu überprüfen.
	- Änderung der SFTP-Server Details. Mehr Infos unter https://transparency.entsoe.eu/content/static_content/
	  Static%20content/knowledge%20base/SFTP-Transparency_Docs.html#welcome.
- Die Grafiken sind auf H:\ nicht verfügbar, auf C:\ (lokal) dagegen schon:
	- Sehr wahrscheinlich funktioniert etwas mit dem Befehl robocopy in scheduler.bat nicht. Überprüfen, ob die
	  Variable DEST noch aktuell ist.
	- "> nul" hinter den robocopy-Befehlen entfernen und scheduler.bat manuell aktivieren. Output überprüfen.




