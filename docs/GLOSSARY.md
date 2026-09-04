# Глоссарий

[**Русский**](GLOSSARY.md) · [English](GLOSSARY.en.md)

Глоссарий объясняет термины человеческим языком, но не переименовывает exact machine tokens, которые используются в contracts, artifacts и tests.

## Service plugin

Плагин-владелец конкретного сервиса Яндекса. Он отвечает за API transport, credentials, service-specific helpers и изменчивые API facts. Примеры: Direct, Metrika, Webmaster, Wordstat, Search.

## Cross-service plugin

Оркестратор, который объединяет evidence нескольких service plugins. `yandex-seo` и `yandex-marketing` не владеют собственными Yandex credentials или HTTP transport.

## `preview_id`

Идентификатор exact preview для consequential write. Он связывает approval с конкретной операцией и её approval-bound параметрами. Изменённый payload или identity требует нового preview.

## Delegated preview

Предпросмотр действия, который cross-service plugin может подготовить для owning service plugin. Он не является live mutation и не даёт cross-service plugin право выполнять чужой API write.

## Fail-closed

Поведение «при неопределённости — не продолжать опасное действие». Например, если невозможно доказать, что approval соответствует exact preview, write блокируется вместо попытки угадать намерение пользователя.

## Provenance

Информация о происхождении данных: сервис, endpoint/artifact, query, URL, период, attribution context, метод вычисления и известные ограничения. Provenance помогает не смешивать несовместимые метрики и не выдавать derived value за observed fact.

## `OBSERVED`

Claim, напрямую полученный из источника: API, export, report или другого задокументированного evidence source.

## `DERIVED`

Claim, вычисленный из `OBSERVED` data по явному и проверяемому правилу. Это не то же самое, что direct observation.

## `HYPOTHESIS`

Вывод, для которого текущих evidence недостаточно для более сильного claim. Hypothesis должна оставаться явно помеченной до дополнительной проверки.

## `METHODOLOGY`

Методический принцип или framework. Его нельзя выдавать за подтверждённый Yandex/Google ranking mechanism или quantitative API observation только потому, что он используется в workflow.

## `SERP_VALIDATION_MISSING`

Exact limitation token: Search/SERP evidence, необходимый для соответствующей проверки, отсутствует. Например, Wordstat demand сам по себе не должен превращать candidate page boundary в подтверждённый SERP cluster.

## `canonical`

В Marketing reconciliation — evidence source, выбранный как основной для конкретного расчёта после проверки совместимости KPI, money context и provenance.

## `reconciliation_only`

Evidence используется для сверки с `canonical`, но не складывается с ним в общий показатель. Это снижает риск двойного счёта пересекающихся данных.

## `enrichment`

Evidence добавляет контекст к основному расчёту, но не заменяет `canonical` metric и не становится скрытым источником суммы.
