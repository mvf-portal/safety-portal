#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/safety.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "safety-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Gemessen am 25.08.2026 mit machbarkeit.py: 11.878 Arbeiten in zwoelf Monaten
# (32,5 pro Tag), 1.490 mit Europabezug, 555 mit Deutschlandbezug. Ueberschneidung
# mit den zehn Schwesterhubs hoechstens 9,3 Prozent - KI 2,5, Pflege 2,4,
# Versorgungsforschung 1,7. OHNE den NOT-Block waeren es 12.898 Arbeiten und
# 16,8 Prozent: Der Block kostet acht Prozent Material und halbiert die
# Ueberschneidung. Wer hier etwas aendert, misst danach neu:
#     py machbarkeit.py kandidaten/patientensicherheit.json --ohne-not --titel
_THEMA = (
    '(("Patient Safety"[Majr] OR "Medical Errors"[Majr] OR "Medication Errors"[Majr] '
    'OR "Diagnostic Errors"[Majr] OR "Malpractice"[Majr] OR "Patient Harm"[Majr] '
    'OR "Iatrogenic Disease"[Majr] OR "Safety Management"[Majr] OR "Risk Management"[Majr] '
    'OR "Medical Order Entry Systems"[Majr] '
    'OR "Drug-Related Side Effects and Adverse Reactions"[Majr] OR "patient safety"[Title] '
    'OR "medical error*"[Title] OR "medication error*"[Title] '
    'OR "diagnostic error*"[Title] OR "adverse event*"[Title] OR "never event*"[Title] '
    'OR malpractice[Title] OR "patient harm"[Title] OR "preventable harm"[Title]) '
    'OR ("Cross Infection"[Majr] OR "Infection Control"[Majr] OR "Hand Hygiene"[Majr] '
    'OR "Catheter-Related Infections"[Majr] OR "Surgical Wound Infection"[Majr] '
    'OR "Antimicrobial Stewardship"[Majr] OR nosocomial[Title] '
    'OR "hospital-acquired"[Title] OR "healthcare-associated"[Title] '
    'OR "infection control"[Title] OR "hand hygiene"[Title] '
    'OR "antimicrobial stewardship"[Title]) OR ("Sepsis"[Majr] OR "Shock, Septic"[Majr] '
    'OR "Systemic Inflammatory Response Syndrome"[Majr] OR sepsis[Title] OR septic[Title] '
    'OR septicemia[Title]) NOT ("Artificial Intelligence"[Majr] '
    'OR "Machine Learning"[Majr] OR "Deep Learning"[Majr] OR "Telemedicine"[Majr] '
    'OR "Nursing"[Majr] OR "Nursing Care"[Majr] OR "Nursing Staff, Hospital"[Majr] '
    'OR "Long-Term Care"[Majr] OR "Nursing Homes"[Majr] OR "Health Literacy"[Majr] '
    'OR "Patient Education as Topic"[Majr] OR "Climate Change"[Majr] '
    'OR "Vaccination"[Majr] OR "Vaccines"[Majr] OR "Aging"[Majr] OR "Longevity"[Majr] '
    'OR "Frailty"[Majr] OR "Noncommunicable Diseases"[Majr] OR "Obesity"[Majr]))'
)
_KONTEXT = (
    '("Delivery of Health Care"[MeSH Terms] OR "Health Services"[MeSH Terms] '
    'OR "Quality of Health Care"[MeSH Terms] OR "Patient Care"[MeSH Terms] '
    'OR "Health Policy"[MeSH Terms] OR "Public Health"[MeSH Terms] '
    'OR "health care"[Title/Abstract] OR "health services"[Title/Abstract] '
    'OR "patient outcome*"[Title/Abstract] OR "clinical practice"[Title/Abstract] '
    'OR implementation[Title/Abstract] OR patients[Title/Abstract])'
)
# "Humans"[MeSH] haelt Tier-, Labor- und reine Modellarbeiten heraus.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}) AND "Humans"[MeSH Terms])',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 30
POOL_ALLGEMEIN = 25
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 1
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
    "Du bist Fachredakteur fuer Patientensicherheit im Gesundheitswesen. "
    "Aus einer Liste von PubMed-Abstracts waehlst du die relevantesten "
    "aktuellen Studien aus und fasst sie praezise auf Deutsch zusammen. "
    "Deine Leserschaft arbeitet im deutschen Gesundheitswesen: Kliniken, "
    "Praxen, Hygiene- und Qualitaetsmanagement, Kostentraeger, "
    "Selbstverwaltung und Gesundheitspolitik. Sie will wissen, was "
    "vermeidbaren Schaden tatsaechlich verhindert - nicht, welcher Erreger "
    "im Labor welche Resistenz zeigte."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) vermeidbaren Schaden in der Versorgung untersuchen - Behandlungs-, Medikations- und Diagnosefehler, nosokomiale Infektionen, Sepsis, oder die Systeme, die beides erkennen und verhindern sollen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
      1. Was Schaden verhindert: eine Massnahme und ihr gemessenes Ergebnis -
         Checklisten, Behandlungsbuendel, Stewardship, Medikationsanalyse,
         veraenderte Ablaeufe, gemessen an Infektionen, Schaeden, Wiederaufnahmen
         oder Sterblichkeit.
      2. Krankenhausinfektionen und Antibiotikaresistenz, sofern eine Massnahme,
         eine Ursache oder eine Folge untersucht wird.
      3. Sepsis als Versorgungsfrage: Erkennungszeit, Behandlungsbuendel,
         Verlegung, Nachsorge und Langzeitfolgen.
      4. Meldesysteme und Sicherheitskultur: Was wird gemeldet, was folgt daraus,
         was aendert sich messbar.
      5. Haftung, Recht und Entschaedigung - der Teil des Feldes, der sich
         zwischen den Laendern am staerksten unterscheidet.
      6. Ungleichheit: Wer traegt das hoehere Schadensrisiko - nach Sprache,
         Herkunft, Alter, Region - und was hilft dagegen.

