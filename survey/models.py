# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.forms.widgets import RadioSelect
from django.db.models import Avg
# Create your models here.
CATEGORIES = ['fear','anger','shame','guilt','neutral']
class Question(models.Model):
    
    CATEGORIES_LONG = ['Angst', 'Ärger', 'Scham', 'Schuld', 'Neutral']
    sentence = models.TextField(_("Satz"),null=False, blank=True)
    category = models.CharField(_("Kategorie"),null=False, blank=True, choices=zip(CATEGORIES,CATEGORIES_LONG), max_length=10)
    
    def __unicode__(self):
        return "%s [%s]: %s"%(self.pk,self.category,self.sentence)
    
class Participant(models.Model):
    age = models.PositiveSmallIntegerField(_("Alter"))
    GENDER_CHOICES = (("m", "männlich"),("f", "weiblich"))
    gender = models.CharField(_("Geschlecht"), max_length=1, choices=GENDER_CHOICES)
    education = models.PositiveSmallIntegerField(_("Schuljahre"))
    DEGREE_CHOICES = (
                      (0,"kein Schulabschluss"),
                      (1,"qualifizierender Hauptschulabschluss"),
                      (2,"Realschulabschluss"),
                      (3,"Abitur/Fachabitur"),
#                      (4,"Hochschulabschluss"),
                      )
    degree = models.SmallIntegerField(_('Schulabschluss'),choices=DEGREE_CHOICES)
    
    JOB_CHOICES = (("LehreOhne","Lehre ohne Abschluss"),("LehreMit","Lehre mit Abschluss"), ("FachOhne","Fachoberschule ohne Abschluss"), ("FachMit","Fachoberschule mit Abschluss"), ("StudOhne","Studium ohne Abschluss"),("StudMit", "Studium mit Abschluss (Diplom, Magister, Bachelor)"))
    degree_free = models.CharField(_('Berufsausbildung'), max_length=50, blank=True, choices=JOB_CHOICES)
    
    date_start = models.DateTimeField(auto_now_add=True)
    date_last = models.DateTimeField(auto_now=True)
    
    session = models.CharField(max_length=100, blank=True) 

    def __unicode__(self):
        return "%s [%s,%s]"%(self.pk, self.age, self.gender)
    done = models.BooleanField(_("Fertig?"), default=False)
       
    #def _isDone(self):
    #    return Answer.objects.filter(participant = self, done = True).count() == Question.objects.all().count()
    #isDone = property(_isDone)

class ParticipantForm(ModelForm):
    class Meta:
        model = Participant
	exclude = ('session','done')
        
class Answer(models.Model):
    CHOICES = [0,1,2,3,4]
    CHOICES_LONG = ["1","2","3","4","5"]
    participant = models.ForeignKey(Participant,)
    question = models.ForeignKey(Question,)
    fear = models.SmallIntegerField(_('Angst'),choices=zip(CHOICES,CHOICES_LONG), null=True)
    anger = models.SmallIntegerField(_(u'Ärger'),choices=zip(CHOICES,CHOICES_LONG), null=True)
    shame = models.SmallIntegerField(_('Scham'),choices=zip(CHOICES,CHOICES_LONG), null=True)
    guilt = models.SmallIntegerField(_('Schuld'),choices=zip(CHOICES,CHOICES_LONG), null=True)
    neutral = models.SmallIntegerField(_('Neutral'),choices=zip(CHOICES,CHOICES_LONG), null=True)
    YESNO_CHOICES = ((0,"nein"),(1,"ja"))
    autobiographic = models.SmallIntegerField(_('autobiographisch?'),choices=YESNO_CHOICES, null=True)
    done = models.BooleanField()
    class Meta:
        unique_together = (('question', 'participant'),)
    def __unicode__(self):
        return u"%s[%s,%s]"%(self.done,self.participant,self.question)
    
    def _dfear(self):
      return self.fear-(self.anger+self.shame+self.guilt+self.neutral)
      
    dfear = property(_dfear)
    
    
