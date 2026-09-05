# Политика безопасности

[**Русский**](SECURITY.md) · [English](SECURITY.en.md)

## Поддерживаемый scope

По умолчанию security support относится к текущей default-branch/repository release line и текущим версиям production plugins. Историческая версия считается поддерживаемой только если repository явно объявляет это отдельно.

## Что считать security-sensitive finding

К security-sensitive относятся, в частности:

- раскрытие credentials, token, secret или другого чувствительного authentication material;
- обход exact-preview / explicit **approval** boundary и возможность consequential write без требуемого разрешения;
- **prompt** injection или иное нарушение правила «retrieved/uploaded data — данные, а не инструкции»;
- обход cross-service transport/credential ownership, особенно получение SEO/Marketing чужих service credentials;
- нарушение **immutable** release/tag guarantees, unsafe rollback или возможность retarget/delete опубликованной истории;
- dependency/supply-chain issue, способная повлиять на выполняемые helpers, CI или release artifacts.

## Как сообщать

Предпочтительный канал — **private** security reporting через GitHub Security интерфейс этого repository, если он доступен пользователю и включён для проекта.

Если GitHub private reporting недоступен, используйте private contact method, который на момент сообщения явно опубликован владельцем repository/profile. Этот файл намеренно не придумывает email address, bounty program или гарантированный response time.

Если private route найти нельзя, допустимо создать public issue **только с просьбой предоставить private contact channel**. Не публикуйте в public issue exploit details, credentials, tokens, customer/account data, private URLs, payloads или другие сведения, которые увеличивают риск эксплуатации.

## Что приложить privately

Если это безопасно, укажите affected release/commit/plugin, минимальные reproduction steps, ожидаемую и фактическую safety boundary, потенциальный impact и любые условия, необходимые для воспроизведения. Секреты и реальные customer/account credentials не нужны даже в private report, если проблему можно показать на synthetic data.

## Координация исправления

Security fix должен сохранять repository release governance: regression evidence, CI и independent review остаются отдельными сигналами, а human maintainer принимает решение о merge/release. Опубликованные immutable tags/releases не переписываются ради исправления; fix выпускается новым release set.