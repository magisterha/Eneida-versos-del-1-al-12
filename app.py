import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Aeneis Tutor AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CORPUS: ENEIDA LIBRO I (TEXTO COMPLETO) ---
# MOVIDO AL PRINCIPIO PARA EVITAR NAME_ERROR
ENEIDA_LIBRO_I = """
Arma virumque cano, Troiae qui primus ab oris
    
 Italiam fato profugus Laviniaque venit
    
litora, multum ille et terris iactatus et alto,

vi superum, saevae memorem Iunonis ob iram,

5  multa quoque et bello passus, dum conderet urbem

inferretque deos Latio, genus unde Latinum

Albanique patres atque altae moenia Romae.

Musa, mihi causas memora, quo numine laeso

quidve dolens regina deum tot volvere casus

10 insignem pietate virum, tot adire labores

impulerit. Tantaene animis caelestibus irae?

Urbs antiqua fuit (Tyrii tenuere coloni)

Karthago, Italiam contra Tiberinaque longe

ostia, dives opum studiisque asperrima belli;

15 quam Iuno fertur terris magis omnibus unam

posthabita coluisse Samo: | hic illius arma,

hic currus fuit; hoc regnum dea gentibus esse,

si qua fata sinant, iam tum tenditque fovetque.

Progeniem sed enim Troiano sanguine duci

20 audierat, Tyrias olim quae verteret arces;

hinc populum late regem belloque superbum

venturum excidio Libyae: sic volvere Parcas.

Id metuens veterisque memor Saturnia belli,

prima quod ad Troiam pro caris gesserat Argis:

25 necdum etiam causae irarum saevique dolores

exciderant animo; manet alta mente repostum

iudicium Paridis spretaeque iniuria formae

et genus invisum et rapti Ganymedis honores:

his accensa super iactatos aequore toto

30 Troas, reliquias Danaum atque immitis Achilli,

arcebat longe Latio, multosque per annos

errabant acti fatis maria omnia circum.

Tantae molis erat Romanam condere gentem.

Vix e conspectu Siculae telluris in altum

35 vela dabant laeti et spumas salis aere ruebant,

cum Iuno aeternum servans sub pectore volnus

haec secum: "Mene incepto desistere victam

nec posse Italia Teucrorum avertere regem?

Quippe vetor fatis. Pallasne exurere classem

40 Argivum atque ipsos potuit submergere ponto

unius ob noxam et furias Aiacis Oilei?

Ipsa Iovis rapidum iaculata e nubibus ignem

disiecitque rates evertitque aequora ventis,

illum exspirantem transfixo pectore flammas

45 turbine corripuit scopuloque infixit acuto;

ast ego, quae divom incedo regina Iovisque

et soror et coniunx, una cum gente tot annos

bella gero. Et quisquam numen Iunonis adorat

praeterea aut supplex aris imponet honorem?"

50 Talia flammato secum dea corde volutans

nimborum in patriam, loca feta furentibus Austris,

Aeoliam venit. Hic vasto rex Aeolus antro

luctantis ventos tempestatesque sonoras

imperio premit ac vinclis et carcere frenat.

55Illi indignantes magno cum murmure montis

circum claustra fremunt; celsa sedet Aeolus arce

sceptra tenens mollitque animos et temperat iras.

Ni faciat, maria ac terras caelumque profundum

quippe ferant rapidi secum verrantque per auras:

60sed pater omnipotens speluncis abdidit atris

hoc metuens molemque et montis insuper altos

imposuit, regemque dedit qui foedere certo

et premere et laxas sciret dare iussus habenas.

Ad quem tum Iuno supplex his vocibus usa est:

65"Aeole (namque tibi divom pater atque hominum rex

et mulcere dedit fluctus et tollere vento),

gens inimica mihi Tyrrhenum navigat aequor,

Ilium et Italiam portans victosque penatis:

incute vim ventis submersasque obrue puppes,

70aut age diversos et dissice corpora ponto.

Sunt mihi bis septem praestanti corpore Nymphae,

quarum quae forma pulcherrima Deiopea,

conubio iungam stabili propriamque dicabo,

omnis ut tecum meritis pro talibus annos

75exigat et pulchra faciat te prole parentem".

Aeolus haec contra: "Tuus, o regina, quid optes,

explorare labor; mihi iussa capessere fas est.

Tu mihi quodcumque hoc regni, tu sceptra Iovemque

concilias, tu das epulis accumbere divom

80nimborumque facis tempestatumque potentem".

Haec ubi dicta, cavum conversa cuspide montem

impulit in latus: ac venti velut agmine facto,

qua data porta, ruunt et terras turbine perflant.

Incubuere mari totumque a sedibus imis

85una Eurusque Notusque ruunt creberque procellis

Africus et vastos volvunt ad litora fluctus.

Insequitur clamorque virum stridorque rudentum.

Eripiunt subito nubes caelumque diemque

Teucrorum ex oculis; ponto nox incubat atra;

90intonvere poli et crebris micat ignibus aether

praesentemque viris intentant omnia mortem.

Extemplo Aeneae solvuntur frigore membra;

ingemit et duplicis tendens ad sidera palmas

talia voce refert: "O terque quaterque beati,

95quis ante ora patrum Troiae sub moenibus altis

contigit oppetere! o Danaum fortissime gentis

Tydide! mene Iliacis occumbere campis

non potuisse tuaque animam hanc effundere dextra,

saevus ubi Aeacidae telo iacet Hector, ubi ingens

100 Sarpedon, ubi tot Simois correpta sub undis

scuta virum galeasque et fortia corpora volvit!"

Talia iactanti stridens Aquilone procella

velum adversa ferit fluctusque ad sidera tollit.

Franguntur remi; tum prora avertit et undis

105 dat latus: insequitur cumulo praeruptus aquae mons.

Hi summo in fluctu pendent; his unda dehiscens

terram inter fluctus aperit, furit aestus harenis.

Tris Notus abreptas in saxa latentia torquet

(saxa vocant Itali, mediis quae in fluctibus, Aras,

110dorsum immane mari summo), tris Eurus ab alto

in brevia et Syrtis urguet (miserabile visu)

inliditque vadis atque aggere cingit harenae.

Unam, quae Lycios fidumque vehebat Oronten,

ipsius ante oculos ingens a vertice pontus

115 in puppim ferit: excutitur pronusque magister

volvitur in caput; ast illam ter fluctus ibidem

torquet agens circum et rapidus vorat aequore vortex.

Apparent rari nantes in gurgite vasto,

arma virum tabulaeque et Troia gaza per undas.

120 Iam validam Ilionei navem, iam fortis Achatae

et qua vectus Abas et qua grandaevos Aletes,

vicit hiemps; laxis laterum compagibus omnes

accipiunt inimicum imbrem rimisque fatiscunt.

Interea magno misceri murmure pontum

125 emissamque hiemem sensit Neptunus et imis

stagna refusa vadis, graviter commotus, et alto

prospiciens summa placidum caput extulit unda.

Disiectam Aeneae toto videt aequore classem,

fluctibus oppressos Troas caelique ruina.

130 Nec latuere doli fratrem Iunonis et irae.

Eurum ad se Zephyrumque vocat, dehinc talia fatur:

"Tantane vos generis tenuit fiducia vestri?

iam caelum terramque meo sine numine, venti,

miscere et tantas audetis tollere moles?

135 Quos ego! sed motos praestat componere fluctus.

Post mihi non simili poena commissa luetis.

Maturate fugam regique haec dicite vestro:

non illi imperium pelagi saevumque tridentem,

sed mihi sorte datum. Tenet ille immania saxa,

140 vestras, Eure, domos; illa se iactet in aula

Aeolus et clauso ventorum carcere regnet".

Sic ait et dicto citius tumida aequora placat

collectasque fugat nubes solemque reducit.

Cymothoë simul et Triton adnixus acuto

145 detrudunt navis scopulo; levat ipse tridenti

et vastas aperit Syrtis et temperat aequor

atque rotis summas levibus perlabitur undas.

Ac veluti in magno populo cum saepe coorta est

seditio saevitque animis ignobile vulgus,

150 iamque faces et saxa volant, furor arma ministrat:

tum pietate gravem ac meritis si forte virum quem

conspexere, silent arrectisque auribus adstant;

ille regit dictis animos et pectora mulcet:

sic cunctus pelagi cecidit fragor, aequora postquam

155 prospiciens genitor caeloque invectus aperto

flectit equos curruque volans dat lora secundo.

Defessi Aeneadae, quae proxima litora, cursu

contendunt petere et Libyae vertuntur ad oras.

Est in secessu longo locus: insula portum

160 efficit obiectu laterum, quibus omnis ab alto

frangitur inque sinus scindit sese unda reductos.

Hinc atque hinc vastae rupes geminique minantur

in caelum scopuli, quorum sub vertice late

aequora tuta silent; tum silvis scaena coruscis

165 desuper horrentique atrum nemus imminet umbra.

Fronte sub adversa scopulis pendentibus antrum:

intus aquae dulces vivoque sedilia saxo,

Nympharum domus. Hic fessas non vincula navis

ulla tenent, unco non alligat ancora morsu.

170 Huc septem Aeneas collectis navibus omni

ex numero subit, ac magno telluris amore

egressi optata potiuntur Troes harena

et sale tabentis artus in litore ponunt.

Ac primum silici scintillam excudit Achates

175 succepitque ignem foliis atque arida circum

nutrimenta dedit rapuitque in fomite flammam.

Tum Cererem corruptam undis Cerealiaque arma

expediunt fessi rerum frugesque receptas

et torrere parant flammis et frangere saxo.

180 Aeneas scopulum interea conscendit et omnem

prospectum late pelago petit, Anthea si quem

iactatum vento videat Phrygiasque biremis

aut Capyn aut celsis in puppibus arma Caici.

Navem in conspectu nullam, tris litore cervos

185 prospicit errantis; hos tota armenta secuntur

a tergo et longum per vallis pascitur agmen.

Constitit hic arcumque manu celerisque sagittas

corripuit fidus quae tela gerebat Achates,

ductoresque ipsos primum, capita alta ferentis

190 cornibus arboreis, sternit, tum volgus et omnem

miscet agens telis nemora inter frondea turbam;

nec prius abstitit, quam septem ingentia victor

corpora fundat humi et numerum cum navibus aequet;

hinc portum petit et socios partitur in omnis.

195 Vina bonus quae deinde cadis onerarat Acestes

litore Trinacrio dederatque abeuntibus, heros

dividit et dictis maerentia pectora mulcet:

"O socii (neque enim ignari sumus ante malorum),

o passi graviora, dabit deus hic quoque finem.

200 Vos et Scyllaeam rabiem penitusque sonantis

accestis scopulos, vos et Cyclopia saxa

experti: revocate animos maestumque timorem

mittite; forsan et haec olim meminisse iuvabit.

Per varios casus per tot discrimina rerum

205 tendimus in Latium, sedes ubi fata quietas

ostendunt; illic fas regna resurgere Troiae.

Durate et vosmet rebus servate secundis".

Talia voce refert curisque ingentibus aeger

spem voltu simulat, premit altum corde dolorem.

210 Illi se praedae accingunt dapibusque futuris:

tergora diripiunt costis et viscera nudant;

pars in frusta secant veribusque trementia figunt,

litore aëna locant alii flammasque ministrant.

Tum victu revocant viris fusique per herbam

215 implentur veteris Bacchi pinguisque ferinae.

Postquam exempta fames epulis mensaeque remotae,

amissos longo socios sermone requirunt

spemque metumque inter dubii, seu vivere credant

sive extrema pati nec iam exaudire vocatos.

220 Praecipue pius Aeneas nunc acris Oronti,

nunc Amyci casum gemit et crudelia secum

fata Lyci fortemque Gyan fortemque Cloanthum.

Et iam finis erat, cum Iuppiter aethere summo

despiciens mare velivolum terrasque iacentis

225 litoraque et latos populos, sic vertice caeli

constitit et Libyae defixit lumina regnis.

Atque illum talis iactantem pectore curas

tristior et lacrimis oculos suffusa nitentis

adloquitur Venus: "O qui res hominumque deumque

230 aeternis regis imperiis et fulmine terres,

quid meus Aeneas in te committere tantum,

quid Troes potuere, quibus tot funera passis

cunctus ob Italiam terrarum clauditur orbis?

Certe hinc Romanos olim volventibus annis,

235 hinc fore ductores revocato a sanguine Teucri,

qui mare, qui terras omnis dicione tenerent,

pollicitus: quae te, genitor, sententia vertit?

Hoc equidem occasum Troiae tristisque ruinas

solabar fatis contraria fata rependens;

240 nunc eadem fortuna viros tot casibus actos

insequitur. Quem das finem, rex magne, laborum?

Antenor potuit mediis elapsus Achivis

Illyricos penetrare sinus atque intuma tutus

regna Liburnorum et fontem superare Timavi,

245 unde per ora novem vasto cum murmure montis

it mare proruptum et pelago premit arva sonanti.

Hic tamen ille urbem Patavi sedesque locavit

Teucrorum et genti nomen dedit armaque fixit

Troia, nunc placida compostus pace quiescit:

250 nos, tua progenies, caeli quibus adnuis arcem,

navibus (infandum!) amissis unius ob iram

prodimur atque Italis longe disiungimur oris.

Hic pietatis honos? sic nos in sceptra reponis?"

Olli subridens hominum sator atque deorum

255 voltu, quo caelum tempestatesque serenat,

oscula libavit natae, dehinc talia fatur:

"Parce metu, Cytherea: manent immota tuorum

fata tibi; cernes urbem et promissa Lavini

moenia sublimemque feres ad sidera caeli

260 magnanimum Aenean; neque me sententia vertit.

Hic tibi (fabor enim, quando haec te cura remordet,

longius, et volvens fatorum arcana movebo)

bellum ingens geret Italia populosque ferocis

contundet moresque viris et moenia ponet,

265 tertia dum Latio regnantem viderit aestas

ternaque transierint Rutulis hiberna subactis.

At puer Ascanius, quoi nunc cognomen Iulo

additur (Ilus erat, dum res stetit Ilia regno),

triginta magnos volvendis mensibus orbis

270 imperio explebit regnumque ab sede Lavini

transferet et Longam multa vi muniet Albam.

Hic iam ter centum totos regnabitur annos

gente sub Hectorea, donec regina sacerdos

Marte gravis geminam partu dabit Ilia prolem.

275 Inde lupae fulvo nutricis tegmine laetus

Romulus excipiet gentem et Mavortia condet

moenia Romanosque suo de nomine dicet.

His ego nec metas rerum nec tempora pono,

imperium sine fine dedi. Quin aspera Iuno,

280 quae mare nunc terrasque metu caelumque fatigat,

consilia in melius referet mecumque fovebit

Romanos, rerum dominos gentemque togatam.

Sic placitum. Veniet lustris labentibus aetas,

cum domus Assaraci Phthiam clarasque Mycenas

285 servitio premet ac victis dominabitur Argis.

Nascetur pulchra Troianus origine Caesar,

imperium Oceano, famam qui terminet astris,

Iulius, a magno demissum nomen Iulo.

Hunc tu olim caelo spoliis Orientis onustum

290 accipies secura; vocabitur hic quoque votis.

Aspera tum positis mitescent saecula bellis:

cana Fides et Vesta, Remo cum fratre Quirinus

iura dabunt; dirae ferro et compagibus artis

claudentur Belli portae; Furor impius intus

295 saeva sedens super arma et centum vinctus aenis

post tergum nodis fremet horridus ore cruento".

Haec ait et Maia genitum demittit ab alto,

ut terrae utque novae pateant Karthaginis arces

hospitio Teucris, ne fati nescia Dido

300 finibus arceret. Volat ille per aëra magnum

remigio alarum ac Libyae citus adstitit oris.

Et iam iussa facit ponuntque ferocia Poeni

corda volente deo; in primis regina quietum

accipit in Teucros animum mentemque benignam.

305 At pius Aeneas per noctem plurima volvens,

ut primum lux alma datast, exire locosque

explorare novos, quas vento accesserit oras,

qui teneant (nam inculta videt), hominesne feraene,

quaerere constituit sociisque exacta referre.

310 Classem in convexo nemorum sub rupe cavata

arboribus clausam circum atque horrentibus umbris

occulit; ipse uno graditur comitatus Achate

bina manu lato crispans hastilia ferro.

Cui mater media sese tulit obvia silva,

315 virginis os habitumque gerens et virginis arma,

Spartanae vel qualis equos Threissa fatigat

Harpalyce volucremque fuga praevertitur Hebrum.

Namque humeris de more habilem suspenderat arcum

venatrix dederatque comam diffundere ventis,

320 nuda genu nodoque sinus collecta fluentis.

Ac prior: "Heus" inquit "iuvenes, monstrate, mearum

vidistis si quam hic errantem forte sororum

succinctam pharetra et maculosae tegmine lyncis,

aut spumantis apri cursum clamore prementem".

325 Sic Venus, et Veneris contra sic filius orsus:

"Nulla tuarum audita mihi neque visa sororum,

o ... quam te memorem, virgo? namque haut tibi voltus

mortalis, nec vox hominem sonat; o, dea, certe

(an Phoebi soror? an Nympharum sanguinis una?),

330 sis felix nostrumque leves, quaecumque, laborem

et quo sub caelo tandem, quibus orbis in oris

iactemur, doceas: ignari hominumque locorumque

erramus, vento huc vastis et fluctibus acti.

Multa tibi ante aras nostra cadet hostia dextra".

335 Tum Venus: "Haut equidem tali me dignor honore;

virginibus Tyriis mos est gestare pharetram

purpureoque alte suras vincire coturno.

Punica regna vides, Tyrios et Agenoris urbem;

sed fines Libyci, genus intractabile bello.

340 Imperium Dido Tyria regit urbe profecta,

germanum fugiens. Longa est iniuria, longae

ambages; sed summa sequar fastigia rerum.

Huic coniunx Sychaeus erat, ditissimus agri

Phoenicum et magno miserae dilectus amore,

345 cui pater intactam dederat primisque iugarat

ominibus. Sed regna Tyri germanus habebat

Pygmalion, scelere ante alios immanior omnis.

Quos inter medius venit furor. Ille Sychaeum

impius ante aras atque auri caecus amore

350 clam ferro incautum superat, securus amorum

germanae; factumque diu celavit et aegram

multa malus simulans vana spe lusit amantem.

Ipsa sed in somnis inhumati venit imago

coniugis ora modis attollens pallida miris;

355 crudelis aras traiectaque pectora ferro

nudavit caecumque domus scelus omne retexit.

Tum celerare fugam patriaque excedere suadet

auxiliumque viae veteres tellure recludit

thensauros, ignotum argenti pondus et auri.

360 His commota fugam Dido sociosque parabat.

Conveniunt, quibus aut odium crudele tyranni

aut metus acer erat; navis, quae forte paratae,

corripiunt onerantque auro. Portantur avari

Pygmalionis opes pelago; dux femina facti.

365 Devenere locos, ubi nunc ingentia cernes

moenia surgentemque novae Karthaginis arcem,

mercatique solum, facti de nomine Byrsam,

taurino quantum possent circumdare tergo.

Sed vos qui tandem? Quibus aut venistis ab oris?

370 Quove tenetis iter?". Quaerenti talibus ille

suspirans imoque trahens a pectore vocem:

"O dea, si prima repetens ab origine pergam

et vacet annalis nostrorum audire laborum,

ante diem clauso componet Vesper Olympo.

375 Nos Troia antiqua, si vestras forte per auris

Troiae nomen iit, diversa per aequora vectos

forte sua Libycis tempestas appulit oris.

Sum pius Aeneas, raptos qui ex hoste penates

classe veho mecum, fama super aethera notus;

380 Italiam quaero patriam et genus ab Iove magno.

Bis denis Phrygium conscendi navibus aequor

matre dea monstrante viam data fata secutus;

vix septem convolsae undis Euroque supersunt.

Ipse ignotus, egens, Libyae deserta peragro,

385 Europa atque Asia pulsus". Nec plura querentem

passa Venus medio sic interfata dolore est:

"Quisquis es, haut, credo, invisus caelestibus auras

vitalis carpis, Tyriam qui adveneris urbem;

perge modo atque hinc te reginae ad limina perfer.

390 Namque tibi reduces socios classemque relatam

nuntio et in tutum versis Aquilonibus actam,

ni frustra augurium vani docuere parentes.

Aspice bis senos laetantis agmine cycnos,

aetheria quos lapsa plaga Iovis ales aperto

395 turbabat caelo; nunc terras ordine longo

aut capere aut captas iam despectare videntur:

ut reduces illi ludunt stridentibus alis

et coetu cinxere polum cantusque dedere,

aut aliter puppesque tuae pubesque tuorum

400 aut portum tenet aut pleno subit ostia velo.

Perge modo et, qua te ducit via, derige gressum".

Dixit et avertens rosea cervice refulsit

ambrosiaeque comae divinum vertice odorem

spiravere; pedes vestis defluxit ad imos,

405 et vera incessu patuit dea. Ille ubi matrem

adgnovit, tali fugientem est voce secutus:

"Quid natum totiens, crudelis tu quoque, falsis

ludis imaginibus? Cur dextrae iungere dextram

non datur ac veras audire et reddere voces?"

410 Talibus incusat gressumque ad moenia tendit.

At Venus obscuro gradientis aëre saepsit

et multo nebulae circum dea fudit amictu,

cernere ne quis eos neu quis contingere posset

molirive moram aut veniendi poscere causas.

415 Ipsa Paphum sublimis abit sedesque revisit

laeta suas, ubi templum illi centumque Sabaeo

ture calent arae sertisque recentibus halant.

Corripuere viam interea, qua semita monstrat.

Iamque ascendebant collem, qui plurimus urbi

420 imminet adversasque aspectet desuper arces.

Miratur molem Aeneas, magalia quondam,

miratur portas strepitumque et strata viarum.

Instant ardentes Tyrii: pars ducere muros

molirique arcem et manibus subvolvere saxa,

425 pars optare locum tecto et concludere sulco;

iura magistratusque legunt sanctumque senatum.

Hic portus alii effodiunt, hic alta theatris

fundamenta petunt alii immanisque columnas

rupibus excidunt, scaenis decora alta futuris.

430 Qualis apes aestate nova per florea rura

exercet sub sole labor, cum gentis adultos

educunt fetus, aut cum liquentia mella

stipant et dulci distendunt nectare cellas,

aut onera accipiunt venientum, aut agmine facto

435 ignavum fucos pecus a praesepibus arcent;

fervet opus redolentque thymo flagrantia mella.

"O fortunati, quorum iam moenia surgunt!"

Aeneas ait et fastigia suspicit urbis.

Infert se saeptus nebula (mirabile dictu)

440 per medios miscetque viris neque cernitur ulli.

Lucus in urbe fuit media, laetissimus umbrae,

quo primum iactati undis et turbine Poeni

effodere loco signum, quod regia Iuno

monstrarat, caput acris equi; sic nam fore bello

445 egregiam et facilem victu per saecula gentem.

Hic templum Iunoni ingens Sidonia Dido

condebat, donis opulentum et numine divae,

aerea cui gradibus surgebant limina nexaeque

aere trabes, foribus cardo stridebat aenis.

450 Hoc primum in luco nova res oblata timorem

leniit, hic primum Aeneas sperare salutem

ausus et adflictis melius confidere rebus.

Namque sub ingenti lustrat dum singula templo

reginam opperiens, dum, quae fortuna sit urbi,

455 artificumque manus inter se operumque laborem

miratur, videt Iliacas ex ordine pugnas

bellaque iam fama totum volgata per orbem,

Atridas Priamumque et saevom ambobus Achillem.

Constitit et lacrimans: "Quis iam locus" inquit, "Achate,

460 quae regio in terris nostri non plena laboris?

En Priamus. Sunt hic etiam sua praemia laudi,

sunt lacrimae rerum et mentem mortalia tangunt.

Solve metus; feret haec aliquam tibi fama salutem".

Sic ait atque animum pictura pascit inani

465 multa gemens largoque umectat flumine voltum.

Namque videbat uti bellantes Pergama circum

hac fugerent Grai, premeret Troiana iuventus;

hac Phryges, instaret curru cristatus Achilles.

Nec procul hinc Rhesi niveis tentoria velis

470 adgnoscit lacrimans, primo quae prodita somno

Tydides multa vastabat caede cruentus,

ardentisque avertit equos in castra priusquam

pabula gustassent Troiae Xanthumque bibissent.

Parte alia fugiens amissis Troilus armis,

475 infelix puer atque impar congressus Achilli,

fertur equis curruque haeret resupinus inani,

lora tenens tamen; huic cervixque comaeque trahuntur

per terram et versa pulvis inscribitur hasta.

Interea ad templum non aequae Palladis ibant

480 crinibus Iliades passis peplumque ferebant

suppliciter, tristes et tunsae pectora palmis;

diva solo fixos oculos aversa tenebat.

Ter circum Iliacos raptaverat Hectora muros

exanimumque auro corpus vendebat Achilles.

485 Tum vero ingentem gemitum dat pectore ab imo,

ut spolia, ut currus, utque ipsum corpus amici

tendentemque manus Priamum conspexit inermis.

Se quoque principibus permixtum agnovit Achivis

Eoasque acies et nigri Memnonis arma.

490 Ducit Amazonidum lunatis agmina peltis

Penthesilea furens mediisque in milibus ardet,

aurea subnectens exsectae cingula mammae,

bellatrix, audetque viris concurrere virgo.

Haec dum Dardanio Aeneae miranda videntur,

495 dum stupet obtutuque haeret defixus in uno,

regina ad templum, forma pulcerrima Dido,

incessit magna iuvenum stipante caterva.

Qualis in Eurotae ripis aut per iuga Cynthi

exercet Diana choros, quam mille secutae

500 hinc atque hinc glomerantur Oreades; illa pharetram

fert umero gradiensque deas supereminet omnis

(Latonae tacitum pertemptant gaudia pectus):

talis erat Dido, talem se laeta ferebat

per medios instans operi regnisque futuris.

505 Tum foribus divae, media testudine templi,

saepta armis solioque alte subnixa resedit.

Iura dabat legesque viris operumque laborem

partibus aequabat iustis aut sorte trahebat:

cum subito Aeneas concursu accedere magno

510 Anthea Sergestumque videt fortemque Cloanthum

Teucrorumque alios, ater quos aequore turbo

dispulerat penitusque alias avexerat oras.

Obstipuit simul ipse, simul percussus Achates

laetitiaque metuque; avidi coniungere dextras

515 ardebant, sed res animos incognita turbat.

Dissimulant et nube cava speculantur amicti,

quae fortuna viris, classem quo litore linquant,

quid veniant: cunctis nam lecti navibus ibant

orantes veniam et templum clamore petebant.

520 Postquam introgressi et coram data copia fandi,

maximus Ilioneus placido sic pectore coepit:

"O regina, novam cui condere Iuppiter urbem

iustitiaque dedit gentis frenare superbas,

Troes te miseri, ventis maria omnia vecti,

525 oramus: prohibe infandos a navibus ignis,

parce pio generi et propius res aspice nostras.

Non nos aut ferro Libycos populare penatis

venimus aut raptas ad litora vertere praedas;

non ea vis animo nec tanta superbia victis.

530 Est locus, Hesperiam Grai cognomine dicunt,

terra antiqua, potens armis atque ubere glebae;

Oenotri coluere viri; nunc fama minores

Italiam dixisse ducis de nomine gentem.

Hic cursus fuit,

535 cum subito adsurgens fluctu nimbosus Orion

in vada caeca tulit penitusque procacibus Austris

perque undas superante salo perque invia saxa

dispulit: huc pauci vestris adnavimus oris.

Quod genus hoc hominum? Quaeve hunc tam barbara morem

540 permittit patria? Hospitio prohibemur harenae;

bella cient primaque vetant consistere terra.

Si genus humanum et mortalia temnitis arma,

at sperate deos memores fandi atque nefandi.

Rex erat Aeneas nobis, quo iustior alter

545 nec pietate fuit nec bello maior et armis.

Quem si fata virum servant, si vescitur aura

aetheria neque adhuc crudelibus occubat umbris,

non metus, officio nec te certasse priorem

paeniteat. Sunt et Siculis regionibus urbes

550 armaque Troianoque a sanguine clarus Acestes.

Quassatam ventis liceat subducere classem

et silvis aptare trabes et stringere remos,

si datur Italiam sociis et rege recepto

tendere, ut Italiam laeti Latiumque petamus;

555 sin absumpta salus et te, pater optume Teucrum,

pontus habet Libyae nec spes iam restat Iuli,

at freta Sicaniae saltem sedesque paratas,

unde huc advecti, regemque petamus Acesten."

Talibus Ilioneus; cuncti simul ore fremebant

560 Dardanidae.

Tum breviter Dido voltum demissa profatur:

"Solvite corde metum, Teucri, secludite curas.

Res dura et regni novitas me talia cogunt

moliri et late finis custode tueri.

565 Quis genus Aeneadum, quis Troiae nesciat urbem

virtutesque virosque aut tanti incendia belli?

Non obtunsa adeo gestamus pectora Poeni,

nec tam aversus equos Tyria Sol iungit ab urbe.

Seu vos Hesperiam magnam Saturniaque arva

570 sive Erycis finis regemque optatis Acesten,

auxilio tutos dimittam opibusque iuvabo.

Voltis et his mecum pariter considere regnis?

Urbem quam statuo, vestra est; subducite navis;

Tros Tyriusque mihi nullo discrimine agetur.

575 Atque utinam rex ipse Noto compulsus eodem

adforet Aeneas! Equidem per litora certos

dimittam et Libyae lustrare extrema iubebo,

si quibus eiectus silvis aut urbibus errat".

His animum arrecti dictis et fortis Achates

580 et pater Aeneas iamdudum erumpere nubem

ardebant. Prior Aenean compellat Achates:

"Nate dea, quae nunc animo sententia surgit?

omnia tuta vides, classem sociosque receptos.

Unus abest, medio in fluctu quem vidimus ipsi

585 submersum; dictis respondent cetera matris".

Vix ea fatus erat, cum circumfusa repente

scindit se nubes et in aethera purgat apertum.

Restitit Aeneas claraque in luce refulsit

os umerosque deo similis; namque ipsa decoram

590 caesariem nato genetrix lumenque iuventae

purpureum et laetos oculis adflarat honores:

quale manus addunt ebori decus aut ubi flavo

argentum Pariusve lapis circumdatur auro.

Tum sic reginam adloquitur cunctisque repente

595 inprovisus ait: "Coram, quem quaeritis, adsum

Troius Aeneas, Libycis ereptus ab undis.

O sola infandos Troiae miserata labores,

quae non, reliquias Danaum, terraeque marisque

omnibus exhaustos iam casibus, omnium egenos,

600 urbe, domo socias, grates persolvere dignas

non opis est nostrae, Dido, nec quidquid ubique est

gentis Dardaniae, magnum quae sparsa per orbem.

Di tibi, si qua pios respectant numina, si quid

usquam iustitiae est, et mens sibi conscia recti,

605 praemia digna ferant. Quae te tam laeta tulerunt

saecula? Qui tanti talem genuere parentes?

In freta dum fluvii current, dum montibus umbrae

lustrabunt convexa, polus dum sidera pascet,

semper honos nomenque tuum laudesque manebunt,

610 quae me cumque vocant terrae". Sic fatus amicum

Ilionea petit dextra laevaque Serestum,

post alios, fortemque Gyan fortemque Cloanthum.

Obstipuit primo aspectu Sidonia Dido,

casu deinde viri tanto, et sic ore locuta est:

615 "Quis te, nate dea, per tanta pericula casus

insequitur? Quae vis immanibus applicat oris?

Tune ille Aeneas quem Dardanio | Anchisae

alma Venus Phrygii genuit Simoentis ad undam?

Atque equidem Teucrum memini Sidona venire

620 finibus expulsum patriis, nova regna petentem

auxilio Beli; genitor tum Belus opimam

vastabat Cyprum et victor dicione tenebat.

Tempore iam ex illo casus mihi cognitus urbis

Troianae nomenque tuum regesque Pelasgi.

625 Ipse hostis Teucros insigni laude ferebat

seque ortum antiqua Teucrorum a stirpe volebat.

Quare agite, o tectis, iuvenes, succedite nostris.

Me quoque per multos similis fortuna labores

iactatam hac demum volvit consistere terra;

630 non ignara mali miseris succurrere disco".

Sic memorat; simul Aenean in regia ducit

tecta, simul divom templis indicit honorem.

Nec minus interea sociis ad litora mittit

viginti tauros, magnorum horrentia centum

635 terga suum, pinguis centum cum matribus agnos,

munera laetitiamque diei.

Ac domus interior regali splendida luxu

instruitur, mediisque parant convivia tectis:

arte laboratae vestes ostroque superbo,

640 ingens argentum mensis caelataque in auro

fortia facta patrum, series longissima rerum

per tot ducta viros antiquae ab origine gentis.

Aeneas (neque enim patrius consistere mentem

passus amor) rapidum ad navis praemittit Achaten,

645 Ascanio ferat haec ipsumque ad moenia ducat;

omnis in Ascanio cari stat cura parentis.

Munera praeterea Iliacis erepta ruinis

ferre iubet, pallam signis auroque rigentem

et circumtextum croceo velamen acantho,

650 ornatus Argivae Helenae, quos illa Mycenis,

Pergama cum peteret inconcessosque hymenaeos,

extulerat, matris Ledae mirabile donum;

praeterea sceptrum, Ilione quod gesserat olim,

maxima natarum Priami colloque monile

655 bacatum et duplicem gemmis auroque coronam.

Haec celerans iter ad navis tendebat Achates.

At Cytherea novas artes, nova pectore versat

consilia, ut faciem mutatus et ora Cupido

pro dulci Ascanio veniat donisque furentem

660 incendat reginam atque ossibus implicet ignem.

Quippe domum timet ambiguam Tyriosque bilinguis;

urit atrox Iuno et sub noctem cura recursat.

Ergo his aligerum dictis adfatur Amorem:

"Nate, meae vires, mea magna potentia, solus

665 nate patris summi qui tela Typhoia temnis,

ad te confugio et supplex tua numina posco.

Frater ut Aeneas pelago tuus omnia circum

litora iactetur odiis Iunonis acerbae,

nota tibi, et nostro doluisti saepe dolore.

670 Nunc Phoenissa tenet Dido blandisque moratur

vocibus, et vereor quo se Iunonia vertant

hospitia: haut tanto cessabit cardine rerum.

Quocirca capere ante dolis et cingere flamma

reginam meditor, ne quo se numine mutet,

675 sed magno Aeneae mecum teneatur amore.

Qua facere id possis nostram nunc accipe mentem:

regius accitu cari genitoris ad urbem

Sidoniam puer ire parat, mea maxima cura,

dona ferens pelago et flammis restantia Troiae;

680 hunc ego sopitum somno super alta Cythera

aut super Idalium sacrata sede recondam,

ne qua scire dolos mediusve occurrere possit.

Tu faciem illius noctem non amplius unam

falle dolo et notos pueri puer indue voltus,

685 ut, cum te gremio accipiet laetissima Dido

regalis inter mensas laticemque Lyaeum,

cum dabit amplexus atque oscula dulcia figet,

occultum inspires ignem fallasque veneno".

Paret Amor dictis carae genetricis et alas

690 exuit et gressu gaudens incedit Iuli.

At Venus Ascanio placidam per membra quietem

inrigat et fotum gremio dea tollit in altos

Idaliae lucos, ubi mollis amaracus illum

floribus et dulci adspirans complectitur umbra.

695 Iamque ibat dicto parens et dona Cupido

regia portabat Tyriis duce laetus Achate.

Cum venit, aulaeis iam se regina superbis

aurea composuit sponda mediamque locavit;

iam pater Aeneas et iam Troiana iuventus

700 conveniunt stratoque super discumbitur ostro.

Dant manibus famuli lymphas Cereremque canistris

expediunt tonsisque ferunt mantelia villis.

Quinquaginta intus famulae, quibus ordine longam

cura penum struere et flammis adolere penatis;

705 centum aliae totidemque pares aetate ministri,

qui dapibus mensas onerent et pocula ponant.

Nec non et Tyrii per limina laeta frequentes

convenere; toris iussi discumbere pictis

mirantur dona Aeneae, mirantur Iulum

710 flagrantisque dei voltus simulataque verba

pallamque et pictum croceo velamen acantho.

Praecipue infelix, pesti devota futurae,

expleri mentem nequit ardescitque tuendo

Phoenissa et pariter puero donisque movetur.

715 Ille ubi complexu Aeneae colloque pependit

et magnum falsi implevit genitoris amorem,

reginam petit. Haec oculis, haec pectore toto

haeret et interdum gremio fovet inscia Dido

insidat quantus miserae deus. At memor ille

720 matris Acidaliae paulatim abolere Sychaeum

incipit et vivo temptat praevertere amore

iam pridem resides animos desuetaque corda.

Postquam prima quies epulis mensaeque remotae,

crateras magnos statuunt et vina coronant.

725 Fit strepitus tectis vocemque per ampla volutant

atria; dependent lychni laquearibus aureis

incensi et noctem flammis funalia vincunt.

Hic regina gravem gemmis auroque poposcit

implevitque mero pateram, quam Belus et omnes

730 a Belo soliti; tum facta silentia tectis:

"Iuppiter (hospitibus nam te dare iura locuntur)

hunc laetum Tyriisque diem Troiaque profectis

esse velis nostrosque huius meminisse minores.

Adsit laetitiae Bacchus dator et bona Iuno;

735 et vos o coetum, Tyrii, celebrate faventes".

Dixit et in mensam laticum libavit honorem

primaque libato summo tenus attigit ore;

tum Bitiae dedit increpitans; ille impiger hausit

spumantem pateram et pleno se proluit auro;

740 post alii proceres. Cithara crinitus Iopas

personat aurata, docuit quem maximus Atlans.

Hic canit errantem lunam solisque labores,

unde hominum genus et pecudes, unde imber et ignes,

Arcturum pluviasque Hyadas geminosque Triones,

745 quid tantum Oceano properent se tinguere soles

hiberni vel quae tardis mora noctibus obstet;

ingeminant plausu Tyrii Troesque secuntur.

Nec non et vario noctem sermone trahebat

infelix Dido longumque bibebat amorem,

750 multa super Priamo rogitans, super Hectore multa;

nunc quibus Aurorae venisset filius armis,

nunc quales Diomedis equi, nunc quantus Achilles.

"Immo age et a prima dic, hospes, origine nobis

insidias" inquit, "Danaum casusque tuorum

755 erroresque tuos; nam te iam septima portat

omnibus errantem terris et fluctibus aestas".
"""

