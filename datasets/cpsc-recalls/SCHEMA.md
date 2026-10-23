# Schema: CPSC recalls 2023-01-01 to 2025-12-31

Every field in `recalls-2023-2025.jsonl`, read from the 1049 records themselves. Each field is a key of the CPSC recall API record, returned by https://www.saferproducts.gov/RestWebServices/Recall. Nothing is added, renamed or derived. `[]` marks an array element, and a dot a nested key.

| Field (source key path) | JSON types seen | Records carrying it |
| --- | --- | --- |
| `ConsumerContact` | string | 1049 of 1049 |
| `Description` | string | 1049 of 1049 |
| `Distributors` | array | 1049 of 1049 |
| `Distributors[]` | object | 276 of 1049 |
| `Distributors[].CompanyID` | string | 276 of 1049 |
| `Distributors[].Name` | string | 276 of 1049 |
| `Hazards` | array | 1049 of 1049 |
| `Hazards[]` | object | 1047 of 1049 |
| `Hazards[].HazardType` | string | 1047 of 1049 |
| `Hazards[].HazardTypeID` | string | 1047 of 1049 |
| `Hazards[].Name` | string | 1047 of 1049 |
| `Images` | array | 1049 of 1049 |
| `Images[]` | object | 1049 of 1049 |
| `Images[].Caption` | string | 1049 of 1049 |
| `Images[].URL` | string | 1049 of 1049 |
| `Importers` | array | 1049 of 1049 |
| `Importers[]` | object | 615 of 1049 |
| `Importers[].CompanyID` | string | 615 of 1049 |
| `Importers[].Name` | string | 615 of 1049 |
| `Inconjunctions` | array | 1049 of 1049 |
| `Inconjunctions[]` | object | 279 of 1049 |
| `Inconjunctions[].URL` | string | 279 of 1049 |
| `Injuries` | array | 1049 of 1049 |
| `Injuries[]` | object | 1048 of 1049 |
| `Injuries[].Name` | string | 1048 of 1049 |
| `LastPublishDate` | string | 1049 of 1049 |
| `ManufacturerCountries` | array | 1049 of 1049 |
| `ManufacturerCountries[]` | object | 1045 of 1049 |
| `ManufacturerCountries[].Country` | string | 1045 of 1049 |
| `Manufacturers` | array | 1049 of 1049 |
| `Manufacturers[]` | object | 324 of 1049 |
| `Manufacturers[].CompanyID` | string | 324 of 1049 |
| `Manufacturers[].Name` | string | 324 of 1049 |
| `ProductUPCs` | array | 1049 of 1049 |
| `ProductUPCs[]` | object | 40 of 1049 |
| `ProductUPCs[].UPC` | string | 40 of 1049 |
| `Products` | array | 1049 of 1049 |
| `Products[]` | object | 1049 of 1049 |
| `Products[].CategoryID` | string | 1049 of 1049 |
| `Products[].Description` | string | 1049 of 1049 |
| `Products[].Model` | string | 1049 of 1049 |
| `Products[].Name` | string | 1049 of 1049 |
| `Products[].NumberOfUnits` | string | 1049 of 1049 |
| `Products[].Type` | string | 1049 of 1049 |
| `RecallDate` | string | 1049 of 1049 |
| `RecallID` | number | 1049 of 1049 |
| `RecallNumber` | string | 1049 of 1049 |
| `Remedies` | array | 1049 of 1049 |
| `Remedies[]` | object | 1049 of 1049 |
| `Remedies[].Name` | string | 1049 of 1049 |
| `RemedyOptions` | array | 1049 of 1049 |
| `RemedyOptions[]` | object | 1049 of 1049 |
| `RemedyOptions[].Option` | string | 1049 of 1049 |
| `Retailers` | array | 1049 of 1049 |
| `Retailers[]` | object | 1048 of 1049 |
| `Retailers[].CompanyID` | string | 1048 of 1049 |
| `Retailers[].Name` | string | 1048 of 1049 |
| `SoldAtLabel` | null | 1049 of 1049 |
| `Title` | string | 1049 of 1049 |
| `URL` | string | 1049 of 1049 |
