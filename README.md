# tsoha-opetussovellus

Sovelluksen tavoitteena on sama toiminnallisuus kuin kurssin aiheista "opetussovellus" -aiheen ominaisuudet. 
Tarkalleen ottaen:
-  Käyttäjätunnusten luonti ja kirjautuminen
-  Erilaisia käyttäjätyyppejä; oppilailla ja opettajilla on eri toiminnallisuus
    - Opiskelijat voivat liittyä kursseille ja tehdä tehtäviä, sekä tarkastelemaan niiden tilannetta - opiskelijat voivat myös nähdä suoritetut kurssit ja opintopistetilanteen
    - Opettajat voivat luoda kursseja, muokata niitä ja poistaa niitä, sekä tarkastelemaan tilastoja

# Ohjelman käynnistys
Kloonaa ensin tämä repositorio:
```
$ git clone https://github.com/candyliaa/tsoha-opetussovellus
``` 
Projektissa käytetään [Docker](https://www.docker.com/) -ohjelmaa. 
Opas Dockerin käyttöön Python web-applikaation kanssa löytyy [täältä](https://docs.docker.com/compose/gettingstarted/).

Muuta `compose.yaml.example` -tiedoston nimeksi `compose.yaml` ja sijoita SECRET_KEY kenttään salainen avain. Voit luoda salaisen avaimen seuraavasti:
```
$ python3
>>> import secrets
>>> secrets.token_hex(16)
```
Docker huolehtii projektissa käytetyistä paketeista ja tietokannasta. Sinun täytyy vain käyttää komentoa
`docker compose up`
käynnistääksesi ohjelman. Voit sen jälkeen avata ohjelman osoitteessa http://localhost:8000 .

Jos haluat nähdä, mitä paketteja ohjelmassa käytetään, ne löytyy `requirements.txt` -tiedostosta hakemistosta `app`.
`db` -hakemistossa olevassa `test_data.sql` -tiedostossa on dataa, jonka avulla ohjelmaa voi testata. Sieltä löytyy käyttäjätilien tiedot.
