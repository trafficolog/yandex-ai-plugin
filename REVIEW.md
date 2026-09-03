# Ревью проекта — yandex-ai-plugins-skills

**Дата:** 2026-09-03 · **Ревьюер:** Arena Agent Mode · **Базовый коммит:** `a93e1dc` (`fix: harden OPUS 1.1.3 release runtime`, main)

Комплексное независимое ревью: архитектура, Python-код, тесты, документация, CI и release-инфраструктура. Проверка выполнялась на свежем клоне `main`; live-вызовы Yandex API и LLM-эвалюации не выполнялись (см. §7 «Ограничения»).

---

## 1. Резюме

**Общая оценка: 8.5/10 — проект в зрелом, production-качественном состоянии.**

Репозиторий — редкий пример дисциплинированного маркетплейса AI-плагинов: контрактная трассировка (skills ↔ helpers ↔ tests ↔ references), четырёхсторонняя синхронизация версий (2 marketplace + 2 manifest + README + CHANGELOG), enforcement cross-service границ на уровне валидатора и CI, продуманная evidence-семантика (`OBSERVED/DERIVED/HYPOTHESIS/METHODOLOGY`) и safety-lifecycle `read → analyze → preview → approval → write → verify`, реально реализованный в коде, а не только в документации.

Критических проблем **нет**. Найдено несколько проблем зрелости в CI/release-инфраструктуре и DX (P1–P2) и ряд улучшений гигиены (P3). Всё воспроизводимо и локализовано.

| # | Находка | Приоритет | Категория | Effort |
|---|---|---|---|---|
| F-1 | CI `py_compile` пропускает Phase 7 скрипты | **P1** | CI | ~15 мин |
| F-2 | Разрастание publish-workflow'ов (6 на `workflow_run`) | **P1** | Release-инфраструктура | 0.5–1 день |
| F-3 | `pytest` из корня репозитория не собирается | **P2** | DX | ~1 час |
| F-4 | В CI нет линтера; мёртвый код (unused imports) | **P2** | Качество кода | ~2 часа |
| F-5 | GitHub Actions пинуются тегами, не SHA | **P2** | Supply chain | ~1 час |
| F-6 | Токен можно передать через argv (`--token`) | **P2** | Безопасность | ~1 час |
| F-7 | Стилевая неоднородность Python (search vs остальные) | P3 | Стиль | ~2 часа |
| F-8 | Дрейф дублей `_http.py` (осознанный tradeoff) | P3 | Архитектура | ~2 часа |
| F-9 | README-бейдж `release-PHASE 7 1.0.1` отстаёт от OPUS 1.1.3 | P3 | Документация | ~5 мин |
| F-10 | Evals-сценарии валидируются, но не исполняются | Наблюдение | Тестирование | — |

---

## 2. Что проверялось и как

- Полный обход структуры: 7 плагинов, 72 skill'а, ~62 reference-документа, 211 Markdown-файлов (~12 000 строк), 12 527 строк Python (из них 6 618 — тесты), 10 GitHub-workflows (1 930 строк YAML).
- Запуск всех тестов ровно так, как это делает CI:
  - `python scripts/validate_repo.py` → **passed**
  - `python -m unittest discover -s tests` (root) → **135 passed + 14 subtests, 0.2 c**
  - per-plugin `unittest discover` (7 плагинов) → **358 tests, все OK, суммарно < 1 c**
- Статический анализ `ruff` (default ruleset) по `plugins/`, `scripts/`, `tests/` → 156 замечаний, из них реальные — единицы (детали в F-4); error-уровень (E/F) — только E501 line-length и 2×F401.
- Сверка консистентности версий: `.claude-plugin/marketplace.json` ↔ `.agents/plugins/marketplace.json` ↔ `.claude-plugin/plugin.json` ↔ `.codex-plugin/plugin.json` ↔ root README ↔ CHANGELOG → **расхождений нет** (подтверждено и валидатором, и независимо).
- Аудит release-механики: теги/релизы на GitHub (`opus-1.1.3`, `yandex-seo-v1.1.2`, `yandex-wordstat-v1.1.2` и др.) соответствуют заявленному в CHANGELOG.
- Чтение ключевых скриптов: `yd_api.py`, `_http.py` (все 4 копии), `seo_topical_architecture.py`, `seo_internal_linking.py`, `ym_import.py`, `ys_overlap.py`, `validate_repo.py`, `contract_controls.py`, `check_reference_freshness.py`.
- Проверка freshness API-референсов: `Verified: 2026-09-02` при лимите 90 дней — актуально.

