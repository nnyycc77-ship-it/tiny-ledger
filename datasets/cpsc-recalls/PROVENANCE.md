# Provenance: CPSC recalls 2023-01-01 to 2025-12-31

Written by `tools/build_cpsc_dataset.py` at 2026-10-23T22:08:20Z (UTC). Source: CPSC recall API (SaferProducts.gov RestWebServices), https://www.saferproducts.gov/RestWebServices/Recall.

## Totals

- Records returned by the month queries: 1049
- Repeated records dropped (same RecallID and identical content, kept once): 0
- Records in the dataset: **1049**, one per line of `recalls-2023-2025.jsonl`
- `recalls-2023-2025.jsonl` sha256: `634f42d5f75d694f3af9391dce14aa1c8f7b9a6e11e0ba730b139755d910be46`

## How the count was verified

1. Every month query returned HTTP 200 with a JSON array that passed the fetcher's record schema check, and every record's RecallDate falls inside the month asked for.
2. Records are kept once per RecallID. A RecallID repeated with different content would have stopped the build.
3. For each year, one whole-year query was run. Its set of unique RecallIDs equals the union of that year's month queries:

   - 2023-01-01 to 2023-12-31: 324 unique recalls, `https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-01-01&RecallDateEnd=2023-12-31`, retrieved 2026-10-23T22:08:17Z
   - 2024-01-01 to 2024-12-31: 305 unique recalls, `https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-01-01&RecallDateEnd=2024-12-31`, retrieved 2026-10-23T22:08:18Z
   - 2025-01-01 to 2025-12-31: 420 unique recalls, `https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-01-01&RecallDateEnd=2025-12-31`, retrieved 2026-10-23T22:08:20Z

## Month queries

