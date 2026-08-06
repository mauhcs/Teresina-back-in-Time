# Foro de Teresina — Ordem por Semana do Ano

Reordenação pessoal e não oficial do feed do podcast *Foro de Teresina*.
O `feed.xml` sempre contém apenas os episódios da **semana atual do
calendário ISO** — todo episódio histórico originalmente publicado nessa
mesma semana ao longo de todos os anos (2018–2026), do ano mais antigo
para o mais recente — e é trocado automaticamente pelo lote da semana
seguinte.

Nenhum áudio é hospedado novamente aqui. O enclosure de cada episódio
aponta para a URL original do MP3, já hospedada pela publicadora
(Megaphone/Spreaker); este repositório só guarda os arquivos de índice
reordenados (RSS/XML) e os scripts que os geram.

## Arquivos

- `episodes.json` — metadados (título, data de publicação original,
  semana ISO, duração, URL do enclosure) dos 535 episódios, extraídos do
  feed oficial (`https://feeds.megaphone.fm/NPP2619427256`).
- `build_weeks.py` — gera um arquivo de feed autocontido para cada semana
  ISO (`weeks/week-01.xml` … `weeks/week-52.xml`) a partir de
  `episodes.json`. Só precisa ser executado de novo quando novos
  episódios forem adicionados ao feed de origem.
- `weeks/week-NN.xml` — os 52 arquivos de feed pré-gerados, um por semana
  do calendário.
- `sync_week.py` — copia o `weeks/week-NN.xml` correspondente à semana
  ISO *atual, no mundo real* para `feed.xml`. É isso que efetivamente
  faz o rodízio do feed ativo.
- `feed.xml` — o feed ativo. **Assine este** no seu app de podcast.
  Contém sempre só os episódios da semana atual.
- `.github/workflows/update-feed.yml` — roda o `sync_week.py`
  diariamente, no cronograma do próprio GitHub, e envia (push) o
  `feed.xml` se a semana tiver mudado. Não precisa de segredos/tokens —
  usa o `GITHUB_TOKEN` embutido do repositório. Requer que em
  Settings → Actions → General → Workflow permissions esteja marcado
  "Read and write permissions".

## Regenerando

Se o podcast de origem publicar novos episódios e você quiser
incorporá-los:

```
curl -s "https://feeds.megaphone.fm/NPP2619427256" -o feed_source.xml
# reextraia o episodes.json a partir do feed_source.xml (ver histórico do projeto),
python3 build_weeks.py   # reconstrói os 52 arquivos semanais
python3 sync_week.py     # atualiza o feed.xml para a semana atual
```

O rodízio do dia a dia já é feito automaticamente pelo workflow do
Actions — você só precisa rodar o `build_weeks.py` quando a lista de
episódios de origem mudar.
