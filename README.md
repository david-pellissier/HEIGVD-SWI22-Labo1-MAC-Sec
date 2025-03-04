# Sécurité des réseaux sans fil

## Laboratoire 802.11 sécurité MAC

__A faire en équipes de deux personnes__


1. [Deauthentication attack](#1-deauthentication-attack)
2. [Fake channel evil tween attack](#2-fake-channel-evil-tween-attack)
3. [SSID Flood attack](#3-ssid-flood-attack)
4. [Probe Request Evil Twin Attack](#4-probe-request-evil-twin-attack)
5. [Détection de clients et réseaux](#5-d%c3%a9tection-de-clients-et-r%c3%a9seaux)
6. [Hidden SSID reveal](#6-hidden-ssid-reveal)
7. [Livrables](#livrables)
8. [Échéance](#%c3%89ch%c3%a9ance)



### Pour cette partie pratique, vous devez être capable de :

*	Détecter si un certain client WiFi se trouve à proximité
*	Obtenir une liste des SSIDs annoncés par les clients WiFi présents

Vous allez devoir faire des recherches sur internet pour apprendre à utiliser Scapy et la suite aircrack pour vos manipulations. __Il est fortement conseillé d'employer une distribution Kali__ (on ne pourra pas assurer le support avec d'autres distributions). __Si vous utilisez une VM, il vous faudra une interface WiFi usb, disponible sur demande__.

Des routers sans-fils sont aussi disponibles sur demande si vous en avez besoin (peut être utile pour l'exercices challenge 6).

__ATTENTION :__ Pour vos manipulations, il pourrait être important de bien fixer le canal lors de vos captures et/ou vos injections (à vous de déterminer si ceci est nécessaire pour les manipulations suivantes ou pas). Une méthode pour fixer le canal a déjà été proposée dans un laboratoire précédent.

## Quelques pistes utiles avant de commencer :

- Si vous devez capturer et injecter du trafic, il faudra configurer votre interface 802.11 en mode monitor.
- Python a un mode interactif très utile pour le développement. Il suffit de l'invoquer avec la commande ```python```. Ensuite, vous pouvez importer Scapy ou tout autre module nécessaire. En fait, vous pouvez même exécuter tout le script fourni en mode interactif !
- Scapy fonctionne aussi en mode interactif en invoquant la commande ```scapy```.  
- Dans le mode interactif, « nom de variable + <enter> » vous retourne le contenu de la variable.
- Pour visualiser en détail une trame avec Scapy en mode interactif, on utilise la fonction ```show()```. Par exemple, si vous chargez votre trame dans une variable nommée ```beacon```, vous pouvez visualiser tous ces champs et ses valeurs avec la commande ```beacon.show()```. Utilisez cette commande pour connaître les champs disponibles et les formats de chaque champ.
- Vous pouvez normalement désactiver la randomisation d'adresses MAC de vos dispositifs. Cela peut être utile pour tester le bon fonctionnement de certains de vos scripts. [Ce lien](https://www.howtogeek.com/722653/how-to-disable-random-wi-fi-mac-address-on-android/) vous propose une manière de le faire pour iOS et Android. 

## Partie 1 - beacons, authenfication

### 1. Deauthentication attack

Une STA ou un AP peuvent envoyer une trame de déauthentification pour mettre fin à une connexion.

Les trames de déauthentification sont des trames de management, donc de type 0, avec un sous-type 12 (0x0c). Voici le format de la trame de déauthentification :

![Trame de déauthentification](images/deauth.png)

Le corps de la trame (Frame body) contient, entre autres, un champ de deux octets appelé "Reason Code". Le but de ce champ est d'informer la raison de la déauthentification. Voici toutes les valeurs possibles pour le Reason Code :

| Code | Explication 802.11                                                                                                                                     |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0    | Reserved                                                                                                                                              |
| 1    | Unspecified reason                                                                                                                                    |
| 2    | Previous authentication no longer valid                                                                                                               |
| 3    | station is leaving (or has left) IBSS or ESS                                                                                                          |
| 4    | Disassociated due to inactivity                                                                                                                       |
| 5    | Disassociated because AP is unable to handle all currently associated stations                                                                        |
| 6    | Class 2 frame received from nonauthenticated station                                                                                                  |
| 7    | Class 3 frame received from nonassociated station                                                                                                     |
| 8    | Disassociated because sending station is leaving (or has left) BSS                                                                                    |
| 9    | Station requesting (re)association is not authenticated with responding station                                                                       |
| 10   | Disassociated because the information in the Power Capability element is unacceptable                                                                 |
| 11   | Disassociated because the information in the Supported Channels element is unacceptable                                                               |
| 12   | Reserved                                                                                                                                              |
| 13   | Invalid information element, i.e., an information element defined in this standard for which the content does not meet the specifications in Clause 7 |
| 14   | Message integrity code (MIC) failure                                                                                                                                              |
| 15   | 4-Way Handshake timeout                                                                                                                                              |
| 16   | Group Key Handshake timeout                                                                                                                                              |
| 17   | Information element in 4-Way Handshake different from (Re)Association Request/Probe Response/Beacon frame                                                                                                                                              |
| 18   | Invalid group cipher                                                                                                                                              |
| 19   | Invalid pairwise cipher                                                                                                                                              |
| 20   | Invalid AKMP                                                                                                                                              |
| 21   | Unsupported RSN information element version                                                                                                                                              |
| 22   | Invalid RSN information element capabilities                                                                                                                                              |
| 23   | IEEE 802.1X authentication failed                                                                                                                                              |
| 24   | Cipher suite rejected because of the security policy                                                                                                                                              |
| 25-31 | Reserved                                                                                                                                              |
| 32 | Disassociated for unspecified, QoS-related reason                                                                                                                                              |
| 33 | Disassociated because QAP lacks sufficient bandwidth for this QSTA                                                                                                                                              |
| 34 | Disassociated because excessive number of frames need to be acknowledged, but are not acknowledged due to AP transmissions and/or poor channel conditions                                                                                                                                              |
| 35 | Disassociated because QSTA is transmitting outside the limits of its TXOPs                                                                                                                                              |
| 36 | Requested from peer QSTA as the QSTA is leaving the QBSS (or resetting)                                                                                                                                              |
| 37 | Requested from peer QSTA as it does not want to use the mechanism                                                                                                                                              |
| 38 | Requested from peer QSTA as the QSTA received frames using the mechanism for which a setup is required                                                                                                                                              |
| 39 | Requested from peer QSTA due to timeout                                                                                                                                              |
| 40 | Peer QSTA does not support the requested cipher suite                                                                                                                                              |
| 46-65535 | Reserved                                                                                                                                              |

a) Utiliser la fonction de déauthentification de la suite aircrack, capturer les échanges et identifier le Reason code et son interpretation.

Adresse ciblée : `c0:ee:fb:e2:4f:1f`
Adresse AP: `dc:a5:f4:60:c2:b0`

Commande pour l'attaque:

```bash
sudo aireplay-ng -0 10 -c c0:ee:fb:e2:4f:1f -a dc:a5:f4:60:c2:b0 wlan0
```



__Question__ : quel code est utilisé par aircrack pour déauthentifier un client 802.11. Quelle est son interpretation ?

Le code n°7 est utilisé par aircrack pour déauthentifier le client. 

L'interprétation de ce code n'est pas très claire car les sources ne disent pas la même chose. L'explication la plus plausible est que ce code indique que le client a reçu des données d'une STA qui n'a pas encore été associée et demande alors une déauthentification.

Sources: 

-   https://support.zyxel.eu/hc/en-us/articles/360009469759-What-is-the-meaning-of-802-11-Deauthentication-Reason-Codes-
-   https://www.rfwireless-world.com/Terminology/WLAN-authentication-deauthentication-frame.html

__Question__ : A l'aide d'un filtre d'affichage, essayer de trouver d'autres trames de déauthentification dans votre capture. Avez-vous en trouvé d'autres ? Si oui, quel code contient-elle et quelle est son interpretation ?

>    Filtre utilisé: wlan.addr == c0:ee:fb:e2:4f:1f 

![image-20220324145732461](images/image-20220324145732461.png)

b) Développer un script en Python/Scapy capable de générer et envoyer des trames de déauthentification. Le script donne le choix entre des Reason codes différents (liste ci-après) et doit pouvoir déduire si le message doit être envoyé à la STA ou à l'AP :

* 1 - Unspecified
* 4 - Disassociated due to inactivity
* 5 - Disassociated because AP is unable to handle all currently associated stations
* 8 - Deauthenticated because sending STA is leaving BSS

Lancer le script ainsi:

```bash
sudo python3 1_deauth.py <MAC STA> <MAC AP> <interface>
```

Le script envoie par défaut 10 trames (changable avec le  paramètre `--count`):

![](images/deauth01.png)

Les options suivantes sont disponibles:

![](images/deauth02.png)



__Question__ : quels codes/raisons justifient l'envoie de la trame à la STA cible et pourquoi ?

-   1: Non spécifié donc peut être envoyé à n'importe qui
-   5: Lorsque l'AP est surchargé il peut demander la déauthentification au client afin de libérer des ressources si le client se connecte à un autre AP du même SSID



__Question__ : quels codes/raisons justifient l'envoie de la trame à l'AP et pourquoi ?

-   1: Non spécifié donc peut être envoyé à n'importe qui
-   4: Si le client désactive automatiquement son WiFi lorsqu'il n'utilise pas le réseau pendant un certain temps
-   8: Lorsque le client a quitté la zone et s'est connecté à un autre AP ayant un meilleur signal



__Question__ : Comment essayer de déauthentifier toutes les STA ?

En indiquant l'adresse de broadcast comme cible de l'attaque: `ff:ff:ff:ff`

__Question__ : Quelle est la différence entre le code 3 et le code 8 de la liste ?

La nuance est dans le mot "Disassociated": 

-   3: le client se déauthentifie uniquement, car il n'y a pas d'autre AP disponible autour de lui et le signal est insuffisant pour garder une connexion
-   8: le client désassocie l'AP pour s'associer à un autre AP plus proche de lui

__Question__ : Expliquer l'effet de cette attaque sur la cible

L'attaque force la cible à se désauthentifier de l'AP, et va immédiatement recommencer le 4-way handshake, qui lorsqu'il est capturé, peut être utilisé dans d'autres attaques. 

### 2. Fake channel evil tween attack
a)	Développer un script en Python/Scapy avec les fonctionnalités suivantes :

* Dresser une liste des SSID disponibles à proximité
* Présenter à l'utilisateur la liste, avec les numéros de canaux et les puissances
* Permettre à l'utilisateur de choisir le réseau à attaquer
* Générer un beacon concurrent annonçant un réseau sur un canal différent se trouvant à 6 canaux de séparation du réseau original

Lancer la commande dans scripts:

```bash
sudo python3 2_fakeChannelEvilTwinAttack.py <interface>
```

Pendant les dix premières secondes, le temps d'itérer sur toutes les channels, le script scanne les SSID et en fait une liste. A la fin de du scan, il est demandé à l'utilisateur d'entrer le BSSID à attaquer:

![](images/fake01.png)

Ensuite, un thread commence pour faire un evil twin à 6 channels d'écart:

![](images/fake02.png)

Finalement, le main vérifie toutes les dix secondes si le twin est sur la nouvelle channel (avec l'adresse MAC de l'utilisateur):

![](images/fake03.png)

__Question__ : Expliquer l'effet de cette attaque sur la cible
	

L'objectif est de faire croire que la victime va se connecter à son access point habituel
	On trouve un wifi
	On crée, sur un autre canal, le même wifi
	La victime va nous envoyer ses données au lieu du vrai access point


### 3. SSID flood attack

Développer un script en Python/Scapy capable d'inonder la salle avec des SSID dont le nom correspond à une liste contenue dans un fichier text fournit par un utilisateur. Si l'utilisateur ne possède pas une liste, il peut spécifier le nombre d'AP à générer. Dans ce cas, les SSID seront générés de manière aléatoire.

Lancer dans script:

```bash
sudo ./3_ssidFlood.py <file or count> <interface>
```

Dans le 1er argument on peut soit donner un entier qui générera le nombre donné de SSID random, ou un fichier comprenant des SSID séparés par des retours à la ligne. 

À noter que le script semble ne fonctionner qu'en mode monitor

Une fois le script lancé, ce dernier lance des trame Beacon pour les fake SSID:

![](images/ssid01.png)

Résultat: 

Une fois le signal d'arrêt envoyé (Ctrl + C), le script arrête proprement les threads des fake AP:

![](images/ssid02.png)

Preuve de fonctionnement: 

![2022-03-31_23-44](images/2022-03-31_23-44.png)


## Partie 2 - probes

## Introduction

L’une des informations de plus intéressantes et utiles que l’on peut obtenir à partir d’un client sans fils de manière entièrement passive (et en clair) se trouve dans la trame ``Probe Request`` :

![Probe Request et Probe Response](images/probes.png)

Dans ce type de trame, utilisée par les clients pour la recherche active de réseaux, on peut retrouver :

* L’adresse physique (MAC) du client (sauf pour dispositifs iOS 8 ou plus récents et des versions plus récentes d'Android). 
	* Utilisant l’adresse physique, on peut faire une hypothèse sur le constructeur du dispositif sans fils utilisé par la cible.
	* Elle peut aussi être utilisée pour identifier la présence de ce même dispositif à des différents endroits géographiques où l’on fait des captures, même si le client ne se connecte pas à un réseau sans fils.
* Des noms de réseaux (SSID) recherchés par le client.
	* Un Probe Request peut être utilisé pour « tracer » les pas d’un client. Si une trame Probe Request annonce le nom du réseau d’un hôtel en particulier, par exemple, ceci est une bonne indication que le client s’est déjà connecté au dit réseau. 
	* Un Probe Request peut être utilisé pour proposer un réseau « evil twin » à la cible.

Il peut être utile, pour des raisons entièrement légitimes et justifiables, de détecter si certains utilisateurs se trouvent dans les parages. Pensez, par exemple, au cas d'un incendie dans un bâtiment. On pourrait dresser une liste des dispositifs et la contraster avec les personnes qui ont déjà quitté le lieu.

A des fins plus discutables du point de vue éthique, la détection de client s'utilise également pour la recherche de marketing. Aux Etats Unis, par exemple, on "sniff" dans les couloirs de centres commerciaux pour détecter quelles vitrines attirent plus de visiteurs, et quelle marque de téléphone ils utilisent. Ce service, interconnecté en réseau, peut aussi déterminer si un client visite plusieurs centres commerciaux un même jour ou sur un certain intervalle de temps.

### 4. Probe Request Evil Twin Attack

Nous allons nous intéresser dans cet exercice à la création d'un evil twin pour viser une cible que l'on découvre dynamiquement utilisant des probes.

Développer un script en Python/Scapy capable de detecter une STA cherchant un SSID particulier - proposer un evil twin si le SSID est trouvé (i.e. McDonalds, Starbucks, etc.).

Pour la détection du SSID, vous devez utiliser Scapy. Pour proposer un evil twin, vous pouvez très probablement réutiliser du code des exercices précédents ou vous servir d'un outil existant.

Dans scripts, lancez:

```bash
sudo python3 4_probeRequestEvilTwinAttack.py <interface>
```

Le script vous salue avec votre adresse MAC. Et vous demande le SSID à trouver:

![](images/probe01.png)

Le script va itérer pendant 10 secondes sur toutes les channels pour trouver le SSID. Si le SSID n'est pas trouvé, le script scanne à nouveau pendant 10 secondes. L'opération est répétée tant que le SSID n'a pas été trouvé. Quand le SSID est trouvé, son adresse MAC est affichée et il est demander à l'utilisateur sur quel channel il veut faire le Twin de ce ssid.

![](images/probe02.png)

Pour vérifier que le clone fonctionne, il est vérifié que le SSID apparaisse sur la channel choisie avec l'adresse MAC de l'utilisateur:

![](images/probe04.png)



__Question__ : comment ça se fait que ces trames puissent être lues par tout le monde ? Ne serait-il pas plus judicieux de les chiffrer ?

Les trames ne sont pas chiffrées, car il faut pouvoir partager un secret avec la STA et l'AP
Si plusieurs AP partagent le réseau, il faudrait que la clé de chiffrement partagée entre une AP et une STA, soit partagée avec tous les AP de ce réseau. Cela est compliqué.




__Question__ : pourquoi les dispositifs iOS et Android récents ne peuvent-ils plus être tracés avec cette méthode ?

Car les adresses MAC sont randomisées maintenant:
https://www.extremenetworks.com/extreme-networks-blog/wi-fi-mac-randomization-privacy-and-collateral-damage/

### 5. Détection de clients et réseaux

a) Développer un script en Python/Scapy capable de lister toutes les STA qui cherchent activement un SSID donné

Le script est plutôt simple, il prend en argument le SSID à chercher et l'interface. Puis analyse chaque Probe request, et si le SSID est celui cherché, l'adresse de la STA est affichée

![image-20220331234658072](images/image-20220331234658072.png)

b) Développer un script en Python/Scapy capable de générer une liste d'AP visibles dans la salle et de STA détectés et déterminer quelle STA est associée à quel AP. Par exemple :

STAs &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; APs

B8:17:C2:EB:8F:8F &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 08:EC:F5:28:1A:EF

9C:F3:87:34:3C:CB &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 00:6B:F1:50:48:3A

00:0E:35:C8:B8:66 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 08:EC:F5:28:1A:EF



Après moultes problèmes nous avons pu faire un script qui fonctionne mais n'est pas parfait. Nous nous sommes basés sur la capture des paquets "QoS null" qui sont envoyés fréquemment depuis le client vers l'AP.

Fonctionnement du script:

![image-20220331234230783](images/image-20220331234230783.png)


### 6. Hidden SSID reveal (exercices challenge optionnel - donne droit à un bonus)

Développer un script en Python/Scapy capable de reveler le SSID correspondant à un réseau configuré comme étant "invisible".

__Question__ : expliquer en quelques mots la solution que vous avez trouvée pour ce problème ?

Nous n'avons pas eu le temps d'écrire un script, mais nous avons quand même fait quelques recherches à ce propos:

Les AP qui cachent leurs SSID ne font qu'envoyer des Beacons qui ont un champ 'SSID' vide. Cependant, tous les autres échanges de données enrte un client et l'AP "invisible" ne cachent pas le SSID et on peut alors connaître le nom du réseau même s'il n'est pas annoncé par l'AP.

Le fonctionnement d'un tel script serait le suivant:

>   Un dictionnaire qui prend pour clé une adresse MAC et comme valeur un SSID
>
>   Pour chaque paquet:
>
>   1.  Si c'est un paquet Beacon avec SSID caché et n'est pas encore gardée en mémoire:
>       1.   garder en mémoire l'adresse MAC de l'AP
>   2.  Si c'est un paquet destiné à l'une des adresses MAC retenues __et__ n'a pas encore de SSID révélée, __et__ que le type du paquet donne l'info sur le SSID (p.ex Authentication):
>       1.  Afficher le SSID et le MAC de l'AP
>       2.  Associer le SSID avec sa MAC address dans le dictionnaire

Quelques pistes utiles: 

-   https://netpacket.net/2020/08/finding-hidden-ssids/
-   https://www.7signal.com/news/blog/controlling-beacons-boosts-wi-fi-performance

## Livrables

Un fork du repo original . Puis, un Pull Request contenant :

- Script de Deauthentication de clients 802.11 __abondamment commenté/documenté__

- Script fake chanel __abondamment commenté/documenté__

- Script SSID flood __abondamment commenté/documenté__

- Script evil twin __abondamment commenté/documenté__

- Scripts détection STA et AP __abondamment commenté/documenté__

- Script SSID reveal __abondamment commenté/documenté__


- Captures d'écran du fonctionnement de chaque script

-	Réponses aux éventuelles questions posées dans la donnée. Vous répondez aux questions dans votre ```README.md``` ou dans un pdf séparé

-	Envoyer le hash du commit et votre username GitHub par email au professeur et à l'assistant


## Échéance

Le 31 mars 2022 à 23h59
