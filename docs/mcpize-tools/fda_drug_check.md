# `fda_drug_check`: FDA drug label facts

A tool factory wave 1 tool (issue #163, parent #158). The fetcher is
[`tools/fda_drug_check.py`](../../tools/fda_drug_check.py), and it is served as
`GET /drug` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is registered on the MCP server: the server on main lists it
(`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
PR #208 (issue #204), the shared surface step the #158 ruling called for.
Going live still waits on the owner redeploy step.

- **What it answers:** For one drug brand or generic name, the label facts of the first matching openFDA drug label record: its brand and generic names, its maker, its product type and route, which warning sections it carries, and its dosage form as the record carries it. The report states the total number of matching label records the response itself reports, so a first record is never presented as the only one when it is not.
- **Source:** openFDA drug label endpoint, `https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22<name>%22+OR+openfda.generic_name:%22<name>%22&limit=1`. Keyless: no API key is needed for this endpoint at this rate and none is read.
- **Arguments:** `name` (a drug brand or generic name, for example Lipitor or acetaminophen). A name carrying a double quote, a backslash or a control character is refused, because the name is searched inside double quotes.
- **Needs on the server:** Outbound HTTPS to `api.fda.gov`. No key, no environment value.
- **Warnings present:** The tool checks the record for the three warning sections `boxed_warning`, `warnings` and `warnings_and_cautions` and names the ones present. It does not summarise or rewrite the warning text; the full label text is in the transcript.
- **Dosage form:** openFDA label records carry no structured dosage form field. The tool prints the record's `dosage_form` when the record has one, else the text of its `dosage_forms_and_strengths` section, else it states plainly that the record carries neither. It never fills the gap from outside the record.
- **What it is not:** Medical advice. It records what one label record says, as shown, at the retrieval time stated.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price. Pricing stays in the owner redeploy step.

Every report uses the repo's fixed evidence format. Each claim has its
source link with the raw response directly beneath it, the exact query
and retrieval time are recorded, and an empty result is proven by the
complete raw response. A failed fetch is an error that names the
source, never an empty result.

## What a report shows, on a recorded response

The tool's answer for one recorded response, a search for Tylenol. The
claims are the tool's own lines for that response (the offline tests
check these exact lines), with the recorded response printed directly
beneath the source link. Note the total: 109 label records matched the
name, and the facts are the first returned record's, as the report
itself states. That record carries a `warnings` section and neither a
`dosage_form` field nor a `dosage_forms_and_strengths` section, and the
report says so.

- `LABEL: first returned record of 109 matching label record(s) (total as shown in the response).`
- `- brand_name as shown: TYLENOL Extra Strength`
- `- generic_name as shown: ACETAMINOPHEN`
- `- maker (openfda.manufacturer_name) as shown: Kenvue Brands LLC`
- `- warnings present: the record carries warnings.`
- `- dosage form: (not present in the API record: the record carries neither a dosage_form field nor a dosage_forms_and_strengths section)`

Source: https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22Tylenol%22+OR+openfda.generic_name:%22Tylenol%22&limit=1, captured keyless live by H6 in the helper environment on issue #163, retrieved 2026-10-24T04:59:59Z; body 7152 bytes, sha256 `9db860274efe440e94df2eb0ceef1b40de734b3d8f8adac0bcd6f86594156a4d`; saved as [`tools/tests/fixtures/openfda/tylenol-hit.http`](../../tools/tests/fixtures/openfda/tylenol-hit.http)
```text
HTTP/1.1 200 OK
Date: Sat, 24 Oct 2026 05:00:08 GMT
Content-Type: application/json; charset=utf-8
X-Frame-Options: deny
X-Xss-Protection: 1; mode=block
Vary: Accept-Encoding
Vary: Accept-Encoding
Vary: Accept-Encoding
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: *
Age: 7
Cache-Control: no-cache, no-store, must-revalidate
Content-Security-Policy: default-src 'none'
Etag: W/"1bf0-x4XGVhGHWWxzz57JtYqhockN0Dg"
Link: <https://api.fda.gov/drug/label.json?search=openfda.brand_name%3A%22Tylenol%22%20OR%20openfda.generic_name%3A%22Tylenol%22&limit=1&skip=0&search_after=0%3D015a6179-bacb-452d-b594-4de628ddc11d>; rel="next"
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Via: https/1.1 api-umbrella (ApacheTrafficServer [cMsSf ])
X-Api-Umbrella-Request-Id: d1dh3rc1a5ujdjp6g1eg
X-Cache: MISS
X-Content-Type-Options: nosniff
X-Vcap-Request-Id: 2962ed1c-10f3-4d5c-56eb-d30e28d8e8ec
Connection: close
Content-Length: 7152

{
  "meta": {
    "disclaimer": "Do not rely on openFDA to make decisions regarding medical care. While we make every effort to ensure that data is accurate, you should assume all results are unvalidated. We may limit or otherwise restrict your access to the API in line with our Terms of Service.",
    "terms": "https://open.fda.gov/terms/",
    "license": "https://open.fda.gov/license/",
    "last_updated": "2026-10-23",
    "results": {
      "skip": 0,
      "limit": 1,
      "total": 109
    }
  },
  "results": [
    {
      "spl_product_data_elements": [
        "TYLENOL Extra Strength acetaminophen CARNAUBA WAX FD&C RED NO. 40 FD&C YELLOW NO. 6 ALUMINUM OXIDE HYPROMELLOSE, UNSPECIFIED FERROSOFERRIC OXIDE MAGNESIUM STEARATE POLYETHYLENE GLYCOL, UNSPECIFIED POLYSORBATE 80 POWDERED CELLULOSE WATER SODIUM STARCH GLYCOLATE TYPE A SUCRALOSE TITANIUM DIOXIDE ACETAMINOPHEN ACETAMINOPHEN TYLENOL;500"
      ],
      "spl_unclassified_section": [
        "Drug Facts"
      ],
      "active_ingredient": [
        "Active ingredient (in each tablet) Acetaminophen 500 mg"
      ],
      "purpose": [
        "Purpose Pain reliever/fever reducer"
      ],
      "indications_and_usage": [
        "Uses temporarily relieves minor aches and pains due to: the common cold headache backache minor pain of arthritis toothache muscular aches premenstrual and menstrual cramps temporarily reduces fever"
      ],
      "warnings": [
        "Warnings Liver warning This product contains acetaminophen. Severe liver damage may occur if you take more than 4,000 mg of acetaminophen in 24 hours with other drugs containing acetaminophen 3 or more alcoholic drinks every day while using this product Allergy alert: acetaminophen may cause severe skin reactions. Symptoms may include: skin reddening blisters rash If a skin reaction occurs, stop use and seek medical help right away. Do not use with any other drug containing acetaminophen (prescription or nonprescription). If you are not sure whether a drug contains acetaminophen, ask a doctor or pharmacist. if you are allergic to acetaminophen or any of the inactive ingredients in this product Ask a doctor before use if you have liver disease Ask a doctor or pharmacist before use if you are taking the blood thinning drug warfarin Stop use and ask a doctor if pain gets worse or lasts more than 10 days fever gets worse or lasts more than 3 days new symptoms occur redness or swelling is present These could be signs of a serious condition. If pregnant or breast-feeding, ask a health professional before use. Keep out of reach of children. Overdose warning In case of overdose, get medical help or contact a Poison Control Center right away. (1-800-222-1222) Quick medical attention is critical for adults as well as for children even if you do not notice any signs or symptoms."
      ],
      "do_not_use": [
        "Do not use with any other drug containing acetaminophen (prescription or nonprescription). If you are not sure whether a drug contains acetaminophen, ask a doctor or pharmacist. if you are allergic to acetaminophen or any of the inactive ingredients in this product"
      ],
      "ask_doctor": [
        "Ask a doctor before use if you have liver disease"
      ],
      "ask_doctor_or_pharmacist": [
        "Ask a doctor or pharmacist before use if you are taking the blood thinning drug warfarin"
      ],
      "stop_use": [
        "Stop use and ask a doctor if pain gets worse or lasts more than 10 days fever gets worse or lasts more than 3 days new symptoms occur redness or swelling is present These could be signs of a serious condition."
      ],
      "pregnancy_or_breast_feeding": [
        "If pregnant or breast-feeding, ask a health professional before use."
      ],
      "keep_out_of_reach_of_children": [
        "Keep out of reach of children."
      ],
      "dosage_and_administration": [
        "Directions do not take more than directed (see overdose warning ) adults and children 12 years and over take 2 tablets every 6 hours while symptoms last do not take more than 6 tablets in 24 hours, unless directed by a doctor do not use for more than 10 days unless directed by a doctor children under 12 years ask a doctor"
      ],
      "dosage_and_administration_table": [
        "<table width=\"65%\" styleCode=\"Noautorules\"><col width=\"25%\" align=\"left\" valign=\"top\"/><col width=\"75%\" align=\"left\" valign=\"top\"/><tbody><tr styleCode=\"Botrule\"><td styleCode=\"Toprule Rrule\">adults and children 12 years and over</td><td styleCode=\"Toprule\"><list listType=\"unordered\" styleCode=\"Square\"><item>take 2 tablets every 6 hours while symptoms last</item><item>do not take more than 6 tablets in 24 hours, unless directed by a doctor</item><item>do not use for more than 10 days unless directed by a doctor</item></list></td></tr><tr><td styleCode=\"Rrule\">children under 12 years</td><td>ask a doctor</td></tr></tbody></table>"
      ],
      "storage_and_handling": [
        "Other information store between 20-25°C (68-77°F) do not use if neck band or foil inner seal imprinted with \"TYLENOL\" is broken or missing"
      ],
      "inactive_ingredient": [
        "Inactive ingredients carnauba wax, FD&C red no. 40 aluminum lake, FD&C yellow no. 6 aluminum lake, hypromellose, iron oxide, magnesium stearate, modified starch may contain , polyethylene glycol, polysorbate 80, powdered cellulose, pregelatinized starch, purified water, sodium starch glycolate, sucralose, titanium dioxide"
      ],
      "questions": [
        "Questions or comments? call 1-877-895-3665 (toll-free) or 215-273-8755 (collect)"
      ],
      "package_label_principal_display_panel": [
        "PRINCIPAL DISPLAY PANEL NDC 50580-590-02 Extra Strength TYLENOL ® FOR ADULTS Acetaminophen Pain Reliever Fever Reducer COATED TABLETS Actual Size 100 Tablets 500 mg each Principal Display Panel"
      ],
      "set_id": "015a6179-bacb-452d-b594-4de628ddc11d",
      "id": "22d94fd9-9488-a812-e063-6394a90a7ffc",
      "effective_time": "20241107",
      "version": "11",
      "openfda": {
        "application_number": [
          "M013"
        ],
        "brand_name": [
          "TYLENOL Extra Strength"
        ],
        "generic_name": [
          "ACETAMINOPHEN"
        ],
        "manufacturer_name": [
          "Kenvue Brands LLC"
        ],
        "product_ndc": [
          "50580-590"
        ],
        "product_type": [
          "HUMAN OTC DRUG"
        ],
        "route": [
          "ORAL"
        ],
        "substance_name": [
          "ACETAMINOPHEN"
        ],
        "rxcui": [
          "198440",
          "209459"
        ],
        "spl_id": [
          "22d94fd9-9488-a812-e063-6394a90a7ffc"
        ],
        "spl_set_id": [
          "015a6179-bacb-452d-b594-4de628ddc11d"
        ],
        "package_ndc": [
          "50580-590-01",
          "50580-590-02",
          "50580-590-03",
          "50580-590-04",
          "50580-590-05",
          "50580-590-06"
        ],
        "is_original_packager": [
          true
        ],
        "unii": [
          "362O9ITL9D"
        ]
      }
    }
  ]
}
```

## The other outcome, on a recorded response

- **A name no label matches** (`Zqxwvnotadrug`): openFDA answers HTTP 404 with the error body `{"error": {"code": "NOT_FOUND", "message": "No matches found!"}}` (shown pretty printed in the recording). The report quotes that code and message, and the complete raw response beneath the source link proves it. Saved as [`tools/tests/fixtures/openfda/no-match-404.http`](../../tools/tests/fixtures/openfda/no-match-404.http), with its provenance in the same folder.
- **A failed fetch** is a source failure, not an empty result: the command prints nothing on stdout and exits 2, and `GET /drug` answers 502 with no report. Both shapes are covered by offline tests with a mocked fetch.

The dosage form lines for a record that does carry a `dosage_form`
field, or a `dosage_forms_and_strengths` section, are covered by
offline tests on small test bodies built in the test file and labelled
there as test bodies, not recordings; no recorded body in this repo
shows those lines, and this page does not quote one as if it did.
