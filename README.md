# tsoha-opetussovellus

Sovelluksen tavoitteena on sama toiminnallisuus kuin kurssin aiheista "opetussovellus" -aiheen ominaisuudet. 
Tarkalleen ottaen:
-  Käyttäjätunnusten luonti ja kirjautuminen
-  Erilaisia käyttäjätyyppejä; oppilailla ja opettajilla on eri toiminnallisuus
    - Opiskelijat voivat liittyä kursseille ja tehdä tehtäviä, sekä tarkastelemaan niiden tilannetta.
    - Opettajat voivat luoda kursseja, luoda tehtäviä niihin, tarkastelemaan tehtävien tiloja ja poistamaan kursseja.

# Tämänhetkinen toiminnallisuus
Tällä hetkellä ohjelmalla pystyy:
- Luoda käyttäjätilin
- Kirjautua sisään
- Opettajat voivat nähdä kaikki kurssit, niiden opettajan ja kuinka monta opiskelijaa kurssilla on
- Opettajat voivat luoda kursseja sekä poistaa niitä
- Opettajat voivat lisätä kurssille tehtäviä (tekstitehtävä tai monivalintatehtävä) sekä nähdä, ketkä opiskelijat ovat tehneet mitkä tehtävät
- Opiskelijat voivat myös nähdä kaikki kurssit, liittyä niihin ja poistua niistä
- Opiskelijat voivat tehdä tehtäviä ja saada palautteen, onko se oikein vai väärin

# Ohjelman käynnistys
Kloonaa ensin tämä repositorio:
```
$ git clone https://github.com/candyliaa/tsoha-opetussovellus
``` 
Projektissa käytetään [Docker](https://www.docker.com/) -ohjelmaa. Asenna se omalle tietokoneellesi [täältä](https://docs.docker.com/get-docker/).
Opas Dockerin käyttöön Python web-applikaation kanssa löytyy [täältä](https://docs.docker.com/compose/gettingstarted/).

Muuta `compose.yaml.example` -tiedoston nimeksi `compose.yaml` ja sijoita `SECRET_KEY` -kenttään salainen avain. Voit luoda salaisen avaimen seuraavasti:
```
$ python3
>>> import secrets
>>> secrets.token_hex(16)
```
Docker huolehtii projektissa käytetyistä paketeista ja tietokannasta. Voit käynnistää ohjelman seuraavalla komennolla:
```
$ docker compose up
```
Voit sen jälkeen avata ohjelman osoitteessa http://localhost:8000 .

Jos haluat nähdä, mitä paketteja ohjelmassa käytetään, ne löytyy `requirements.txt` -tiedostosta hakemistosta `app`.
`db` -hakemistossa olevassa `test_data.sql` -tiedostossa on dataa, jonka avulla ohjelmaa voi testata. Sieltä löytyy käyttäjätilien tiedot.
Tietokannan rakennetta voi tarkastella `schema.sql` -tiedostossa, joka on hakemistossa `db`.