class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        widgets = {
            'shame': RadioSelect(),
            'fear': RadioSelect(),
            'anger': RadioSelect(),
            'guilt': RadioSelect(),
            'neutral': RadioSelect(),
            'autobiographic': RadioSelect(),
        }

AnswerFormSet = modelformset_factory(Answer, extra=0, form = AnswerForm)

class Result(models.Model):
    question = models.ForeignKey(Question,unique=True)
    count = models.PositiveIntegerField(_("Antworten"),editable=False)
    avg_fear = models.FloatField(_("avg(Angst)"),editable=False)
    avg_anger = models.FloatField(_(u"avg(Ärger)"),editable=False)
    avg_shame = models.FloatField(_("avg(Scham)"),editable=False)
    avg_guilt = models.FloatField(_("avg(Schuld)"),editable=False)
    avg_neutral = models.FloatField(_("avg(Neutral)"),editable=False)
    d_fear = models.FloatField(_("d(Angst)"),editable=False)
    d_anger = models.FloatField(_(u"d(Ärger)"),editable=False)
    d_shame = models.FloatField(_("d(Scham)"),editable=False)
    d_guilt = models.FloatField(_("d(Schuld)"),editable=False)
    d_neutral = models.FloatField(_("d(Neutral)"),editable=False)
    
    
    def __unicode__(self):
        return u"result for %s (%s answers)"%(self.question, self.count)
    
    def save(self, *args, **kwargs):
        answers = Answer.objects.filter(question = self.question, done = True)
        self.count = answers.count()
        aggregate = answers.aggregate(Avg('fear'),Avg('anger'),Avg('shame'),Avg('guilt'),Avg('neutral'))
        
        self.avg_fear = aggregate['fear__avg']
        self.avg_anger = aggregate['anger__avg']
        self.avg_shame = aggregate['shame__avg']
        self.avg_guilt = aggregate['guilt__avg']
        self.avg_neutral = aggregate['neutral__avg']
        
        sumagg = self.avg_fear + self.avg_anger + self.avg_guilt + self.avg_shame + self.avg_neutral
        
        self.d_fear = 2* self.avg_fear - sumagg
        self.d_anger = 2* self.avg_anger - sumagg
        self.d_shame = 2* self.avg_shame - sumagg
        self.d_guilt = 2* self.avg_guilt - sumagg
        self.d_neutral = 2* self.avg_neutral - sumagg
        
        super(Result, self).save(*args,**kwargs)
        
