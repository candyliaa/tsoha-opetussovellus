# tsoha-opetussovellus

Sovelluksen tavoitteena on sama toiminnallisuus kuin kurssin aiheista "opetussovellus" -aiheen ominaisuudet. 
Tarkalleen ottaen:
-  Käyttäjätunnusten luonti ja kirjautuminen
-  Erilaisia käyttäjätyyppejä; oppilailla ja opettajilla on eri toiminnallisuus
    - Opiskelijat voivat liittyä kursseille ja tehdä tehtäviä, sekä tarkastelemaan niiden tilannetta - opiskelijat voivat myös nähdä suoritetut kurssit ja opintopistetilanteen
    - Opettajat voivat luoda kursseja, muokata niitä ja poistaa niitä, sekä tarkastelemaan tilastoja

# Ohjelman käynnistys
Ohjelma on kirjoitettu Python -kielellä, käyttämällä tietokantana PostgreSQL -tietokantaa. Käytössä on Windows 10 -laite, jolla on WSL2 -asennus. 
Paketteja on hallittu Conda -ohjelman avulla: https://docs.conda.io/en/latest/

Muut samankaltaiset pakettienhallintaohjelmat käyvät myös, mutta ohjeet ovat tehty olettaen, että käytössä on Conda.

Kloonaa ensin tämä repositorio:
```
$ git clone https://github.com/candyliaa/tsoha-opetussovellus
``` 
ja luo virtuaaliympäristö Condan avulla:
```
$ conda create --name nimi
```
Aktivoi virtuaaliympäristö:
```
$ conda activate nimi
```
Projektissa on käytetty seuraavia kirjastoja:

https://flask.palletsprojects.com/en/3.0.x/installation/ (`flask` ja `flask-sqlalchemy`)

https://pypi.org/project/psycopg2/ (`psycopg2`)

https://pypi.org/project/python-dotenv/ (`python-dotenv`)

Voit asentaa kirjastot seuraavalla komennolla:
```
$ conda install package
```
Määritä tietokannan skeema seuraavalla komennolla:
```
$ psql < schema.sql
```
Ohjelman voi nyt käynnistää tällä komennolla:
```
flask run
```