# --- 2. GESTIÓN DEL TEXTO (CORPUS VERGILIANUM) ---
# Función para manejar el texto. En lugar de una lista manual, procesamos un bloque.
def obtener_versos_libro_i():
    # El texto completo está al inicio del script en la variable ENEIDA_LIBRO_I
    # Limpiamos espacios y separamos por saltos de línea
    lines = [line.strip() for line in ENEIDA_LIBRO_I.strip().split('\n') if line.strip()]
    return lines

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
URL_HOJA_CALCULO = "https://docs.google.com/spreadsheets/d/1022thHT1sGmNBhYdty1lXLELSK6MYQWc1GaMILlzZtQ/edit?usp=sharing"

# --- 3. DICCIONARIO DE TRADUCCIONES ---
TRADUCCIONES = {
    "Español": {
        "sidebar_title": "🏛️ Configuración",
        "lang_label": "Idioma del Tutor:",
        "nav_label": "📜 Navegación (Versos):",
        "reset_btn": "🔄 Reiniciar Consulta",
        "header": "P. Vergili Maronis: Aeneis (Liber I)",
        "chat_header": "💬 Consulta Filológica Libre",
        "welcome": "### 🏛️ ¡Salve!\nSoy tu *grammaticus* digital. Estoy leyendo contigo los versos seleccionados. ¿Qué duda gramatical o mitológica tienes?",
        "input_placeholder": "Ej: ¿Por qué usa el ablativo aquí? / ¿Quién es Eolo?",
        "spinner": "Consultando los oráculos...",
        "cta_btn": "🏛️ Reserva una clase de latín"
    },
    "English": {"sidebar_title": "Settings", "lang_label": "Language:", "nav_label": "📜 Navigation (Verses):", "reset_btn": "Reset", "header": "Aeneid (Book I)", "chat_header": "Consultation", "welcome": "### Salve!", "input_placeholder": "Ask...", "spinner": "...", "cta_btn": "Book Class"},
    "Latine": {"sidebar_title": "Configuratio", "lang_label": "Lingua:", "nav_label": "📜 Navigatio:", "reset_btn": "Iterare", "header": "Aeneis (Liber I)", "chat_header": "Colloquium", "welcome": "### Salve!", "input_placeholder": "Interrogā...", "spinner": "...", "cta_btn": "Schola"},
    "繁體中文 (Taiwan)": {"sidebar_title": "設定", "lang_label": "語言:", "nav_label": "📜 導航 (詩句):", "reset_btn": "重置", "header": "維吉爾：《埃涅阿斯紀》第一卷", "chat_header": "諮詢", "welcome": "### 您好!", "input_placeholder": "詢問...", "spinner": "...", "cta_btn": "預約"}
}

