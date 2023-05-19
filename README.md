# Testat: Publisher/Subscriber System"

Florian Glaser, Florian Herkommer, David Felder, Miriam Astor, Steffen Freitag

## Nutzung

Server starten:

```bash
python src/server.py

>>> ======== Running on http://127.0.0.1:8080 ========
>>> (Press CTRL+C to quit)
```

- Ein Topic subscriben:

  ```bash
  python src/client.py --server http://127.0.0.1:8080 --subscribe first_topic second_topic
  ```
  
- Eine Nachricht für Topics schreiben:

  ```bash
  python src/client.py --server http://127.0.0.1:8080 --publish second_topic --message "Hello World Message"
  ```

- ...

## Pytest
Es wird hier nur der Server getestet. Zum testen muss der Server gestartet werden. Es kann zudem immer nur 1 Test ausgeführt werden. Anschließend muss der Server neu gestartet werden.

Folgende Tests stehen zu Verfügung:
- `test_subscribe`
- `test_publish`
- `test_unsubscribe`
- `test_list_topics`
- `test_get_topic_status`

Server starten:
```bash
python src/server.py
```

Beispiel `test_subscribe` ausführen:
```bash
cd src
pytest test.py::test_subscribe
```

## Dokumentation

### Technologien

und deren Funktionalität

### Architekturbeschreibung

### Schnittstelle Server/Client

### Buildprozess Client/Server

### Verwendung Client/Server

### Testumfang und -ergebnisse

