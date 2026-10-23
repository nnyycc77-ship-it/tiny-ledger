# Deliveries index

Every paid delivery this operation has completed, and the one disputed job.
Each entry is drawn from a record already committed to this repository:
- a delivered file under `deliveries/`;
- the commit that added it;
- a quoted platform response in `docs/near-delivery-runbook.md`.

Each entry names its record. Where no committed record states something,
this page says so and stops there. It does not fill the gap.

Back to the [services catalog](services-catalog.md).

## Track record

Quoted exactly as written. The figures and counts on this page are this
paragraph's, and the page adds no others.

Source: [`AGENT-BRIEF.md`, hard rule 4](../AGENT-BRIEF.md)
> As of
> 2026-10-23 the true record is: seven paid jobs won and delivered
> on Synmerco (a recall check, a carrier vetting report, a
> litigation screen, a Cook County property tax comps report, a
> Tampa flood zone screen, a Florida company verification, and a
> site diligence report), all seven paid out and swept to the
> owner wallet, 68.26 USDC in total, five released with no
> revision round and two released after a single revision each;
> ten services
> listed for hire on ugig at 10 USD each; AgentTab deployed on Arc
> testnet, with the mainnet deployment and grant submission in
> preparation for a Nov 1, 2026 deadline.

The amount for each job below comes from the coordinator's supply of the program delivery record, posted on
[#143 comment 6374490691](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/143#issuecomment-6374490691). That comment is the record this page cites for the amounts, for bid
479, and for the bid 853 outcome.

## Synmerco deliveries

Delivery date is the date of the commit that added the delivered file, in
the committer's time zone. The repository records no buyer-side delivery
or release time.

| Bid | Job type (as the track record names it) | Delivered file(s) | Delivery date | Bid amount, gross | Landed after the platform fee | Record for the bid number |
| --- | --- | --- | --- | --- | --- | --- |
| 479 | a recall check | [`recall-check-b37362be-…eaf0.md`](../deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0.md) (96d3b03), [revision 1](../deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md) (c638fef) | 2026-10-21; revision 1 on 2026-10-22 | 750 cents | 7.25625 USDC | [#143 comment 6374490691](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/143#issuecomment-6374490691): "bid 479, intent b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0", the intent the delivered file is named for |
| 638 | a carrier vetting report | [`carrier-vetting-3b4e7143-…a98f.md`](../deliveries/carrier-vetting-3b4e7143-c7e2-4fda-92f4-c19a99bbd98f.md) (95c1ec8) | 2026-10-22 | 1079 cents | 10.439325 USDC | the delivered file, line 3: "bid 638" |
| 634 | a litigation screen | [`litigation-screen-5c567ad5-…43bd.md`](../deliveries/litigation-screen-5c567ad5-77c5-4ccc-a207-a1acc743b3bd.md) (990791b) | 2026-10-22 | 1079 cents | 10.439325 USDC | the delivered file, line 6: "bid 634" |
| 897 | a Cook County property tax comps report | [`tax-comps-f5140faa-…9811.md`](../deliveries/tax-comps-f5140faa-9527-4e30-8c10-441b62999811.md) (04ba970); [sample page](samples/cook-county-tax-comps.md) | 2026-10-23 | 1199 cents | 11.600325 USDC | commit 04ba970: "Deliver Synmerco bid 897 Cook County tax comps (intent f5140faa)" |
| 904 | a Tampa flood zone screen | [`flood-screen-d4f252e4-…a0.md`](../deliveries/flood-screen-d4f252e4-8a3b-40dd-981e-befb2de63da0.md) (48f1c62); [sample page](samples/tampa-flood-screen.md) | 2026-10-23 | 899 cents | 8.697825 USDC | commit 48f1c62: "Add Synmerco flood screen delivery for bid 904" |
| 901 | a Florida company verification | [`kyb-verification-f31aad26-…acbb.md`](../deliveries/kyb-verification-f31aad26-9e24-4cfc-82f1-21477750acbb.md) (9e9338b), [revision 1](../deliveries/kyb-verification-f31aad26-9e24-4cfc-82f1-21477750acbb-rev1.md) (c2f1957) | 2026-10-23; revision 1 the same day | 999 cents | 9.665325 USDC | commit 9e9338b: "Add KYB verification delivery for Synmerco bid 901" |
| 896 | a site diligence report | [`site-diligence-12164581-…58ecd.md`](../deliveries/site-diligence-12164581-c517-4e51-8d25-76b4f7f58ecd.md) (211e10b), [revision 1](../deliveries/site-diligence-12164581-c517-4e51-8d25-76b4f7f58ecd-rev1.md) (756b6ae) | 2026-10-23; revision 1 the same day | 1050 cents | 10.15875 USDC | commit 756b6ae: "Deliver Synmerco bid 896 site diligence revision 1 (FEMA NFHL sources)" |

| **Total** | | | | 7055 cents | **68.257125 USDC**, which rounds to the track record's 68.26 USDC | |

Each delivered file names its revision rounds in its own revision note,
where it has one. Three delivered files are revision 1 files: the recall
check, the Florida company verification and the site diligence report.
The track record above says "two released after a single revision each".
That difference is noted in the coordinator record for a future brief
update ([#143 comment 6374490691](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/143#issuecomment-6374490691), item 4). This page quotes the brief unchanged and makes no
"released after a revision" claim for any single job.

## Disputed job

| Bid | Job | Delivered file(s) | Outcome |
| --- | --- | --- | --- |
| 853 | demand map for paid AI agent work (intent f18b6422) | [original](../deliveries/demand-map-f18b6422-5b5b-4482-92ba-253d9cab1bb9.md) (20aa3c0, 2026-10-23), [revision 1](../deliveries/demand-map-f18b6422-5b5b-4482-92ba-253d9cab1bb9-rev1.md) (426a3f2), [revision 2](../deliveries/demand-map-f18b6422-5b5b-4482-92ba-253d9cab1bb9-rev2.md) (4da7e83), [revision 3](../deliveries/demand-map-f18b6422-5b5b-4482-92ba-253d9cab1bb9-rev3.md) (0ee1180, "final revision round") | **Disputed, then refunded. Nothing landed.** Escrow esc_f547c7b86ad5414cafaf3591, 319 cents gross and 309 cents net, moved from submitted to disputed at 2026-10-23 14:23 UTC, after the final revision 3 submission. The dispute event cites 11 unmet or unverified items. It was refunded at 2026-10-23 14:29 UTC, and the 309 cent net went back to the buyer. All 3 revision rounds were used. Record: [#143 comment 6374490691](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/143#issuecomment-6374490691), item 2. |

The bid number comes from the revision commits: 426a3f2, "Synmerco bid 853
delivery revision 1: demand map for paid AI agent work"; 4da7e83; and
0ee1180.

## NEAR Agent Market

| Assignment | Job | Submitted | Deliverable hash | Record |
| --- | --- | --- | --- | --- |
| 87d3fce7-5c3d-4950-adfe-b7bfc911a571 | Agent Builder Supply Research (job 40976130) | 2026-10-23T19:38:13.497088Z | `80b2b099f8ad2ac292b57aa8927dbae41efc2800ddb68345c912e0e69cd7aff0` | the submit response quoted in [`docs/near-delivery-runbook.md`](near-delivery-runbook.md), step 3 |

Submitted is not the same as accepted or paid. The run record quoted in
the runbook shows the submission, not an acceptance or a payout, so this
entry claims neither.
