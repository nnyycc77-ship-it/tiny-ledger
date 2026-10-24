# upc_lookup

**Price: 0.25 USDC per call.**

Answers one question: what does Open Food Facts list for this product
barcode? Give the tool a UPC or EAN barcode and it returns the product
name, brand and category exactly as listed in the Open Food Facts
response, or a proven not found when the database holds no product for
that barcode. The facts are the database's, as listed; the report
makes no assessment of the product and gives no advice. The source is
keyless and public, and the tool uses only the Python standard library.
It is not yet registered on the MCP server; registration is a separate
shared step at the end of the wave.

## Input

- `code`: a product barcode, digits only, in one of the standard
  lengths (8, 12, 13 or 14). The length and the check digit are
  validated locally before any fetch, so a mistyped barcode is refused
  with the reason (wrong length, not digits, or the check digit the
  format expects) and no request is made.

## Source

Open Food Facts API, the product lookup endpoint under
api.openfoodfacts.org:

```
GET https://api.openfoodfacts.org/api/v2/product/{code}.json?fields=product_name,brands,categories
```

Community: https://world.openfoodfacts.org — Open Food Facts is a
crowdsourced food products database; entries are contributed by
volunteers, and blank fields are normal. The fields parameter is
always sent, so the answer stays the small product summary instead of
the full crowdsourced document (about 150 KB unfiltered).

Two properties of this API shape the reading, both pinned by live
captures in the repository:

- The API normalizes barcodes: a 12 digit UPC is answered under its
  zero padded 13 digit form (a query for 036000291452 returns the code
  0036000291452, live capture). The returned code is therefore
  compared to the requested code with leading zeros ignored, and the
  report states the padding plainly when it happens. An answer whose
  significant digits differ from the requested code is about a
  different product: the tool refuses it and emits no report, never
  presenting one product as another. (Asking the API for a short
  numeric string without local validation is how this trap bites: the
  API pads it and answers with a real but wrong product.)
- A barcode the database does not hold is answered with the not found
  document `{"code": ..., "status": 0, "status_verbose": "product not
  found"}`, normally delivered with HTTP 404 (live capture). That
  document, quoted in full in the report, is the proof of the not
  found. Any other non 200 status, an unparseable or off shape body, a
  timed out or failed fetch, or a redirect off the API host produces
  no report at all: the lookup is unknown, never a not found claim.

## Output

The claim block at the top, then the evidence: the exact query URL,
the UTC retrieval time, verbatim field excerpts (the returned code,
status and status_verbose, and the product fields), and the complete
raw response transcript directly beneath.

For a found product:

- the code as shown in the response, with the zero padding stated
  when the API padded a UPC to 13 digits;
- the product name, brand and category, each exactly as listed;
- a field the response leaves absent or blank is shown as not listed
  (live capture 2000000000008 lists a product name with blank brands
  and categories), never filled in from anywhere else.

For a barcode the database does not hold, the answer states that Open
Food Facts holds no product for it and quotes the not found document
in full. That covers the request only; it says nothing about the
product itself.

## Local use

```
python3 tools/upc_lookup.py 3017620422003
python3 tools/upc_lookup.py 036000291452
python3 tools/upc_lookup.py 5098765432100   # not found, proven by the raw response
```

Also served by the API as `GET /upc?code=...` (see api/README.md).

## Verification

Offline tests replay real captures of all four shapes (a found EAN, a
found UPC the API zero padded, a found product with blank fields, and
the not found document) and pin the fail closed rules: a returned code
that does not match the request, an unknown status, a found document
with no product, a found document delivered on a 404, a non JSON body,
and a failed fetch all emit no report.