# --- 4. FUNCIONES DE MEMORIA (RAG LIGERO) ---
def buscar_en_base_datos(pregunta_usuario):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL_HOJA_CALCULO, ttl=0)
        df = df.dropna(how="all").fillna("")
        pregunta_usuario = pregunta_usuario.lower().strip()
        for index, row in df.iterrows():
            pregunta_db = str(row.iloc[0]).lower().strip()
            respuesta_db = str(row.iloc[1])
            if not pregunta_db: continue
            if (pregunta_usuario in pregunta_db) or (pregunta_db in pregunta_usuario):
                return respuesta_db
        return None
    except: return None

def guardar_nueva_entrada(pregunta, respuesta):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL_HOJA_CALCULO, ttl=0)
        df = df.dropna(how="all")
        nueva_fila = pd.DataFrame([[pregunta, respuesta]], columns=df.columns)
        df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
        conn.update(spreadsheet=URL_HOJA_CALCULO, data=df_actualizado)
        return True
    except: return False

# --- 5. ESTILOS CSS (CSS PRO) ---
st.markdown("""
    <style>
    /* Estilo para el texto latino: Fuente Serif clásica y espaciado */
    .verse-container {
        background-color: #fcfbf9; /* Color papiro suave */
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #8e44ad;
        height: 600px;
        overflow-y: auto; /* Scroll interno */
    }
    .verse-line { 
        font-family: 'Times New Roman', serif; 
        font-size: 1.2rem; 
        line-height: 1.6; 
        color: #2c3e50; 
        margin-bottom: 4px;
    }
    .verse-number {
        color: #95a5a6;
        font-size: 0.8rem;
        margin-right: 10px;
        user-select: none;
    }
    .main-header { color: #8e44ad; font-weight: bold; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- 6. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    idioma_app = st.selectbox("Language / Idioma / 語言", list(TRADUCCIONES.keys()))
    t = TRADUCCIONES[idioma_app]
    
    st.title(t["sidebar_title"])
    st.divider()
    
    # --- LÓGICA DE PAGINACIÓN ---
    # Cargamos el texto completo
    todos_los_versos = obtener_versos_libro_i()
    total_versos = len(todos_los_versos)
    VERSOS_POR_PAGINA = 30 # Muestra 30 versos por bloque para no saturar
    
    # Slider para seleccionar el rango
    st.markdown(f"**{t['nav_label']}**")
    pagina = st.slider("Selectio", 1, total_versos, 1, step=VERSOS_POR_PAGINA)
    
    inicio = pagina - 1
    fin = min(inicio + VERSOS_POR_PAGINA, total_versos)
    versos_visibles = todos_los_versos[inicio:fin]
    rango_actual = f"Versus {inicio + 1} - {fin}"
    
    st.caption(f"📍 {rango_actual} / {total_versos}")
    
    st.divider()
    if st.button(t["reset_btn"]):
        st.session_state.messages = []
        st.cache_data.clear()
        st.rerun()

# --- 7. CONFIGURACIÓN GEMINI ---
@st.cache_data
def load_prompt(url):
    try:
        r = requests.get(url)
        return r.text if r.status_code == 200 else "Act as an expert Latin Philologist specializing in Virgil."
    except: return "Act as an expert Latin Philologist specializing in Virgil."

PROMPT_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/prompt_maestro.txt"
base_instruction = load_prompt(PROMPT_URL)

# Aquí inyectamos el contexto de los versos que el usuario está mirando
contexto_actual = "\n".join(versos_visibles)
sys_instruction = f"""
{base_instruction}
CONTEXTO ACTUAL DEL USUARIO (El usuario está leyendo estos versos específicos ahora mismo):
---
{contexto_actual}
---
Si el usuario pregunta sobre 'este verso' o 'esta palabra', refiérete a este fragmento.
"""

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite-preview-02-05", system_instruction=sys_instruction)
else:
    st.warning("⚠️ API KEY missing. AI features disabled.")
    model = None

# --- 8. INTERFAZ PRINCIPAL ---
col_txt, col_chat = st.columns([6, 4], gap="medium") # 60% texto, 40% chat

with col_txt:
    st.markdown(f"<h2 class='main-header'>{t['header']} <span style='font-size:0.6em; color:gray'>({rango_actual})</span></h2>", unsafe_allow_html=True)
    
    # Contenedor del texto con scroll
    texto_html = '<div class="verse-container">'
    for i, v in enumerate(versos_visibles):
        num_verso = inicio + i + 1
        # Formato: Número en gris + Verso
        texto_html += f'<div class="verse-line"><span class="verse-number">{num_verso}</span>{v}</div>'
    texto_html += '</div>'
    
    st.markdown(texto_html, unsafe_allow_html=True)

with col_chat:
    st.subheader(t["chat_header"])
    chat_container = st.container(height=600, border=True)

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = [{"role": "assistant", "content": t["welcome"]}]

    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input(t["input_placeholder"]):
        if model is None:
            st.error("No API Key configured")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"): st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    # 1. BUSCAR EN DB
                    respuesta_db = buscar_en_base_datos(prompt)
                    
                    if respuesta_db:
                        st.success("📚 Memoria Externa")
                        st.markdown(respuesta_db)
                        st.session_state.messages.append({"role": "assistant", "content": respuesta_db})
                    else:
                        # 2. CONSULTAR IA
                        try:
                            # Enviamos historial breve
                            history = [{"role": "model" if m["role"]=="assistant" else "user", "parts": [m["content"]]} 
                                       for m in st.session_state.messages[-6:-1]]
                            
                            # Prompt aumentado con idioma
                            full_query = f"[User Language: {idioma_app}] [Intention: Philological/Grammatical Analysis] {prompt}"
                            
                            chat = model.start_chat(history=history)
                            with st.spinner(t["spinner"]):
                                response = chat.send_message(full_query)
                                texto_ia = response.text
                                st.markdown(texto_ia)
                                st.session_state.messages.append({"role": "assistant", "content": texto_ia})
                                
                                # Guardar en segundo plano
                                guardar_nueva_entrada(prompt, texto_ia)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            st.rerun()

    st.divider()
    form_url = "https://docs.google.com/forms/d/tu-form-id"
    st.link_button(t["cta_btn"], form_url, use_container_width=True, type="primary")
