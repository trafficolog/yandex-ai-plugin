# SERP overlap clustering

Use only FLAT XML snapshots. The caller must explicitly choose `top_k` and `min_shared_urls`; there is no universal hidden threshold. Report shared URL count and Jaccard for each pair. Connected-components clustering must expose `weakest_pair` and `bridge_risk` when transitive chaining joins queries whose direct overlap is below the threshold.
