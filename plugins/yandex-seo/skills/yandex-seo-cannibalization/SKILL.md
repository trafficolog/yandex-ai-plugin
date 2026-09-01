---
name: yandex-seo-cannibalization
description: Use when investigating whether multiple pages on the same site compete for the same Yandex search intent.
---
# Cannibalization candidates

Do not label two URLs as cannibalization merely because both contain similar words. Require multiple own URLs in the same Search intent/cluster plus Webmaster evidence that visibility is split, unstable or otherwise relevant. Emit `CANNIBALIZATION_CANDIDATE` as a HYPOTHESIS with confidence and the supporting Search and Webmaster evidence. Preserve Search `bridge_risk`; weak transitive clusters reduce confidence and require manual validation before consolidation decisions.