def fillquestions():
    sentences = {}
    sentences['fear'] = [u"Ich rutsche an einem Berg ab.",
u"Ich verliere die Kontrolle über mein Fahrzeug.",
u"Ich bleibe im Aufzug stecken.",
u"Ich höre im Bett liegend unbekanntes Geräusch.",
u"Ich werde auf der Straße bedroht.",
u"Ich bin eingesperrt.",
u"Ich wache aus einem Alptraum auf.",
u"Ich werde in der Arbeit gekündigt.",
u"Ich habe meinen Talisman verloren.",
u"Ich verlaufe mich.",
u"Ich bin alleine im Wald.",
u"Ich gehe alleine nachts nach Hause.",
u"Ich weiß, dass sich ein Fremder in meiner Wohnung befindet.",
u"Ich habe eine tödliche Erkrankung.",
u"Ich werde erpresst.",
u"Ich werde plötzlich am Arm festgehalten.",
u"Ich werde verfolgt.",
u"Ich werde von einem großen Hund angebellt.",
u"Ich sitze in einem wackeligen Flugzeug.",
u"Ich stehe auf einer morschen Leiter.",
u"Ich sehe aus dem Augenwinkel einen Schatten.",
u"Ich sehe den Notarzt vor meiner Tür.",
u"Ich sehe mir einen Horrorfilm an.",
u"Ich laufe durch ein starkes Gewitter.",
u"Ich sehe ohne erkennbaren Grund die Tür aufgehen.",
u"Ich habe einen Glassplitter im Auge.",
u"Ich weiß nicht mehr wo ich wohne.",
u"Ich werde von einer Schlange gebissen.",
u"Ich muss Insolvenz anmelden.",
u"Ich befinde mich in einer schweren Prüfung.",
u"Ich halte einen Vortrag vor einem großen Publikum.",
u"Ich sehe meiner Mutter beim Sterben zu.",
u"Ich bin nicht ausreichend vorbereitet.",
u"Ich gehe die knarzende Kellertreppe hinab.",
u"Ich werde von einem großen Hund angeknurrt.",
u"Ich bekomme ein Kind.",
u"Ich verstecke mich.",
u"Ich kann auf einmal nicht mehr sehen.",
u"Ich muss operiert werden.",
u"Ich sehe ein Auto auf mich zurasen.",
u"Ich weiß nicht, wie ich mich verhalten soll.",
u"Ich fühle mich überfordert.",
u"Ich kann meinen Aufgaben nicht gerecht werden.",
u"Ich habe niemanden, der mir hilft.",
u"Ich muss große Verantwortung übernehmen."]

    sentences['anger'] = [u"Ich zerschlage aus Missgeschick meinen Kaffeebecher.",
"Ich mache trotz besseren Wissens einen Fehler.",
"Ich finde mein abgestelltes Fahrzeug mit einem Schaden vor.",
"Ich habe das Gefühl, dass mir jemand die Zeit stiehlt.",
u"Ich werde belogen.",
u"Ich warte lange an der Kasse.",
u"Ich versalze mein Essen.",
u"Ich werde angespuckt.",
u"Ich werde um Geld betrogen.",
u"Ich werde beschimpft.",
u"Ich werde getreten.",
u"Ich werde verarscht.",
u"Ich werde ungerecht behandelt.",
u"Ich werde von meinem Freund versetzt.",
u"Ich bezahle zu viel für etwas.",
u"Ich werde aus dem Schlaf geweckt.",
u"Ich werfe Geld in einen Automaten, welches stecken bleibt.",
u"Ich hätte es besser machen können.",
u"Ich trete auf meine Brille.",
u"Ich entscheide mich falsch.",
u"Ich trete in Hundekot.",
u"Ich lasse meinen Geldbeutel im Geschäft liegen.",
u"Ich vergesse etwas Wichtiges.",
u"Ich lasse meinen Schlüssel in der Wohnung liegen.",
u"Ich sehe meiner Lieblingsmannschaft beim Verlieren zu.",
u"Ich habe knapp das Ziel verpasst.",
u"Ich falle auf einen Streich herein.",
u"Ich verschütte aus Versehen Wasser über meinen Laptop.",
u"Ich bekleckere mein teures Hemd.",
u"Ich werde andauernd beim Sprechen unterbrochen.",
u"Ich werde ignoriert.",
u"Ich bin vor dem großen Fußballfinale eingeschlafen.",
u"Ich verliere bei einem Gesellschaftsspiel.",
u"Ich sehe meinen Kollegen beim Schleimen vor dem Chef zu.",
u"Ich erhalte die versprochene Gehaltserhöhung nicht.",
u"Ich konnte meine Daten vor einem PC-Absturz nicht sichern.",
u"Ich lösche Urlaubsbilder von meiner Camera.",
u"Ich finde mein Sparbuch nicht mehr.",
u"Ich lasse meinen neuen Fernseher fallen.",
u"Ich habe ein Andenken meiner Oma verloren.",
u"Ich sehe Regen bei meiner geplanten Grillfeier aufkommen.",
u"Ich werde als dumm bezeichnet.",
u"Ich werde belästigt.",
u"Ich habe keine Zeit für eine Pause.",
u"Ich bekomme zum gewünschten Zeitpunkt kein Hotelzimmer mehr."]

    sentences['shame'] = [u"Ich werde von meinen Eltern beim Sex erwischt.",
u"Ich bekomme einen Blackout bei einem Vortrag.",
u"Ich lasse das Essen für meine Gäste anbrennen.",
u"Ich muss mir von einem Freund Geld leihen.",
u"Ich pinkele in die Hose.",
u"Ich gehe mit weißem Badezeug ins Wasser.",
u"Ich schütte im Restaurant ein Weinglas um.",
u"Ich werfe bei einem Besuch eine Vase um.",
u"Ich muss im Krankenhaus eine Bettpfanne benutzen.",
u"Ich lache im Gespräch an einer unpassenden Stelle.",
u"Ich pupse laut in der Kirche.",
u"Ich steige meinem Tanzpartner auf die Füße.",
u"Ich erkenne einen alten Bekannten nicht.",
u"Ich vergreife mich in der Wortwahl.",
u"Ich lästere über jemanden, der zuhört.",
u"Ich verstopfe das Klo.",
u"Ich habe einen Pilz an den Genitalien.",
u"Ich verrate versehentlich ein Geheimnis.",
u"Ich bemerke, dass meine Hose offen steht.",
u"Ich habe versehentlich meinen Pullover verkehrt herum angezogen.",
u"Ich habe zwei ungleiche Socken an.",
u"Ich bin der einzig verkleidete auf einer Party.",
u"Ich werde beim Lügen ertappt.",
u"Ich habe Läuse.",
u"Ich laufe gegen eine Fensterscheibe.",
u"Ich stecke mit dem Schuh in einem Gitter fest.",
u"Ich laufe gedankenverloren vor einen Bus.",
u"Ich komme zu spät zu einem Termin.",
u"Ich bekomme bei einem Konzert einen Hustenanfall.",
u"Ich verwechsle einen Fremden mit meinem Partner.",
u"Ich falle durch die Fahrprüfung.",
u"Ich vergesse die Toilettentüre abzuschließen.",
u"Ich schwitze sichtlich unter den Armen.",
u"Ich habe Mundgeruch.",
u"Ich kann mich aufgrund von Alkohol an die gestrige Feier nicht mehr     erinnern.",
u"Ich sehe in der Zeitung meine Vergangenheit enthüllt.",
u"Ich verliere etwas Geliehenes.",
u"Ich niese über einen Geburtstagskuchen.",
u"Ich schicke einen fragenden Touristen in die falsche Richtung.",
u"Ich bin nicht frisiert.",
u"Ich remple im Getümmel eine alte Dame um.",
u"Ich komme zu früh zum Orgasmus.",
u"Ich treffe meinen Lehrer in der Sauna.",
u"Ich spucke beim Sprechen.",
u"Ich plaudere eine Überraschung aus."]

    sentences['guilt'] = [u"Ich belüge einen guten Freund.",
u"Ich betrüge meinen Partner.",
u"Ich behalte Spendengelder ein.",
u"Ich sage im Streit ungerechte Dinge.",
u"Ich verletzte einen anderen Menschen.",
u"Ich verursache einen Autounfall.",
u"Ich fahre betrunken Auto.",
u"Ich klaue einen Pulli.",
u"Ich mobbe einen Kollegen.",
u"Ich lasse die Tür auf und der Hund läuft weg.",
u"Ich übertrage eine Grippe an meine Kollegen.",
u"Ich schlage auf einen anderen Menschen ein.",
u"Ich trinke regelmäßig zu viel Alkohol.",
u"Ich fahre einen Igel tot.",
u"Ich zerstöre aus Wut eine Vase.",
u"Ich vergesse jemanden abzuholen.",
u"Ich behalte ein geplantes Verbrechen für mich.",
u"Ich erledige etwas nicht, worum ich gebeten wurde.",
u"Ich fahre in den Urlaub, während meine Mutter im Krankenhaus liegt.",
u"Ich kann etwas Schlimmes vorhersehen, tue aber nichts.",
u"Ich bin seit langem nicht mehr am Grab meiner Großeltern gewesen.",
u"Ich habe nicht genügend Zeit für meinen Partner.",
u"Ich esse nachts heimlich Süßigkeiten.",
u"Ich antworte nie auf den Brief einer Freundin.",
u"Ich sehe tatenlos zu, wie jemand verprügelt wird.",
u"Ich mache einen Fehler, den jemand anders ausbaden muss.",
u"Ich schreibe im Examen ab und bekomme eine bessere Note.",
u"Ich nutze einen Freund aus.",
u"Ich ruhe mich auf den Lorbeeren anderer aus.",
u"Ich befriedige mich selbst.",
u"Ich sage beim Sex den Namen des Expartners.",
u"Ich sage nichts, als eine dunkelhäutige Frau als Äffin bezeichnet wird.",
u"Ich begehe Fahrerflucht.",
u"Ich teile mein Wasser nicht mit jemand durstigem.",
u"Ich zertrete ein Spielzeug.",
u"Ich sage kurzfristig ein wichtiges Gespräch ab.",
u"Ich hindere jemanden nicht daran, einen Fehler zu begehen.",
u"Ich nehme keine Rücksicht auf andere.",
u"Ich lasse an dem nächst besten meine schlechte Laune aus.",
u"Ich schwänze die Arbeit.",
u"Ich missachte ein Verbot.",
u"Ich habe Vorurteile gegenüber Ausländern.",
u"Ich stolpere über einen kleinen Hund.",
u"Ich verurteile jemanden zu Unrecht.",
u"Ich gebe aus Versehen falsche Informationen weiter."]

    sentences['neutral']=["Ich koche mir einen Tee.",
u"Ich lese ein Buch.",
u"Ich telefoniere mit einer Sekretärin.",
u"Ich liege auf einem Stuhl in der Sonne.",
u"Ich koche das Essen.",
u"Ich fahre mit dem Fahrstuhl in das obere Stockwerk.",
u"Ich putze die Wohnung.",
u"Ich sehe am Abend fern.",
u"Ich putze mir die Zähne.",
u"Ich dusche am Morgen.",
u"Ich gehe Klamotten einkaufen.",
u"Ich schreibe einen Brief an einen Freund.",
u"Ich fahre mit dem Auto.",
u"Ich blase bunte Luftballons auf.",
u"Ich esse zu Abend.",
u"Ich blättere in einem Katalog.",
u"Ich fahre mit meinem Fahrrad.",
u"Ich packe meinen Koffer für den Urlaub.",
u"Ich topfe meine Blumen in einen größeren Topf um.",
u"Ich leere den vollen Müll aus.",
u"Ich mache ein Puzzle mit vielen Teilen.",
u"Ich sitze im Kino.",
u"Ich reiße eine Milchtüte auf.",
u"Ich spaziere gemütlich zum Bus.",
u"Ich nehme freiwillig an einer Befragung teil.",
u"Ich wähle eine Telefonnummer um einen Anruf zu tätigen.",
u"Ich nehme ein Stück Seife um meine Hände zu waschen.",
u"Ich parke das Auto.",
u"Ich löse das Ticket in der U-Bahn.",
u"Ich rühre die Milch im Kaffee um.",
u"Ich baue ein Regal für meine Bücher zusammen.",
u"Ich falte eine Decke und lege diese auf das Sofa.",
u"Ich reinige die Badezimmerfliesen.",
u"Ich sitze am Computer.",
u"Ich trinke in meiner Pause einen Kaffee.",
u"Ich sehe den Menschen auf der Straße zu.",
u"Ich kaufe für das Wochenende Essen ein.",
u"Ich creme mir die Hände ein.",
u"Ich sehe aus dem Fenster auf einen Baum.",
u"Ich höre einer Geschichte im Radio zu.",
u"Ich schüttele die Kissen meines Bettes auf.",
u"Ich knipse das Licht an.",
u"Ich verschließe einen Brief.",
u"Ich wische den Tisch ab.",
u"Ich gieße die Blumen auf meinem Balkon."]
    for cat in CATEGORIES:
        for sentence in sentences[cat]:
            Question(category=cat, sentence=sentence).save()