NICHT in die Auswahl gehoeren:
Grundlagenforschung, mikrobiologische Typisierung und Resistenzmechanismen ohne
Versorgungsbezug, Tiermodelle, Wirksamkeitsstudien einzelner Antibiotika oder
Wirkstoffe ohne Bezug zur Versorgung, Phase-I- und Phase-II-Studien,
Validierungen von Scores, Tests oder Bildgebung ohne Ergebnisbezug, Fallberichte
und Fallserien, reine Erregerstatistiken ohne Bezugsgroesse sowie Uebersichten,
die nichts Eigenes berichten.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
      1. MINDESTENS DREI der sechs Studien muessen aus Europa stammen oder ein
         europaeisches Gesundheitssystem betreffen. Liegen weniger als drei solche
         Arbeiten vor, nimm die verbleibenden Plaetze aus dem Rest - aber schoepfe
         die europaeischen zuerst aus.
      2. HOECHSTENS ZWEI der sechs duerfen Sepsis oder Intensivmedizin betreffen.
         Dieser Teil des Suchraums ist klinisch dominiert und publiziert um ein
         Vielfaches mehr als der Rest; ohne die Grenze bestuende die Ausgabe
         regelmaessig zur Haelfte aus Intensivmedizin, und der Hub laese sich wie
         eine Fachzeitschrift fuer Intensivmediziner.
      3. HOECHSTENS EINE darf eine reine Erreger- oder Resistenzstatistik sein,
         ohne dass eine Massnahme, eine Ursache oder eine Folge untersucht wird.
      4. HOECHSTENS EINE darf eine digitale Anwendung, ein Vorhersagemodell oder
         ein Verfahren des maschinellen Lernens im Mittelpunkt haben. Die Abfrage
         schliesst solche Arbeiten bereits aus, wenn sie dort das Hauptthema sind;
         diese Quote faengt die uebrigen. Sie gehoeren in das Schwesterportal
         ki.m-vf.de.
      5. HOECHSTENS EINE darf ausschliesslich die Pflege betreffen - Personal-
         schluessel, Pflegequalitaet, Heimversorgung. Dafuer gibt es
         pflege.m-vf.de.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Nicht die Wirksamkeit einer Massnahme
