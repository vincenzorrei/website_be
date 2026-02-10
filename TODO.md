# TODO - Miglioramenti futuri (complessita' media/alta)

- [ ] **Summary memory**: riassunto dei turni vecchi con LLM per comprimere la finestra di contesto
- [ ] **Agent con tools**: integrazione MCP o LangChain tools per azioni complesse
- [ ] **Streaming migliorato**: streaming diretto chunk-by-chunk senza buffer completo
- [ ] **Redis per memoria**: sostituire dict in-memory con Redis per sessioni persistenti in produzione
- [ ] **PDF/Markdown/URL loaders**: supporto ingestion multi-formato (PDF, Markdown, URL scraping)
- [ ] **Semantic chunking**: chunking basato su significato semantico invece di caratteri fissi
- [ ] **LangSmith tracing**: integrazione tracing per debug e monitoring delle chain
