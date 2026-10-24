# Unsourced package: SYNTHETIC test input

This folder is a deliberately broken package, built to prove that
`tools/delivery_packager.py verify` fails a deliverable that carries an
unsourced claim (issue #154, acceptance item "verification pass
demonstrably fails a deliberately unsourced example"). It is not a
delivery and must never be sent to a buyer.

It was made from `../recall/report.md` and `../recall/manifest.json`
with exactly these changes, and nothing else:

1. A label line under the title saying the file is SYNTHETIC.
2. An unsourced line added to the Summary: `- No other recall applies to
   this product.` It names no section, and no source in the package
   supports it.
3. In Section S2, the source link line and the fenced raw response
   beneath it were removed, so the section's claims stand without their
   evidence.

The manifest is the recall manifest with its `deliverable_sha256` set to
the SHA-256 of this altered report (and the subject marked SYNTHETIC),
so that the hash check passes and the failures below are the unsourced
claims alone.

Expected result, checked by `tools/tests/test_delivery_packager.py`:

```
$ python3 tools/delivery_packager.py verify --dir tools/delivery-packager/examples/unsourced-SYNTHETIC
FAIL Section S2: the complete raw response for https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128 is not printed in the section (no block with SHA-256 3df43c84a1bc24258dc64ff6eca01985b40bef4e8961301225fd47d5116d1706)
FAIL Section S2: the count cpsc_records has no printed raw response to recount from
FAIL unsourced summary claim (names no section): - No other recall applies to this product.
verify: FAIL (tools/delivery-packager/examples/unsourced-SYNTHETIC)
```

Exit status 1.