| Month query URL | Retrieved (UTC) | Records | Raw response sha256 |
| --- | --- | --- | --- |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-01-01&RecallDateEnd=2023-01-31 | 2026-10-23T22:07:42Z | 24 | `103f90bc950f1b8effbebd2f11eb4061441095796d9e3d2e56b88a3212aea8e5` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-02-01&RecallDateEnd=2023-02-28 | 2026-10-23T22:07:44Z | 31 | `5203946b761f1c5fa467428e5c089c241a326d220e064d59257f7d51fdee3462` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-03-01&RecallDateEnd=2023-03-31 | 2026-10-23T22:07:45Z | 40 | `158e3980e59a8cc2fbed5e72408bf6279e1ec99dd571ee3ea3f33cac3d28d979` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-04-01&RecallDateEnd=2023-04-30 | 2026-10-23T22:07:46Z | 25 | `e578c1c2b6b416abf986ff6ac474256265d44bd49d975cefe7e313f411e706cb` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-05-01&RecallDateEnd=2023-05-31 | 2026-10-23T22:07:47Z | 25 | `9dd3937c12e40257d33adcbe34d5043ba03fbccdbb7ca36d86fcb8f019c89c7d` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-06-01&RecallDateEnd=2023-06-30 | 2026-10-23T22:07:48Z | 27 | `aab4894475d1b5a589b003e86e2699f9d325f1798654d2bcad4ede4e70fedb46` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-07-01&RecallDateEnd=2023-07-31 | 2026-10-23T22:07:49Z | 13 | `9c7d2b0a5826e749c3936e91dafc5cd951ae3bb22b55e66e3e018ce08b616f53` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-08-01&RecallDateEnd=2023-08-31 | 2026-10-23T22:07:50Z | 27 | `fa07461b757a774e566541d34968da117034a3f068ad8bd9e8487234a53c85bb` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-09-01&RecallDateEnd=2023-09-30 | 2026-10-23T22:07:51Z | 25 | `107fc8d895095ead30756dbc95711f875f5711269b04d23762d3ef723c62abc3` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-10-01&RecallDateEnd=2023-10-31 | 2026-10-23T22:07:52Z | 17 | `ac9a7d1fde4d3ab96c73f257fa66258893b97cf67fc5c9766159d735413972cb` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-11-01&RecallDateEnd=2023-11-30 | 2026-10-23T22:07:53Z | 35 | `664e820449c3c0b341bea3a960e394874647bebc273ee99d3c70099d4c2199e0` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2023-12-01&RecallDateEnd=2023-12-31 | 2026-10-23T22:07:54Z | 35 | `bd8c5f7f8f02dfc8ea646e9b186bfa7592210c3e2d83c1510c1df8ea821a1cd8` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-01-01&RecallDateEnd=2024-01-31 | 2026-10-23T22:07:55Z | 17 | `82063b89c5ff9cf692f1fe8657abc322ad1723089e14ef6748ea42f9ebbef2e1` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-02-01&RecallDateEnd=2024-02-29 | 2026-10-23T22:07:56Z | 47 | `4a03c212bb62e8972400b3ab8971d15b9324cf9dcafe7e64e599c690cbf5b3a5` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-03-01&RecallDateEnd=2024-03-31 | 2026-10-23T22:07:57Z | 28 | `3bc30f579918153c8990cddc036424b7fa2430b7d58639aaf8ee5c35ec80a363` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-04-01&RecallDateEnd=2024-04-30 | 2026-10-23T22:07:58Z | 29 | `624e9b19949a1ecfe0fe41cd7f0c279112568d3b781a1e74b1c13dbe1d63713a` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-05-01&RecallDateEnd=2024-05-31 | 2026-10-23T22:07:58Z | 26 | `c009ec6457f357561b1d20c17e81f4894c5009180cb1757f4f57282705e98318` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-06-01&RecallDateEnd=2024-06-30 | 2026-10-23T22:07:59Z | 31 | `af4bd374a1a440c1c2dcac3a6d6ecf06ee3f1c4d8e4d8d3ae2d991e01ec8a0ca` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-07-01&RecallDateEnd=2024-07-31 | 2026-10-23T22:08:00Z | 26 | `01ab4db94302ecbae329c5364f83c0db267560d0f7a78d9732e8bbf1dc62ece7` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-08-01&RecallDateEnd=2024-08-31 | 2026-10-23T22:08:01Z | 24 | `26bb75bbd14a427783fa9b35fccd2740c9a1b77da2c400666f0e5c380818b836` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-09-01&RecallDateEnd=2024-09-30 | 2026-10-23T22:08:02Z | 18 | `57d8cf14ae1dee89153e8fe2e90edc6086f8eb23c628a4cac27269130422f03e` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-10-01&RecallDateEnd=2024-10-31 | 2026-10-23T22:08:03Z | 19 | `9b527c204e7eb124bafafafe70e501f5fa3fb3df60ae540183c24d11af9e923f` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-11-01&RecallDateEnd=2024-11-30 | 2026-10-23T22:08:04Z | 19 | `a023351df313f928d9d1e3a3cd57ee1648bed6e9d60626a435e9699cfe26a291` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2024-12-01&RecallDateEnd=2024-12-31 | 2026-10-23T22:08:05Z | 21 | `2582c92127dcf2ce670ffb0c01c6d19f2ed2c1c632cafcf13f26f05261d1be0c` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-01-01&RecallDateEnd=2025-01-31 | 2026-10-23T22:08:06Z | 25 | `3804fcc8b03e7f0c887f1dacac80417ed6a1f09a52ff928f1bad347ebed7e582` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-02-01&RecallDateEnd=2025-02-28 | 2026-10-23T22:08:07Z | 43 | `bdbb1941ec40f858130a60eda37276a901153227589ca070f389cab9176d64a9` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-03-01&RecallDateEnd=2025-03-31 | 2026-10-23T22:08:07Z | 32 | `5f365111e66c6357f2a159071cf0f3831f92171d66a3ed370926b62ec81baf45` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-04-01&RecallDateEnd=2025-04-30 | 2026-10-23T22:08:08Z | 34 | `822790863be4c0ee7c2e0e72840cfc713b04132a0358a8ffe2039655a05a9047` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-05-01&RecallDateEnd=2025-05-31 | 2026-10-23T22:08:09Z | 37 | `a4a38ce08e1c81b3b0fff1e338cb22ff283ca139dba6efae06e4703e6117380d` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-06-01&RecallDateEnd=2025-06-30 | 2026-10-23T22:08:10Z | 38 | `dbb3dba2bcc72d7e114cb2857cd6f842c4418d78b4bd07f45de7b39f1e951cd8` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-07-01&RecallDateEnd=2025-07-31 | 2026-10-23T22:08:11Z | 43 | `59a0e3bd4326f161f748b112f733530f0cd7a34e8ff3b0be8afab125055c0e12` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-08-01&RecallDateEnd=2025-08-31 | 2026-10-23T22:08:12Z | 24 | `08fbe40e1f7c871d41c558b6e10655626701149c1f7a8f3787d4f9594275ef6a` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-09-01&RecallDateEnd=2025-09-30 | 2026-10-23T22:08:13Z | 20 | `86f1a9c7585110a5ab82a2463a3d98291955268dd8d20f56ceef52af4a91e088` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-10-01&RecallDateEnd=2025-10-31 | 2026-10-23T22:08:14Z | 51 | `2a42a8da0e3c1b9adcb3f7c5689ebc559bffebfd3e68dfb8b636d156e0ee9eb0` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-11-01&RecallDateEnd=2025-11-30 | 2026-10-23T22:08:15Z | 40 | `9de412fa620f00e5a6b7f1fa963024f6977c18b33da2e49228ef1d2f40a2505a` |
| https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallDateStart=2025-12-01&RecallDateEnd=2025-12-31 | 2026-10-23T22:08:15Z | 33 | `b841195ba806e90691f4595412f3a8d44accdd393a541ff8b08a555e2e83648b` |