---

## 3. Сильные стороны

1. **Контрактная дисциплина.** `docs/CONTRACT_MATRIX.json` связывает каждый инвариант (например, `direct.preview-before-write`, `metrika.direct-expense-duplication-guard`) со skills/helpers/tests/references; `tests/test_review_followups.py` и `tests/test_phase7_contracts.py` фиксируют трассировку регрессионно.
2. **Валидатор репозитория как «компилятор контрактов».** `scripts/validate_repo.py` (652 строки общей инфраструктуры) проверяет: SemVer-паритет во всех манифестах, capability-матрицы в README каждого плагина, структуру evals, секреты (regex по `Authorization: Bearer/OAuth`, `Api-Key`, `AQVN*`), запрещённые runtime-пути, отсутствие transport/credentials у cross-service плагинов, двуязычные пары доков, parity release-маркеров changelog. Это редкий уровень самопроверки для markdown-центричного репозитория.
3. **Safety-lifecycle реализован в коде.** `yd_api.py`: любой не-read метод по умолчанию dry-run с редаксом заголовков; `--execute` требует явного флага. Webmaster/Metrika — guarded writes. Cross-service плагины физически не содержат HTTP-клиентов (enforced регулярками по import'ам).
4. **Evidence-семантика.** Разделение claim classes, coverage states (`COMPLETE/PARTIAL/MISSING`), fail-closed поведение при недостатке данных (`DIRECT_SOURCE_UNVERIFIED`, `SERP_VALIDATION_MISSING`), запрет invented demand summation — всё это защищено тестами (101 тест только в SEO-плагине).
5. **Тесты.** 493 теста, чистый stdlib + unittest, ноль зависимостей, мгновенное исполнение, симметричные per-plugin suites. Тесты проверяют содержательные инварианты (нормализация NFKC, orphan-определение по inbound links, `null` vs `[]` для неоценённых артефактов), а не только «код не падает».
6. **Документация.** Честные разделы ограничений, THIRD_PARTY_NOTICES с ролями donor-проектов, датируемые API-факты, ru/en пары с автопроверкой соответствия.
7. **Честная SemVer-политика.** Independent versioning плагинов; repository-milestones не подталкивают к синхронному bump — и матрица версий в README это отражает.

---

## 4. Находки

### F-1 · CI: `py_compile` списки устарели — Phase 7 скрипты не компилируются явно — **P1**

`ci.yml`, job `seo`:
```yaml
run: python -m py_compile scripts/seo_context.py scripts/seo_bundle.py scripts/seo_join.py \
  scripts/seo_quality.py scripts/seo_opportunities.py scripts/seo_cannibalization.py scripts/seo_prioritize.py
```
Отсутствуют `scripts/seo_topical_architecture.py` (524 строки — самый большой скрипт репозитория) и `scripts/seo_internal_linking.py`. Аналогично job `wordstat` не включает `scripts/ywstat_topic_map.py`.

Смягчение: тесты импортируют эти модули, поэтому синтаксические ошибки будут пойманы на шаге unittest. Но ручной список — хрупкая практика: он уже однажды отстал от роста кодовой базы.

**Рекомендация:** заменить перечисление на `python -m compileall -q scripts` (или glob), чтобы список никогда не устаревал. Заодно это сократит YAML.

### F-2 · Release-инфраструктура: 6 workflow'ов на каждый `workflow_run` — **P1**

В `.github/workflows/` накопилось 9 `publish-*.yml`. Шесть из них (`publish-opus-1.1.1/1.1.2/1.1.3`, `publish-phase-7-topical-architecture{,-1.0.1}`, `publish-repository-1.0.2`) висят на:

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
```

и запускаются **на каждый успешный CI-пуш в main** — все шесть одновременно. Каждый несёт собственную копию bespoke idempotency-логики на bash (op. 1.1.3 — 23 КБ, 600+ строк: draft-recovery, tag-lock, immutable-release проверки). Суммарно ~1 900 строк YAML release-механики.

Риски: (а) каждый следующий релиз добавляет ещё один файл навсегда — линейный, неограниченный рост; (б) шесть параллельных заданий с `contents: write` на каждый пуш — широкая поверхность для аудита; (в) расхождение копий логики (что уже произошло — отсюда «hardening»-коммиты); (г) сложность рассуждения о гонках между publisher'ами. Сами guard'ы (`github.repository == ...`, `head_branch == 'main'`, `concurrency` per-workflow) написаны грамотно — вопрос именно в архитектуре процесса, а не в баге.

**Рекомендация:** один параметризованный publisher: `workflow_call`-reusable workflow + матрица/inputs (теги, target-SHA, набор артефактов), исторические one-shot workflow'ы удалить из ветки (они сохранятся в git-истории и прикреплены к уже опубликованным релизам). Альтернатива минимального вмешательства: перевести все на `workflow_dispatch` с inputs и не держать шесть «вечных слушателей» CI.

### F-3 · DX: `pytest` из корня не работает (коллизия пакетов `scripts`) — **P2**

```
$ python -m pytest plugins/ -q
ERROR plugins/yandex-direct/tests/test_yd_api.py
E   ImportError: cannot import name 'yd_report' from 'scripts' (.../scripts/__init__.py)
→ 60 errors during collection
```

Причина: плагин-тесты делают `from scripts import yd_report`, рассчитывая на cwd = каталог плагина (так делает CI через `working-directory`). При запуске из корня рутовый пакет `scripts/` перехватывает импорт. CI не страдает (unittest per-plugin), но любой контрибьютор с привычным `pytest` получает 60 ошибок сбора и красное первое впечатление.

**Рекомендация (одно из):**
- корневой `conftest.py`, вставляющий в `sys.path` каталог каждого плагина с `tests/` (или через `pytest.ini` + `rootdir`-механику), либо
- переименовать рутовый пакет `scripts/` → `tools/` (это также снимает семантическую коллизию с плагин-пакетами), либо
- задокументировать в CONTRIBUTING: «тесты запускаются только per-plugin через unittest».

### F-4 · Нет линтера в CI; мёртвый код — **P2**

В CI только `py_compile` и unittest. `ruff` (дефолт) находит 156 замечаний; после отбрасывания стилистики остаются реальные:
- `scripts/validate_repo.py:9` — `import sys` не используется;
- `plugins/yandex-direct/tests/test_yd_api.py` — неиспользуемый импорт (`io`);
- `tests/test_contract_controls.py:1` — неиспользуемый импорт;
- 2×`DTZ011` (`date.today()` в `ym_logs.py`, `ym_import.py`) — локально-зависимая дата (для freshness-логики уже параметризуемо через `today`, так что это именно техдолг, не баг);
- 78× unsorted imports, 13× deprecated import (`UP035`) — косметика.

**Рекомендация:** добавить в CI шаг `ruff check` с минимальным кураторским набором (`E,F,UP,B,SIM`) и `ruff format --check` либо `black`. Первым же прогоном почистить F401. Это дешёвая постоянная страховка против дрейфа стиля, который уже виден (F-7).

### F-5 · Actions пинуются тегами — **P2**

Все 34 использования: `actions/checkout@v4`, `actions/setup-python@v5`, `actions/github-script@v7` — без пина к SHA. Для репозитория, чьи workflow'ы владеют `contents: write` и выпускают релизы, компрометация тега = компрометация релизного конвейера.

**Рекомендация:** запинить к полным SHA (можно автоматизировать `dependabot`/`renovate` с `pin-actions` или шагом в CI). Хотя бы для workflow'ов с `permissions: write`.

### F-6 · Токен через argv — **P2**

CLI-хелперы принимают `--token` (например, `yd_api.py`, плюс `.env.example` подсказывают env-first). Значение в argv попадает в `/proc/<pid>/cmdline`, shell history и логи CI-отладки. Env-переменная — безопасный дефолт уже есть; риск остаётся в явном флаге.

**Рекомендация:** поддержать чтение из файла (`--token-file`) и/или предупреждать при использовании `--token` («предпочтите env; argv виден в process listing»). Минимум — упомянуть в `.env.example`/README плагинов.

### F-7 · Стилевая неоднородность — P3

Скрипты search-плагина (`ys_overlap.py`, `ys_api.py`, `_http.py`) написаны в ultra-compact стиле с `;`-последовательностями и однобуквенными переменными, остальные плагины — аккуратный PEP8. Внутри `ys_overlap.py` алгоритм корректен (union-guard от деления на ноль есть), но читаемость против остальной кодовой базы контрастирует. Форматтер (см. F-4) закроет вопрос системно.

### F-8 · Дубли `_http.py` — P3 (осознанный tradeoff, зафиксировать дрейф)

4 копии: metrika/webmaster (OAuth) и search/wordstat (Api-Key/IAM). `packages/README.md` явно документирует, почему централизация преждевременна (installability boundary) — с этим согласен. Но копии уже дрейфуют семантически нейтрально (форматирование) и потенциально семантически (webmaster имеет типизированный `WebmasterAPIError`, metrika поднимает голый `RuntimeError`; лимиты чтения тела ошибки различаются — 4096 байт vs безлимит).

**Рекомендация:** до появления distribution-механизма добавить cross-copy consistency-тест: пара функций с одинаковой семантикой (`redact_headers`) проверяется на идентичность поведения (уже почти покрыто per-plugin тестами — достаточно сверить тест-кейсы), и таблицу «какой фикс в какой копии должен быть отражён» в `packages/README.md`.

### F-9 · README-бейдж release — P3

Бейдж `release-PHASE 7 1.0.1` при текущем milestone `OPUS 1.1.3`. В статус-абзаце различие baseline vs maintenance объяснено, но бейдж без контекста читается как «последний релиз — PHASE 7 1.0.1». Вариант: `release-OPUS 1.1.3` + отдельный бейдж `baseline-PHASE 7 1.0.1`, или просто динамический бейдж последнего релиза.

### F-10 · Evals не исполняются — наблюдение

`evals/scenarios.json` (7 плагинов, сценарии с `must_route_to`/`must_refuse`/`must_mention`/`must_not_claim`) валидируются структурно, но runner'а нет — ни в CI, ни вне. Для AI-плагинов это самый ценный и при этом неисполняемый актив: контракты поведения агента проверяются только человеком/LLМ ad hoc. Осознанное ограничение (стоимость/стабильность LLM-прогонов), но стоит явно зафиксировать в ROADMAP этап «scheduled/offline eval runner» хотя бы для `must_refuse`-сценариев safety-класса.

---

## 5. Отдельно проверено — проблем не найдено

- **Версионная консистентность** — все 4 источника манифестов + README + CHANGELOG согласованы для всех 7 плагинов.
- **Секреты в репозитории** — regex-скан валидатора + независимый grep: утечек нет; заголовки везде редактятся (`OAuth ***`, `Bearer ***`, `Api-Key ***`).
- **Cross-service границы** — `yandex-seo`/`yandex-marketing` не содержат import'ов HTTP/transport (проверено валидатором и вручную).
- **Деление на ноль / граничные случаи** — Jaccard (guard пустого union), overlap top-k, CTR-базлайны: guarded.
- **Fail-closed семантика** — unverified Direct provenance блокируется, а не пропускается; неизвестные методы Direct API считаются write по умолчанию (safe-by-default) — правильно.
- **Двуязычная синхронизация** — `bilingual_docs.py` + тесты; ru/en структурно паритетны.
- **Freshness** — контролируемые референсы проверены 2026-09-02 (лимит 90 дней), еженедельный scheduled check с авто-issue — грамотная механика.

## 6. Рекомендованный порядок действий

1. **F-1** (compileall) — быстрый фикс, сразу в ближайший патч.
2. **F-3** (conftest.py / rename `scripts/`→`tools/`) — до того, как появятся внешние контрибьюторы.
3. **F-4** (ruff в CI + чистка) — вместе с F-3 одним PR.
4. **F-2** (консолидация publishers) — следующий maintenance-milestone; самый большой, но самый важный для долгосрочной сопровождаемости.
5. **F-5, F-6** — security-hygiene PR.
6. **F-7–F-9** — по ходу; F-9 — 5 минут.
7. **F-10** — решение в ROADMAP (сделать явно).

## 7. Ограничения ревью

- Не выполнялись live-вызовы Yandex API: корректность API-фактов (эндпоинты v4/v4.1, лимиты, статусы) принята по dated-референсам и внутренним контрактам.
- Не запускались LLM-эвалюации скиллов — оценивалась структура и контракты, не фактическое поведение агента.
- Release-workflow'ы анализировались статически; воспроизведение draft-recovery сценариев не выполнялось.
- Локальный клон содержит единственный squashed-коммит (артефакт среды ревью); на upstream GitHub история полная — не находка.
