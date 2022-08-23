VISUALISIERUNG DER SCHWEIZER NETTOSTROMPRODUKTION

Stand: 23.08.2022 12:00
Yanis Schärer
yanis.schaerer@swissnuclear.ch

Kurzbeschreibung: Mit mehreren Python Scripts werden die aktuellen Stromproduktionsdaten von der Transparency
			Platform von Entso-E heruntergeladen und gefiltert. Die verleibenden Daten werden als Grafiken
			und als CSV-Dateien neu abgespeichert, mit dem Ziel, diese öffentlich zugänglich zu machen.
			Weitere Informationen: res/Praesentation.pptx

Zum Ausführen benötigt:
Ein Windows-Computer mit Python 3.10.4. Ältere Versionen von Python werden nicht unterstützt und bei neueren
Versionen kann nicht garantiert werden, dass die Funktionalität erhalten bleibt. Folgende Packages müssen installiert
sein (optimalerweise in einem separaten Conda Environment, alle heruntergeladen mit Pip):
numpy 1.23.2
pandas 1.4.3
matplotlib 3.5.3
pysftp 0.2.9
tqdm 4.64.0

Das Projekt befindet sich unter H:\KKW Unterstützung\Kernanlagen (CH)\Produktionsdaten Entso-E CH.
Die Struktur ist folgendermassen:
- README.txt: Diese Datei.
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

SFTP-Server Details:
host = sftp-transparency.entsoe.eu
port = 22
user = ------------------------ HIER EINFÜGEN ---------------------------------
pw = ------------------------ HIER EINFÜGEN ---------------------------------
Mehr Infos: https://transparency.entsoe.eu/content/static_content/
		Static%20content/knowledge%20base/SFTP-Transparency_Docs.html#welcome

Troubleshooting:
Mögliche Szenarien, wenn das Programm nicht den gewünschten Output erstellt.
- Kein Eintrag in log.txt für den aktuellen und möglicherweise vergangene Tage:
	- Überprüfen, ob der Rechner eingeschaltet ist.
	- Überprüfen, ob die Windows Aufgabenplanung ordnungsgemäss funktioniert.
	- Möglicherweise hat sich das Programm aufgehängt: Aufgabenplanung öffnen -> Reiter Aktion -> Alle aktiven
	  Aufgaben -> Die entsprechende Aufgabe beenden.
- Nur "Started xxx.py..." aber kein entsprechendes "Finished xxx.py" in log.txt:
	- Die Batch-Datei scheduler.bat mit einem Doppelklick manuell starten und den Output beobachten. Falls alles
	  rund läuft sind keine weiteren Massnahmen nötig. Es kommt selten vor, dass etwas nicht so läuft wie es sollte.
- Die Grafiken sehen nicht normal aus:
	Viele mögliche Ursachen. Einige Vorschläge:
	- Die entsprechende CSV-Datei, welche zusammen mit den Grafiken erstellt wurde, untersuchen.
	- Änderung der Struktur auf dem SFTP-Server von Entso-E. WinSCP oder ähnliche nutzen, um die Struktur auf dem
	  SFTP-Server manuell zu überprüfen.
	- Änderung der SFTP-Server Details. Mehr Infos unter https://transparency.entsoe.eu/content/static_content/
	  Static%20content/knowledge%20base/SFTP-Transparency_Docs.html#welcome.




