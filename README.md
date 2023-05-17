# Testat: Publisher/Subscriber System"

Florian Glaser, Florian Herkommer, David Felder, Miriam Astor, Steffen Freitag

## Nutzung

Server starten:

```bash
python server.py

>>> ======== Running on http://127.0.0.1:8080 ========
>>> (Press CTRL+C to quit)
```

- Ein Topic subscriben:

  ```bash
  python client.py --server http://127.0.0.1:8080 --subscribe first_topic second_topic
  ```
  
- Eine Nachricht für Topics schreiben:

  ```bash
  python client.py --server http://127.0.0.1:8080 --publish second_topic --message "Hello World Message"
  ```

- ...

## Dokumentation

### Technologien

und deren Funktionalität

### Architekturbeschreibung

### Schnittstelle Server/Client

### Buildprozess Client/Server

### Verwendung Client/Server

### Testumfang und -ergebnisse