entscheidet, was hier ankommt, sondern das Melde- und Haftungsrecht.
Deutschland kennt KEIN Entschaedigungssystem ohne Verschuldensnachweis - Schaden
wird ueber die Arzthaftung geklaert, mit der Beweislastumkehr des Paragrafen
630h BGB als wichtigster Ausnahme. Daenemark, Schweden, Norwegen und Finnland
entschaedigen dagegen ohne Verschuldensnachweis; dort wird gemeldet, was hier
zur Haftungsfrage wuerde, und Meldezahlen aus Skandinavien sind mit deutschen
deshalb NICHT vergleichbar. Massgeblich sind ausserdem die Meldepflichten des
Infektionsschutzgesetzes und die Vermutungswirkung der KRINKO-Empfehlungen, das
einrichtungsinterne Qualitaetsmanagement nach Paragraf 135a SGB V samt
CIRS-Vorgabe, die Trennung von ambulant und stationaer sowie die Zustaendigkeit
der Laender fuer den oeffentlichen Gesundheitsdienst. Ordne die Systeme nach
Vergleichbarkeit: hoch bei DACH, Niederlanden und Frankreich, mittel bei
Skandinavien und Grossbritannien (anderes Melde- und Entschaedigungsrecht),
gering bei den USA (Haftungsklima, andere Finanzierung). Nenne im Feld transfer
bei Melde- und Haftungsstudien AUSDRUECKLICH, wie das Entschaedigungssystem des
Herkunftslandes aussieht.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
      **Er MUSS das Ergebnis nennen, nicht den Fehler oder den Erreger allein.**
      Abstracts sind nach dem Problem betitelt; uebernimmt der Titel das, liest
      sich der Hub wie eine Schadensliste. Der Schaden darf vorkommen, aber er
      darf nicht allein stehen.
      Gut:      "Standardisierte Uebergabe senkte Medikationsfehler auf
                Intensivstationen um ein Drittel"
      Schlecht: "Medikationsfehler auf Intensivstationen: eine
                Beobachtungsstudie" (nennt nur das Problem)
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Beispiele fuer Begriffe, die englisch bleiben: Never Event, Safety Culture,
Antibiotic Stewardship, Bundle, Root Cause Analysis, Trigger Tool, Debriefing.
Uebersetze dagegen, was im Deutschen eine gaengige Entsprechung hat: aus
"near miss" wird der Beinahe-Schaden, aus "adverse event" das unerwuenschte
Ereignis, aus "healthcare-associated infection" die nosokomiale Infektion, aus
"hand hygiene" die Haendehygiene, aus "incident reporting system" das
Fehlermeldesystem, aus "preventable harm" der vermeidbare Schaden.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""


# ------------------------------------------------- Newsfeed
# Wonach dieser Hub im MVF-Archiv sucht (scripts/newsfeed.py). Eigene Liste
# statt der Schnellwahlbegriffe: Chips sind fuer Datenbankabfragen gemacht und
# treffen im deutschen Archiv oft daneben - im Gender-Hub holten "Herzinfarkt"
# und "Arzneimittelsicherheit" allgemeine Herz- und Arzneimittelmeldungen, im
# Mental-Hub brachte "Wartezeit" jeden Arzttermin.
#
# Am 29.08.2026 gegen das Archiv gemessen; einzelne Begriffe stehen trotz
# heute null Treffern drin, weil sie fachlich in der Mitte des Themas liegen
# und das Archiv taeglich waechst. Ein Abruf ohne Treffer kostet nichts.
NEWS_SUCHE = [
    "Patientensicherheit",
    "Behandlungsfehler",
    "Medikationsfehler",
    "Sepsis",
    "nosokomiale Infektion",
    "Fehlermeldesystem",
]
