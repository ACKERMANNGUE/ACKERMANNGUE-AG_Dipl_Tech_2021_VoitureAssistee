## Journal de bord du travail de diplôme 2021
### 19.04.2021
* J'ai copié le disque dur de M. Bauduccio car le mien causait des soucis
* M. Moreno, M. Huber et moi avons eu un entretien avec M. Bonvin pour discuter des appréciations du stage
* J'ai mis en place mon poste (Création du repository, installation des programmes nécessaires tel que : VS Code, Github Desktop, Suite Office, etc...)
* J'ai lu le chapitre 6 du magpi nommé "Le guide officiel du débutant Raspberry Pi" conseillé par M. Bonvin
* J'ai commencé à m'intéresser à l'utilisation du Remote GPIO pour établir une connexion entre mon Raspberry Pi 4 et celui de M. Moreno
  * Nous avons d'abord mis nos 2 Raspberry Pi sur le même réseau, ensuite nous nous sommes assurés que l'interface `Remote GPIO` était bien active des 2 côtés et nous avons vérifié que `pigpio` était bien installé, puis pour terminer nous avons mis en place le code disponible dans ce [PDF](https://magpi.raspberrypi.org/issues/60) à la page 61 sur le Raspberry Pi de M. Moreno. Avant d'exécuter le programme, nous avons tout deux exécuter la commande suivante dans un terminal `sudo pigpiod`
  * De son côté nous avons utilisé un bouton pressoir et du miens une LED
  * ![breadboard de M. Moreno](./images/breadboard_moreno.jpeg "breadboard de M. Moreno")
    * Le bouton est connecté au GPIO 2, donc la pin 3
  * ![breadboard de M. Ackermann](./images/breadboard_ackermann.jpeg "breadboard de M. Ackermann")
    * La led est connectée au GPIO 17, donc la pin 11
  * Le code disponible sur la machine de M. Moreno va attendre que le bouton soit pressé, une fois ceci fait, la LED connecté en remote (liée à mon Raspberry Pi) se vera allumée.
* J'ai commencé mes recherches sur l'échange d'informations par bluetooth entre 2 Raspberry Pi 4
  * J'ai tenté de mettre en place le code disponible sur ce [repos](https://gist.github.com/keithweaver/3d5dbf38074cee4250c7d9807510c7c3) mais j'avais l'erreur suivante `ModuleNotFoundError: No module named 'bluetooth'`, pourtant j'avais déjà le bluetooth d'installé ainsi que blueman. En faisant des recherches je suis tombé sur cette commande `sudo apt-get install bluetooth libbluetooth-dev && sudo python3 -m pip install pybluez`. Depuis l'installation des 2 commandes je n'ai plus d'erreurs d'import.
#### Liens consultés
##### Remote GPIO
* https://www.instructables.com/Remote-control-Raspberry-PI-GPIO-pins-over-the-int/
* https://www.instructables.com/Raspberry-Pi-Remote-GPIO/
* https://magpi.raspberrypi.org/articles/remote-control-gpio-raspberry-pi-gpio-zero
* https://magpi.raspberrypi.org/issues/60
##### Échange d'informations par bluetooth entre 2 Raspberry Pi 4
* https://technologisttips.com/raspberry-pi-bluetooth/
* https://bluedot.readthedocs.io/en/latest/pairpipi.html
* https://gist.github.com/keithweaver/3d5dbf38074cee4250c7d9807510c7c3
* https://www.stuffaboutcode.com/2017/07/python-bluetooth-rfcomm-client-server.html
* https://bluedot.readthedocs.io/en/latest/pairpipi.html
* https://stackoverflow.com/questions/23985163/python3-error-no-module-named-bluetooth-on-linux-mint#23985374

### 20.04.2021
* M. Moreno et moi avons continué l'échange d'informations par bluetooth entre nos 2 Raspberry Pi 4
  * De mon côté, j'ai utilisé les fonctions suivantes :
    * `lookUpNearbyBluetoothDevices`, va lancer un scan bluetooth pour découvrir les appareils alentours. Pour chaque appareil trouvés, ils vont être affichés dans la console, si l'un de ces appareils est nommé `morenoPi42` alors son adresse mac se voit être retournée pour être utilisée en paramètre par la fonction ci-dessous.
    * `sendMessageTo` va se connecter à un appareil à l'aide de son adresse mac et d'un port désigné (le port 1 dans notre cas) pour ensuite lui envoyé une information et fermner la connexion.
* Du côté de M. Moreno, il a utilisé la méthode `receiveMessage` qui va écouter sur le port spécifié (dans notre cas, il s'agit toujours du port 1), qui va ensuite accepter la connexion entrante jusqu'à 1024 bytes, puis affiche dans la console les données reçues, une fois cela fait, elle va fermer les sockets de connexion.
![Scan bluetooth des environs](./images/rsp_scan_bluetooth.png "Scan bluetooth des environs")
![Transfère de données entre les 2 Raspberry Pi 4](./images/rsp_send_data_to_another_rsp.png "Transfère de données entre les 2 Raspberry Pi 4")
* Avec M. Moreno, nous avons modifié le programme pour en faire un t'chat par bluetooth. Pour lancer le programme, il faut utiliser la commande suivante en remplaçant le _XXXX_ par le nom d'hôte de l'appareil bluetooth : `python3 bluetooth_data_transfer.py XXXX`
  * En premier temps nous avons pensé regrouper l'ouverture des sockets dans une fonction d'initialisation afin d'avoir une trace sur les sockets pour pouvoir les fermer lorsque cela est voulu.
    * Nous avons une erreur nous indiquant ceci `_bluetooth.error: (111, 'Connection refused')`, cela nous a fait comprendre que pour s'envoyer des informations, il faut que l'un écoute pendant que l'autre parle et réciproquement dans l'autre sens.
    * Nous avons mis en place une boucle while qui tourne constamment. Dans cette boucle, il y a des if qui vérifient le mode actuel.
      * 0 veut dire que nous sommes en attente d'un message
      * 1 veut dire que nous allons envoyé un message

![T'chat en bluetooth](./images/tchat.png "T'chat en bluetooth")
1. Affiche le nom d'hôte et l'adresse mac de l'appareil connecté
2. Espace de saisie de message à envoyer
3. Connexion réussie à l'appareil (adresse mac, port)
4. Réception du message
5. Espace de saisie de message à envoyer, utilisant une commande personnalisée pour quitter le programme

* J'ai commencé mes recherches sur le `Technic Hub`.

#### Liens consultés
##### Échange d'informations par bluetooth entre 2 Raspberry Pi 4
* https://pybluez.readthedocs.io/en/latest/api/bluetooth_socket.html
##### Sockets
* https://docs.python.org/3/library/socket.html
##### Récupération de saisie utilisateur
* https://pythonprogramminglanguage.com/user-input-python/
##### Récupération de paramètres en ligne de commande Python
* https://www.pythonforbeginners.com/system/python-sys-argv
##### Bluetooth LEGO
* https://lego.github.io/lego-ble-wireless-protocol-docs/
* https://github.com/hoharald/leguno-remote

### 21.04.2021
* J'ai commencé la journée par lire [cet article sur le bluetooth](https://www.novelbits.io/deep-dive-ble-packets-events/) pour tenter d'approfondir mes connaissances afin de régler le problème de connexion entre le Raspberry Pi et le `Technic Hub`. Après avoir lu l'article, j'ai tenté de relancer le code d'exemple disponible sur le repos [Bricknil](https://github.com/virantha/bricknil), malheureusement j'avais toujours la même erreur. Je me suis dit que j'allais tenté de créer un script python qui ne fait que se connecter pour l'instant pour pouvoir ensuite tenté d'envoyer des ordres par bluetooth.
  * J'ai commencé par essayer de lire dans [cette documentation](https://lego.github.io/lego-ble-wireless-protocol-docs/index.html#port-information-request) et de comprendre comment je pouvais envoyer des messages que le `Technic Hub` pourrait comprendre. J'ai donc en un premier temps cherché à comprendre si c'était à moi d'envoyé le premier message et sur quel port ou de faire l'inverse, c'est-à-dire moi écouter un port particulier car à chaque fois que depuis l'interface graphique ou par commande dans le terminal, quand je tente de me connecter au `Technic Hub`, j'ai toujours cette erreur ci : `Failed to pair: org.bluez.Error.AuthenticationFailed`.
  * La première chose que j'ai constaté, c'est que des fois après avoir beaucoup tenté d'utiliser le bluetooth de redémarrer le Raspberry Pi car il a de la peine à capter les appareils alentours, tandis qu'une fois redémarré, si l'on utilise `bluetoothctl`, qu'on active le scan avec `scan on`, on peut voir les informations suivantes :
```:
[NEW] Device 90:84:2B:50:36:43 Technic Hub
[CHG] Device 90:84:2B:50:36:43 RSSI: -58
[CHG] Device 90:84:2B:50:36:43 TxPower: 0
[CHG] Device 90:84:2B:50:36:43 ManufacturerData Key: 0x0397
[CHG] Device 90:84:2B:50:36:43 ManufacturerData Value: 
  00 80 06 00 61 00                                ....a. 
```
  * RSSI (Received Signal Strength Indicator) représente la mesure du niveau de la puissance au niveau du récepteur. Il est mesuré en  dBm, sur une échelle logarithmique et étant négatif. Plus le nombre est négatif, plus le dispositif est éloigné. Par exemple, une valeur de -20 à -30 dBm indique que le dispositif est proche, tandis qu'une valeur de -120 indique que le dispositif est proche de la limite de détection.
  * TxPower représente la puissance du signal. Pour un émetteur Bluetooth, 0 dBm (décibel-milliwatt) est le niveau de puissance standard
  * ManufacturerData Key: 0x0397 est le code de LEGO System A/S
  * ManufacturerData Value: 00 80 06 00 61 00
    1. Longueur des données (0x09)
    2. Le nom du type de données (0xFF)
    3. L'ID du fabricant (0x0397)
    4. L'état du bouton (entre 0x00 et 0x01)
    5. Le type de système et le numéro de l'appareil (entre 0x00 et 0xFF)
    6. Les capacités de l'appareil  (entre 0x01 et 0xFF)
    7. L'id du précédent réseau (entre 0x00 et 0xFF)
    8. Le status actuel (entre 0x00 et 0xFF)
* En continuant mes recherches, je me suis demandé s'il n'était pas une bonne idée de tester petit à petit ce que propose le code de Bricknil. Le premier élément que je voulais tester était le `bleak` car j'avais vu lorsque je lançais le code de Bricknil qu'il y avait un message contenant le nom de ce module. Pour installer `bleak`, `pygatt` et `bluepy` j'ai utilisé cette commande : `sudo pip3 install pygatt && pip3 install gatt && pip3 install gattlib && pip3 install bluepy && pip3 install bleak`. Une fois cela fait, j'ai donc été sur [le repos officiel](https://github.com/hbldh/bleak) pour exécuter le code présent. Le premier code nous montre la méthode `discover` tandis que le second nous montre une manière de s'appareiller.
  * La première chose que j'ai faite c'est de tester la connexion. Pour ce faire, j'ai testé la méthode `discover` disponible grâce à `BleakScanner`. J'ai pu voir apparaître le `Technic Hub` dans la liste des appareils détectés. Pour tenter de me "connecter", j'ai utilisé l'adresse mac tel que : `90:84:2B:50:36:43` ainsi que le `Characteristic UUID` tel que : `00001624-1212-EFDE-1623-785FEABCD123` qui va ensuite retourner le numéro de modèle. La led sur le `Technic Hub` devient bleue lorsque je lance le programme et que la méthode `read_gatt_char` est exécutée. Cette méthode retourne un array de byte, dans mon cas voici ce qu'elle me retourne `\x05\x00\x04\x03\x00.\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00`, autrement écrit : `50430460016000160000000`.
   
#### Liens consultés
##### Bluetooth
 * https://www.novelbits.io/deep-dive-ble-packets-events/
 * https://punchthrough.com/crash-course-in-2m-bluetooth-low-energy-phy/
 * https://github.com/karulis/pybluez
 * https://www.bluetoothle.wiki/tx_power
 * https://www.bluetoothle.wiki/rssi?s[]=rssi
 * https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
 * https://lego.github.io/lego-ble-wireless-protocol-docs/index.html
 * https://bleak.readthedocs.io/en/latest/usage.html
 * https://github.com/hbldh/bleak
 * https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt
##### Repos Bricknil
* https://github.com/virantha/bricknil

##### Date avec python
* https://www.tutorialspoint.com/How-to-print-current-date-and-time-using-Python

### 22.04.2021
#### Liens consultés
##### ----
##### ----

### 23.04.2021
#### Liens consultés
##### ----
##### ----