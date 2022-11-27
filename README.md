# Studoši dump

## Sadržaj repozitorija

- [resursi](./assets): ovdje se ne nalazi ništa, ali se mogu raspakirati slike kako bi
  se upotpunile rasprave
- [rasprave](./discussions): ovdje se nalaze postovi
  - [postovi u JSONu](./discussions/json/)
  - [⚠️ postovi u Markdownu ⚠️](./discussions/markdown/)
- [razno](./misc): ovdje se nalaze:
  - [ankete](./misc/polls.json)
  - [lista korisnika](./misc/users.csv)
- [⚠️ generacija Markdowna ⚠️](./markdown_setup.py): skripta za generaciju Markdown pregleda rasprava
- [⚠️ iscrtavanje Markdowna ⚠️](./markdown_render.py): skripta za iscrtavanje Markdowna
- [⚠️ popis ovisnosti ⚠️](./requirements.txt): potrebno samo za iscrtavanje Markdowna

## Resursi

Resursi se nalaze na [sljedećoj poveznici](https://drive.google.com/drive/folders/1Ak_A_qj418HXON_PGdX5Uj3XVOlK9oKy?usp=sharing). Potrebno ih je raspakirati unutar `assets` direktorija.

Nakon toga, moguće je pokrenuti [⚠️ `markdown_setup.py` ⚠️](./markdown_setup.py), koja će za
svaku raspravu generirati Markdown datoteke podijeljene po 10 postova, uz slike.

Konačno, pokretanjem [⚠️ `markdown_render.py` ⚠️](./markdown_render.py) će se preko
generiranih Markdowna iscrtati objave. Za ovo će biti potrebno instalirati paket koji
renderira Markdown, a nalazi se u [⚠️ `requirements.txt` ⚠️](./requirements.txt).
