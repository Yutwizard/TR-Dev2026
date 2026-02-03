## Table: entity_master

**Description:** This table represents the authoritative, enterprise-wide obligor registry. It stores the top-level identity of each customer group, legal entity, or economic group used for credit risk, Basel, TFRS 9, Moody’s mapping, and BOT DER_CPEN.Entity Id.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| entity_id | VARCHAR(40) | Top-level unique identifier for the obligor or customer group. Used as the BOT DER_CPEN.Entity Id and compatible with Moody’s ENTITY_CODE. This identifier is systematically constructed by concatenating "entity_short_name + juristic_registration_number" to ensure uniqueness and consistency across counterparty_master, entity_master, and regulatory reporting. This is the primary key that counterparty_master.entity_id references. | BBL0107536000374 | PK | No |
| entity_name | VARCHAR(255) | Full legal name of the entity/obligor. Often the same as Counterparty_Master.legal_name, but stored here at obligor/group level. | Bangkok Bank PCL | - | No |
| entity_short_name | VARCHAR(10) | Short name / abbreviation used in risk reporting. | BBL | - | Yes |
| entity_type | VARCHAR(50) | Fine-grained Basel/Moody’s obligor classification (BANK, BANK_SOV, PSE, CORP_HVCRE, SME_PF, INDIV, SOV, SUPRA, etc.). Used for regulatory RW, EAD grouping, and Moody’s mapped class. | BANK | - | No |
| industry_sector | VARCHAR(50) | User-defined industry sector (Moody’s INDUSTRY_SECTOR). Used for concentration analysis. | FINANCIALS | - | Yes |
| country_code | CHAR(3) | Country of domicile for country risk and Basel mapping. | TH | - | No |
| juristic_registration_number | VARCHAR(20) | เลขจดทะเบียนนิติบุคคล / เลขนิติบุคคล (13 digits for Thai juristic entities). Used for KYC, BOT reporting, and obligor-level regulatory mapping. | 0107536000374 | - | No |
| registered_capital_amount | DECIMAL(20,2) | ทุนจดทะเบียนของนิติบุคคล (Registered Capital of the entity). | 40000000000 | - | Yes |
| financials_currency | CHAR(3) | Currency for financials. | THB |  | Yes |
| g_sib_type | CHAR(1) | G-SIB / D-SIB classification (G/D/NULL). | D | - | Yes |
| created_date | DATE | Record creation timestamp. | 2024-01-10 00:00:00 | - | No |
| last_updated_date | DATE | Record last update timestamp. | 2025-07-15 00:00:00 | - | Yes |

## Table: counterparty_master

**Description:** This table serves as the single, authoritative repository for all external and internal entities with which the bank conducts treasury business.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| entity_id | VARCHAR(40) | Unique reference number identifying a person, juristic person, group of persons, group of juristic persons, or customer group. May represent either (a) an internal identifier used within the financial institution, or (b) an external reference number used for BOT data submission. | BBL0107536000374 | FK → entity_master.entity_id | No |
| counterparty_id | VARCHAR(40) | Unique system-generated identifier for the counterparty. | 101 | PK | Yes |
| legal_name | VARCHAR(255) | The full legal name of the entity. | Bangkok Bank PCL | - | No |
| short_code | VARCHAR(50) | A short, unique code used for quick identification in user interfaces. | BBL | - | Yes |
| counterparty_type | VARCHAR(50) | Type of counterparty (e.g., 'Commercial Bank', 'SOE', 'Corporate', 'Central Bank'). | Commercial Bank | - | No |
| bank_code | VARCHAR(13) | Official identifier assigned by the Bank of Thailand in Sheet 'BANK_CODE'. The format should be Text "XXX". | 001 | - | Yes |
| swift_bic | VARCHAR(11) | The counterparty's Business Identifier Code for SWIFT messaging. | BKKBTHBK | - | Yes |
| primary_credit_rating | VARCHAR(10) | The primary credit rating from the designated agency. | AA+ | - | Yes |
| primary_rating_agency | VARCHAR(50) | The name of the primary credit rating agency (e.g., 'Fitch', 'TRIS Rating'). | TRIS Rating | - | Yes |
| primary_rating_date | DATE | The date the primary rating was assigned or last updated. | 2025-07-15 00:00:00 | - | Yes |
| created_date | DATE | Timestamp of record creation for audit purposes. | 2024-01-10 00:00:00 | - | No |
| last_updated_date | DATE | Timestamp of the last update for audit purposes. | 2025-07-15 00:00:00 | - | Yes |
| involved_party_type | INT | Classification code representing the type of institution or counterparty based on the Bank of Thailand’s (BOT) standardized in sheet “Involved_Party_Type” list. | 176039 | - | No |
| customer_code | VARCHAR(10) | Bank-defined customer classification code used to identify the type of customer for regulatory, reporting, and business rules (e.g., interest calculation, FCC, interbank classification). Each CIF must be mapped to exactly one customer type. The code is maintained by the bank and aligned with BOT/MFSMCG concepts such as Personal, Juristic Person, Government, Financial Institution (Resident / Non-Resident), etc.  Please refer to sheet 'Customer_type_master' for the defition. | 2008 | - | No |
| reside_in_thailand_flag | BOOLEAN | Indicates whether the counterparty is a financial institution that resides in Thailand, in accordance with the Monetary and Financial Statistics Manual and Compilation Guide (MFSMCG) residency classification. - TRUE = Counterparty is resident in Thailand (มีถิ่นฐานอยู่ในประเทศ) - FALSE = Counterparty is non-resident (มีถิ่นฐานอยู่นอกประเทศ) Please refer to sheet 'Resident definition' for the defition. | TRUE | - | No |

## Table: security_master

**Description:** This table is a comprehensive catalog of every financial instrument the bank can trade or hold, aligned with standards from the Thai Bond Market Association (ThaiBMA).

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| security_id | VARCHAR(10) | Unique system-generated identifier for the security e.g. The official trading symbol used by ThaiBMA. | LB28DA | PK | No |
| isin | VARCHAR(12) | International Securities Identification Number. | TH0623038C09 | PK | No |
| issuer_id | VARCHAR(40) | Identify the issuer. 1 = Govt of Thailand, 2 = BOT, 3 = State Own Enterprise, 4 = Corporate https://www.thaibma.or.th/EN/Issuer/IssuerSearch.aspx | 1 | PK | No |
| unique_id | VARCHAR(20) | ID for BOT report , Please refer to Sheet 'Unique Id Type'.  ( (1) BOT bond use BANK_CODE   (2) Govt bond, T-bill, SOE bond, SOE MOF use Govt Agency code  (3) Corp bond, use Juristic Id from dataforThai website) | 001 | PK | No |
| instrument_type | VARCHAR(20) | The type of instrument (e.g., 'T-Bill', 'Gov Bond', 'Corp Bond', 'SOE Bond', 'BOT Bond', 'SOE MOF'). | Gov Bond | - | No |
| issue_date | DATE | The date the security was issued. | 2018-12-17 00:00:00 | - | No |
| maturity_date | DATE | The date the security matures. | 2028-12-17 00:00:00 | - | No |
| coupon_rate | DECIMAL(10,6) | Nominal coupon rate. “0” for zero-coupon bonds. Fixed: contract rate; Floating: last reset per ThaiBMA MTM. | 2.75 | - | Yes |
| coupon_margin | DECIMAL(10,6) | Spread over the reference rate in percentage terms. For fixed-rate deals, set to 0 | 0.1 | - | Yes |
| coupon_reference_rate | VARCHAR(20) | Floating rate benchmark (e.g., THBFIX6M). If fixed, set to NULL. |  | - | Yes |
| coupon_frequency | VARCHAR(20) | Frequency of coupon payments (e.g., 'Semi-Annual', 'Quarterly'). | Semi-Annual | - | No |
| coupon_day_count_conv | VARCHAR(20) | The convention for calculating accrued interest (e.g., 'Actual/365'). 1 | Actual/365 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency code. | THB | - | No |
| country | VARCHAR(3) | Country Code | TH | - | No |
| bond_structure | VARCHAR(20) | Structure of principal repayment (e.g., "ZERO", 'Bullet'). | Bullet | - | No |
| rating_tris | VARCHAR(8) | The long-term credit rating assigned to the security or issuer by TRIS Rating (Thailand). This field stores the latest available rating used for credit risk assessment and reporting. Leave blank for Government or MOF-guaranteed securities where ratings are not applicable. | A- | - | Yes |
| rating_fitch | VARCHAR(8) | The long-term credit rating assigned to the security or issuer by Fitch Ratings. This field stores the latest available rating used for credit risk assessment, valuation models, and investment eligibility checks. Leave blank for Government or MOF-guaranteed securities where ratings are not applicable. | A-(tha) | - | Yes |
| is_eligible_bot_repo_collateral | BOOLEAN | Flag indicating if the security is eligible for use in BOT's repo operations. | 1 | - | No |
| is_eligible_crm_collateral | BOOLEAN | Flag indicating if the security meets BOT's criteria for Credit Risk Mitigation. | 1 | - | No |
| status | VARCHAR(20) | Active', 'Matured', 'Defaulted'. | Active | - | No |
| status_timestamp | DATETIME | Timestamp of record creation. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2024-02-01 11:00:00 | - | Yes |
| coupon_rate_type | VARCHAR(10) | ‘Fixed’ or ‘Floating’. | Fixed | - | No |
| cross_default | BOOLEAN | Flag indicating if the security has entered default due to a cross-default event triggered by another security under the same issuer. If TRUE, the system immediately treats this plan as defaulted. | False | - | No |

## Table: portfolio_master

**Description:** This table allows for the logical segregation of the bank's treasury positions according to their strategic intent.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| portfolio_id | VARCHAR(40) | Unique system-generated identifier for the portfolio. | 201 | PK | No |
| portfolio_name | VARCHAR(100) | Clear accounting classification upfront (e.g., 'Amortized Cost', 'Fair Value through OCI', 'Fair Value through P&L (Trading Book)') along with Asset type (Gov, SOE, BOT, T-Bill) | AMC - Govt Bonds | - | No |
| portfolio_manager | portfolio_manager | The name or ID of the responsible manager or desk. | John Doe | - | No |
| accounting_treatment | VARCHAR(50) | The accounting designation which dictates valuation and P&L recognition rules. | FVOCI | - | No |
| created_timestamp | DATETIME | Timestamp of record creation. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2024-02-01 11:00:00 | - | No |

## Table: netting_agreement

**Description:** This table contains the master information for all legally enforceable netting and collateral agreements (e.g., ISDA, CSA, GMRA, GMSLA) established between the institution and its counterparties.
 Each record represents one agreement that defines the scope, effective period, and key legal attributes governing how financial transactions (e.g., swaps, repos, FX, securities lending) are netted, margined, and settled.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| netting_agreement_id | VARCHAR2(40) | Unique generated identifier for each netting agreement record. | GMRA_2023_KB | PK | No |
| counterparty_id | VARCHAR(40) | Identifier linking to the counterparty legal entity in Counterparty_Master. | 101 | FK → counterparty_master.counterparty_id | No |
| netting_set_id | VARCHAR(40) | Logical identifier for the enforceable netting set under which trades are aggregated. Remains the same for new/replacement agreements if the legal relationship continues. | 20001 | - | No |
| agreement_type | VARCHAR(10) | Type of master/annex agreement defining the netting scope i.e. GMRA, ISDA. | GMRA | - | No |
| netting_type | VARCHAR2(20) | Classification of the netting structure used in the agreement. Examples: • CLOSE_OUT – for close-out netting under ISDA/CSA • COLLATERAL – for collateral netting • SET_OFF – for balance sheet set-off netting | COLLATERAL | - | No |
| collateral_contract_type | VARCHAR2(12) | Classification of the netting collateral type, used by the engine to determine exposure and regulatory product mapping: • REP – contract type for collateral legs under repo agreements. • BAL – contract type for balance sheet/liability netting. • OTC – contract type for OTC derivatives. | REP | - | No |
| trade_date | DATE | Date of signature or execution of the agreement by both parties. | 2023-06-15 00:00:00 | - | No |
| value_date | DATE | Effective or enforcement date when the agreement becomes active for new trades. | 2023-07-01 00:00:00 | - | No |
| maturity_date | DATE | Expiry or termination date of the agreement. No new trades should map after this date. | 2025-06-30 00:00:00 | - | Yes |
| is_replacement | TINYINT (0/1) | Flag indicating if this agreement replaces an earlier one (1 = Yes, 0 = No). | False | - | No |
| replaced_agreement_id | VARCHAR(40) | References the previous NettingAgreementID that this record replaces. Null if not a replacement |  | FK → netting_agreement.netting_agreement_id | Yes |
| settlement_currency | VARCHAR(3) | Primary settlement or close-out currency used under the agreement. | THB | - | Yes |
| created_at | DATETIME | Timestamp of record creation. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-03-01 10:30:00 | - | No |
| updated_at | DATETIME | Timestamp of the latest record update. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-03-25 18:45:00 | - | Yes |
| agreement_status | VARCHAR(20) | ‘Active’, ‘Matured’, ‘In-Default’. | Active | - | No |

## Table: interbank_deals

**Description:** This table records all interbank lending (placements) and borrowing (takings) transactions.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| deal_id | VARCHAR(40) | Unique identifier for the deal. | 40001 | PK | No |
| trade_date | DATETIME | Date and time the deal was executed. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-09-05 10:30:00 | - | No |
| value_date | DATE | The start date of the loan/deposit. | 2025-09-05 00:00:00 | - | No |
| maturity_date | DATE | The end date of the loan/deposit. | 2025-09-08 00:00:00 | - | No |
| deal_type | VARCHAR(10) | Lend' or 'Borrow'. | Lend | - | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master. | 101 | FK → counterparty_master.counterparty_id | No |
| principal_amount | DECIMAL(20,2) | The nominal amount of the deal. | 250000000 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency code. | THB | - | No |
| reference_rate_id | VARCHAR(20) | Contractual reference rate identifier, typically ReferenceRate + ReferenceRate_Tenor + DealID (e.g. ‘THOR1M45001’). | THOR1M | - | Yes |
| interest_rate_type | VARCHAR(10) | Fixed' or 'Floating'. | Fixed | - | No |
| interest_rate | DECIMAL(10,6) | The current applicable interest rate (% p.a.).  • Fixed: the agreed contractual rate (reported from TradeDate).  • Floating: the latest ResetRate (= ReferenceRate + Margin) effective from LastResetDate. | 2.25 | - | No |
| reference_rate_tenor | VARCHAR(10) | Tenor bucket of the reference rate, if applicable. Possible values include ‘O/N’, ‘1M’, ‘3M’, ‘6M’. | 1M | - | Yes |
| reference_rate | VARCHAR(20) | Benchmark name if floating (e.g., ThaiBMA/BOT code: THOR, THORA, SOFR). For fixed-rate deals, set value = 'FIX'. | THOR | - | No |
| margin | DECIMAL(10,6) | Spread over the reference rate in percentage terms. For fixed-rate deals, set to NULL. | 0.26161 | - | Yes |
| reset_rate | DECIMAL(10,6) | The actual benchmark rate fixed on LastResetDate. Used to compute InterestRate = ResetRate + Margin. NULL for fixed deals. | 2.05 | - | Yes |
| last_reset_date | DATE | Start date of the current interest period for floating-rate deals. Usually equals ValueDate for first reset. NULL if fixed. | 2025-05-09 00:00:00 | - | Yes |
| next_reset_date | DATE | End date of current interest period / next reset date. NULL if fixed or last reset before maturity. | 2025-05-10 00:00:00 | - | Yes |
| day_count_convention | VARCHAR(20) | The convention for calculating accrued interest (e.g., 'Actual/365'). 1 | Actual/365 | - | No |
| accrued_interest | DECIMAL(20,2) | The calculated interest accrued to date. | 46232.88 | - | Yes |
| status | VARCHAR(20) | Active', 'Matured', 'Defaulted'. | Active | - | No |
| confirmation_ref | VARCHAR(50) | Reference to the outgoing/incoming ISO 20022 confirmation. | CONF-ISO-45001-20250905 | - | Yes |
| limit_id | VARCHAR(40) | Unique identifier linking to a specific limit (e.g., Counterparty Exposure). | 45 | FK → limit_utilization.limit_id | Yes |
| term | INT | The term of the Interbank in days. | 7 | - | No |
| entity_id | VARCHAR(40) | Top-level obligor / customer group to which this limit belongs. Links to Entity_Master.entity_id and aligns with BOT DER_CPEN Entity Id. | BBL0107536000374 | FK → entity_master.entity_id | No |

## Table: interbank_interest_schedule

**Description:** This child table maintains the interest period schedule (floating) and reset details for each interbank lending or borrowing deal recorded in the Interbank_Deals table.
Each record represents a single interest accrual period, storing the applicable benchmark rate, margin, effective interest rate, and accrued interest for that specific period.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| schedule_id | VARCHAR(40) | Primary key for each interest period record. | 1 | PK | No |
| referencerate_id | VARCHAR(20) | Contractual reference rate identifier, typically ReferenceRate + ReferenceRate_Tenor (e.g. ‘THOR1M’). | THOR1M | FK → interbank_deals.referencerate_id | No |
| deal_id | VARCHAR(40) | Link to parent deal in Interbank_Deals. | 50001 | FK → interbank_deals.deal_id | No |
| last_reset_date | DATE | Start date of the current interest period. | 2025-01-03 00:00:00 |  | No |
| next_reset_date | DATE | End date of the current interest period / next scheduled reset date. | 2025-02-03 00:00:00 |  | No |
| reset_rate | DECIMAL(10,6) | Benchmark fixing rate (e.g., THOR 1M) applied for this period. NULL if next period not yet fixed. | 2.05 |  | Yes |
| interest_rate | DECIMAL(10,6) | Total effective rate = ResetRate + Margin for this period.  NULL if next period not yet fixed. | 2.15 |  | Yes |
| status | VARCHAR(20) | Status of the period (‘Active’, 'Planned', ‘Closed’). | Active |  | No |

## Table: repo_trades

**Description:** This table captures the master details of each REPO or Reverse REPO transaction.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| repo_trade_id | VARCHAR(40) | Unique identifier for the REPO trade. Use non-overlapping ID sequences (e.g., RepoTradeID starts at 70000+, BondTradeID starts at 90000+). | 70001 | PK | No |
| trade_date | DATETIME | Date and time the trade was executed. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-09-05 14:00:00 | - | No |
| trade_type | VARCHAR(20) | Repo (you give securities, get cash) or ReverseRepo (you receive securities, give cash) or 'Rehypothecation' | Repo | - | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master. | 215 | FK → counterparty_master.counterparty_id | No |
| netting_agreement_id | VARCHAR2(40) | Unique generated identifier for each netting agreement record. | GMRA_2023_KB | - | Yes |
| netting_set_id | VARCHAR(40) | Logical identifier for the enforceable netting set under which trades are aggregated. Remains the same for new/replacement agreements if the legal relationship continues. | 20001 | - | Yes |
| nominal_amount | DECIMAL(20,2) | Face value of securities being repoed or received. | 100000000 | - | No |
| purchase_date | DATE | Start date of the REPO (first leg). | 2025-09-08 00:00:00 | - | No |
| repurchase_date | DATE | End date of the REPO (second leg). | 2025-09-15 00:00:00 | - | No |
| purchase_price | DECIMAL(20,2) | Cash received (REPO) or cash paid (Reverse Repo) on day 1 (purchase date). | 100000000 | - | No |
| repurchase_price | DECIMAL(20,2) | Cash paid (REPO) or received (Reverse Repo) on day 2 (repurchase date). | 100038356.2 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency code. | THB | - | No |
| reference_rate_id | VARCHAR(20) | Contractual reference rate identifier, typically reference_rate + repo_trade_id | THOR1M | - | Yes |
| interest_rate_type | VARCHAR(10) | Fixed or Floating. | Fixed | - | No |
| interest_rate | DECIMAL(10,6) | Current applicable repo rate (% p.a.). • Fixed = agreed contractual rate. • Floating = ResetRate + Margin. | 2.25 | - | No |
| reference_rate | VARCHAR(20) | Benchmark name if floating (e.g., ThaiBMA/BOT code: THOR, THORA, SOFR). For fixed-rate deals, set value = 'FIX'. | FIX | - | No |
| margin | DECIMAL(10,6) | Spread (%) added over ReferenceRate for floating repos; NULL if fixed. |  | - | Yes |
| day_count_convention | VARCHAR(20) | The convention for calculating accrued interest (e.g., 'Actual/365'). 1 | Actual/365 | - | No |
| repo_rate | DECIMAL(10,6) | The implied interest rate of the transaction. | 2 | - | Yes |
| term | INT | The term of the REPO in days. | 7 | - | No |
| repo_out_flag | BOOLEAN | TRUE if securities are currently out as collateral. | 1 | - | No |
| repo_in_flag | BOOLEAN | TRUE if securities received via Reverse Repo. | False | - | No |
| status | VARCHAR(20) | Active', 'Matured', 'In-Default'. | Active | - | No |
| limit_id | VARCHAR(40) | Unique identifier linking to a specific limit (e.g., Counterparty Exposure). | 45 | FK → limit_utilization.limit_id | Yes |
| accrued_interest | DECIMAL(20,2) | The calculated interest accrued to date. | 46232.88 | - | Yes |
| entity_id | VARCHAR(40) | Top-level obligor / customer group to which this limit belongs. Links to Entity_Master.entity_id and aligns with BOT DER_CPEN Entity Id. | BBL0107536000374 | FK → entity_master.entity_id | No |

## Table: collateral_positions

**Description:** This is a child table to Repo_Trades, providing a granular log of all securities allocated as collateral for a specific trade.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| collateral_id | VARCHAR(20) | Unique identifier for this specific collateral allocation. Typically constructed using RepoTradeID + SecurityID + sequence number to ensure uniqueness across multiple collateral pieces within the same trade.” | 77002_LB28DA_1 | PK | No |
| repo_trade_id | VARCHAR(40) | Links to the parent Repo_Trades record. | 77002 | PK  | No |
| security_id | VARCHAR(10) | Links to the specific security in Security_Master. | LB28DA | FK → security_master.security_id | No |
| nominal_amount | DECIMAL(20,2) | The face value of the securities pledged. | 102500000 | - | No |
| allocation_date | DATE | The date this collateral was allocated to the trade. | 2025-09-08 00:00:00 | - | No |
| valuation_price | DECIMAL(18,6) | The clean price used for valuation at the last MTM cycle. | 100.1 | - | Yes |
| market_value | DECIMAL(20,2) | The calculated market value (Nominal * Price + Accrued). | 102602500 | - | Yes |
| haircut_percentage | DECIMAL(5,2) | Haircut applied to this collateral lot for margining purposes, as per GMRA / internal CRM rules. | 2 | - | Yes |
| collateral_value_after_haircut | DECIMAL(20,2) | The final value of the collateral for margining purposes. | 100550450 | - | Yes |
| margin_call_id | INT | Links to a margin call event in Margin_Calls if this allocation was created or adjusted due to a margin call. |  | FK → margin_calls.margin_call_id | Yes |
| currency | VARCHAR(3) | ISO 4217 currency code. | THB | - | No |

## Table: bond_trades

**Description:** This table records all outright purchases and sales of bonds for the bank's investment portfolios.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| bond_trade_id | VARCHAR(40) | Unique identifier for the originating trade. This field links to either the Bond_Trades table (if the position arises from a bond trade) or the Repo_Trades table (if the position arises from a repo/reverse-repo transaction). Use non-overlapping ID ranges to distinguish trade types (e.g., BondTradeID ≥ 90000, RepoTradeID ≥ 70000). | 90001 | PK | No |
| portfolio_id | VARCHAR(40) | Links to Portfolio_Master to indicate which portfolio the trade belongs to. | 201 | FK → portfolio_master.portfolio_id | No |
| trade_date | DATE | Date for the trade was executed. | 2025-09-05 00:00:00 | FK → security_master.security_id | No |
| settlement_date | DATE | The date for settlement (typically T+2 in Thailand). 1 | 2025-09-09 00:00:00 | FK → counterparty_master.counterparty_id | No |
| security_id | VARCHAR(10) | Links to the specific security in Security_Master. | LB28DA | - | No |
| counterparty_id | VARCHAR(40) | Links to the broker/dealer in Counterparty_Master. | 101 | - | No |
| trade_type | VARCHAR(10) | Buy' or 'Sell'. | Buy | - | No |
| nominal_amount | DECIMAL(20,2) | The face value of the bonds traded. | 50000000 | - | No |
| clean_price_trade | DECIMAL(18,6) | The agreed-upon price as of trade date. | 169.8 | - | No |
| yield_to_maturity | DECIMAL(10,6) | The calculated yield at the time of the trade. | 2.805 | - | Yes |
| settlement_status | VARCHAR(20) | Pending', 'Settled', 'Failed'. | Pending | - | No |

## Table: bond_transactions

**Description:** This table captures all bond trading activities at the transaction level executed by the bank across its investment and trading portfolios. Each record represents a single trade event, providing full details of the commercial terms, settlement information, pricing attributes, coupon characteristics, and valuation data associated with that transaction.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| trade_id | VARCHAR(40) | Unique identifier for the originating trade. This field links to either the Bond_Trades table (if the position arises from a bond trade) or the Repo_Trades table (if the position arises from a repo/reverse-repo transaction). Use non-overlapping ID ranges to distinguish trade types (e.g., BondTradeID ≥ 90000, RepoTradeID ≥ 70000).  For coupon-only events (trade_type = 'Coupon'), use an alphanumeric convention with the prefix 'CPN_' to clearly distinguish them from principal trades, e.g.:  • CPN_<SecurityID>_<YYYYMMDD>_<nn>    → CPN_GSB26OA_20251016_01 for the first coupon payment of GSB26OA on 16-Oct-2025. | 90001 | PK | No |
| security_id | VARCHAR(10) | Identifier linking to Security_Master. | LB28DA | FK → security_master.security_id | No |
| portfolio_id | VARCHAR(40) | Links to Portfolio_Master (e.g., AMC, FVOCI). | 301 | FK → portfolio_master.portfolio_id | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 112 | FK → counterparty_master.counterparty_id | No |
| trade_type | VARCHAR(20) | Identifies the nature of the bond transaction. Supports normal buy/sell and securities financing (repo) including re-use of collateral, as well as standalone coupon cash receipts.   Allowed Values = 'Buy', 'Sell', 'Repo', 'ReverseRepo', 'Rehypothecation' and 'Coupon' (standalone coupon payment event where only interest cash is received and the bond nominal does not change) where sell have to be more than 90 days in banking book policy | Buy | - | No |
| trade_date | DATE | Date the trade was executed. | 2025-09-05 00:00:00 | - | No |
| settlement_date | DATE | Settlement date (T+2 for THB bonds). | 2025-09-09 00:00:00 | - | No |
| maturity_date | DATE | Bond maturity date (from Security_Master). | 2061-06-17 00:00:00 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency code. | THB | - | No |
| nominal_amount | DECIMAL(20,2) | Original amount at the beginning of the contract, excluding amortization (Face value of Bond). | 100000000 | - | No |
| clean_price | DECIMAL(18,6) | Clean price at reporting date | 170.8 | - | Yes |
| clean_price_trade | DECIMAL(18,6) | The agreed-upon price as of trade date. | 169.8 | - | Yes |
| accrued_interest | DECIMAL(20,2) | Accrued coupon since last payment. Usage by trade_type: • For 'Buy' / 'Sell' / 'Repo' / 'ReverseRepo':     – Represents accrued coupon embedded in the dirty price as of SettlementDate (i.e. interest bought/sold). • For 'Coupon':     – Represents the actual coupon cash received on the coupon payment date for the outstanding nominal.       In this case, no principal (nominal_amount) changes and clean_price_trade is typically 0. | 45694.44 | - | Yes |
| dirty_price | DECIMAL(20,6) | Total paid incl. accrued at reporting date | 171.21 | - | Yes |
| classification | VARCHAR(10) | Accounting classification: AC (AMC), FVOCI, FVTPL. | FVOCI | - | No |
| book_value | DECIMAL(20,2) | • Buy – Calculated at trade inception as: Clean Price at Trade (%) × Nominal Amount ÷ 100 – Represents the initial amortized cost / cost basis contributed by this buy transaction.  • Sell – Represents the carrying amount of the portion sold, determined using the prevailing cost basis method (e.g. WAC). – Calculated as: Average Book Clean Price (%) × Sold Nominal ÷ 100, where Average Book Clean Price is sourced from position_costing.avg_book_price_pct at the realization date.  • Repo / ReverseRepo / Rehypothecation – Populated only if required for accounting or audit traceability; otherwise may be NULL depending on policy.  • Coupon – Not applicable; set to 0 or NULL, as coupon events do not affect bond principal carrying value. | 171180000 | - | No |
| market_clean_value | DECIMAL(20,2) | Market value of the bond excluding accrued interest, calculated as (Market Clean Price × NominalAmount) / 100. | 171500000 | - | Yes |
| market_value | DECIMAL(20,2) | Current MTM fair value (FVOCI/FVTPL) | 172200000 | - | Yes |
| last_coupon_date | DATE | Needed for accrual | 2025-12-17 00:00:00 | - | Yes |
| coupon_rate_type | VARCHAR(10) | ‘Fixed’ or ‘Floating’. | Fixed | - | No |
| coupon_reference_rate | VARCHAR(20) | Benchmark if floating e.g., THBFIX6M (NULL if fixed). |  | - | Yes |
| coupon_margin | DECIMAL(10,6) | Spread over the reference rate in percentage terms. For fixed-rate deals, set to 0 | 0.1 | - | Yes |
| coupon_frequency | VARCHAR(20) | Coupon frequency (Monthly, Quarterly, Semi-Annual, Annual). | Quarterly | - | No |
| coupon_rate | DECIMAL(10,6) | Nominal coupon rate. “0” for zero-coupon bonds. Fixed: contract rate; Floating: last reset per ThaiBMA MTM. | 4.85 | - | No |
| coupon_day_count_conv | VARCHAR(20) | Day count convention (e.g., 30/360, ACT/365). | 30/360 | - | No |
| rating_tris | VARCHAR(8) | The credit rating assigned to the security or issuer by TRIS Rating (Thailand). This field stores the latest available rating used for credit risk assessment and reporting.     Leave blank for Government or MOF-guaranteed securities where ratings are not applicable. | A- | - | Yes |
| rating_fitch | VARCHAR(8) | The credit rating assigned to the security or issuer by Fitch Ratings. This field stores the latest available rating used for credit risk assessment, valuation models, and investment eligibility checks.     Leave blank for Government or MOF-guaranteed securities where ratings are not applicable. | A-(tha) | - | Yes |
| status | VARCHAR(20) | ‘Active’, ‘Matured’, ‘In-Default’. | Active | - | No |
| last_updated_timestamp | DATETIME | System timestamp for last update. =Today() where Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS   | 2025-10-03 17:00:00 | - | No |
| valuation_date | DATE | Date of latest valuation snapshot. | 2025-09-30 00:00:00 | - | No |

## Table: bond_positions

**Description:** This table maintains the current holding details for each bond investment. Each row represents a unique position in a bond under a specific portfolio.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| position_id | VARCHAR(40) | Unique identifier for each bond lot position. | 1 | PK | No |
| security_id | VARCHAR(10) | Bond/security identifier. | LB28DA | FK → security_master.security_id | No |
| portfolio_id | VARCHAR(40) | Portfolio classification (AC/AMC, FVOCI, Trading). | 301 | FK → portfolio_master.portfolio_id | No |
| open_date | DATE | Effective date position was created (usually SettlementDate). | 2025-09-09 00:00:00 | - | No |
| maturity_date | DATE | Bond maturity date for reference. | 2061-06-17 00:00:00 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency code. | THB | - | No |
| nominal_amount | DECIMAL(20,2) | Current outstanding face after sales/adjustments. (net Buy & Sell transactions) | 100000000 | - | No |
| unencumbrance | DECIMAL(20,2) | Portion of NominalAmountOutstanding that is free (not pledged as collateral).    Derived as: (Σ Nominal of Buy) − (Σ Nominal of Sell) − (Σ Nominal of Repo/RepoFromBuy). | 100000000 | - | No |
| encumbrance | DECIMAL(20,2) | Portion of NominalAmountOutstanding pledged as collateral in a Repo transaction.   Derived as: Σ Nominal of Repo | False | - | No |
| unenc_from_reverse_repo | DECIMAL(20,2) | Portion of securities received via Reverse Repo that remain unencumbered.   Derived as: (Σ Nominal of ReverseRepo) − (Σ Nominal of Rehypothecation). | False | - | No |
| rehypothecation | DECIMAL(20,2) | Portion of securities received via Reverse Repo that were subsequently re-pledged (re-hypothecated).   Derived as: Σ Nominal of Rehypothecation. | False | - | No |
| avg_book_clean_price_pct | DECIMAL(12,6) | The weighted average cost basis (WAC) for the remaining position. Used to measure gain/loss on future sales (Changes only when new buys occur (adds to cost basis)). | 169.8 | - | No |
| book_value | DECIMAL(20,2) | Carrying amount at amortized cost at trade date (Clean Price Trade × Nominal ÷ 100).(only bond in Bank Portfolio exclude Reverse REPO bond) | 171800000 | - | No |
| valuation_date | DATE | Date of latest valuation snapshot. | 2025-09-30 00:00:00 | - | No |
| clean_price | DECIMAL(12,6) | Market clean price % at ValuationDate. | 171.5 | - | Yes |
| accrued_interest | DECIMAL(20,2) | Accrued coupon interest on the outstanding nominal at ValuationDate, calculated from LastCouponDate (or IssueDate) to ValuationDate using the bond’s day-count convention. Business rules: • Increases daily (or per accrual run) while the bond is held and no coupon has been paid. • On coupon payment dates:     – A 'Coupon' transaction is recorded in bond_transactions.     – The corresponding coupon cash is captured as accrued_int_realized in position_realization_events.     – This accrued_interest field is reset/rolled into the next accrual period (typically reset close to 0 after payment).  The Bank uploads Accrued Interest (%) (%AI) directly from ThaiBMA MTM data.  Business Rules - Accrued interest increases over time in line with ThaiBMA MTM updates. - On coupon payment dates: 1. A Coupon transaction is recorded in bond_transactions. 2. The coupon cash received is captured as accrued_int_realized in position_realization_events. - %AI from ThaiBMA resets for the new accrual period, and this field reflects the updated MTM %AI accordingly. | 700000 | - | Yes |
| dirty_price | DECIMAL(20,6) | Total paid incl. accrued at reporting date | 171.21 | - | Yes |
| market_value | DECIMAL(20,2) | (Price%×NominalCur/100) + AccruedInterestRpt. (only bond in Bank Portfolio exclude Reverse REPO bond) | 172200000 | - | Yes |
| realized_gain_loss | DECIMAL(20,2) | Realized P&L recognized when NominalAmountOutstanding decreases due to sale or transfer. Changes only when you sell or transfer out a portion of the position. Business rules: • Represents ONLY the clean-price P&L from disposals:       Σ( (SellCleanPricePct − AvgBookPricePct at event date) × SoldNominal / 100 ) | False | - | Yes |
| unrealized_gain_loss | DECIMAL(20,2) | MTM P&L on the remaining outstanding amount.   Rules (by Portfolio_Master.AccountingTreatment):  1. FVOCI  - If Sell lot: 0  - If Buy lot: MarketValue − BookValue (recognized in OCI)    2. AMC  - NULL (not required; no MTM under amortized cost)    3. FVTPL (optional, if applicable)  - MarketValue − BookValue (recognized in P&L) | 400000 | - | Yes |
| status | VARCHAR(20) | ‘Active’, ‘Matured’, ‘In-Default’. | Active | - | No |
| last_updated_timestamp | DATETIME | Last updated timestamp. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-03-10 17:00:00 | - | No |
| market_rate | DECIMAL(10,6) | The ThaiBMA market yield (%) applied in fair value calculations for bond products classified as FVOCI or FVTPL. - For FVOCI/FVTPL bonds, this is the ThaiBMA Market Yield at the valuation date. - For AMC bonds, this field is NULL, as these are measured at amortized cost and do not use market yield in their accounting valuation. | 1.22 | - | Yes |

## Table: position_costing

**Description:** This table maintains the current cost basis and realized P&L state for each active bond position.
Each record represents the aggregated weighted-average cost (WAC) of all buy transactions linked to a position, as well as the cumulative realized gain/loss from any partial disposals. The table is updated whenever a buy or sell transaction occurs.
It supports valuation, accounting, and audit purposes by preserving a clear linkage between trade events, cost accumulation, and realized results.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| costing_id | VARCHAR(40) | Row id. | 1 | PK | No |
| position_id | VARCHAR(40) | Which position/lot this cost belongs to. | 1 | FK → bond_positions.position_id | No |
| cost_method | VARCHAR(8) | WAC, FIFO, LIFO. | WAC | – | No |
| avg_book_price_pct | DECIMAL(12,6) | For WAC: running weighted-avg clean price % (Changes only when new buys occur (adds to cost basis)) . Null for pure FIFO/LIFO. | 100.45 | – | Yes |
| sum_product_clean | DECIMAL(20,6) | Σ(clean% × nominal) for WAC audit. | 100450000 | – | No |
| total_nominal_in | DECIMAL(20,2) | Σ buys/transfers-in nominal contributing to basis. | 100000000 | – | No |
| cumulative_sold_nominal | DECIMAL(20,2) | Σ nominal sold so far (for audit). | 20000000 | – | No |
| realized_gain_loss_to_date | DECIMAL(20,2) | Cumulative realized P&L on this position. | 45000 | – | No |
| last_realization_date | DATE | Last sell/transfer date applied. | 2025-10-29 00:00:00 | – | Yes |

## Table: position_realization_events

**Description:** This table serves as an immutable journal of realized P&L events for bond positions.
Each record represents a single realization event (e.g., a sale or transfer-out) capturing the clean-price differential between the sale and the weighted-average cost at that time.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| realization_id | VARCHAR(40) | Row id. | 1 | PK | No |
| position_id | VARCHAR(40) | Links to the position being sold or transferred. | 1 | FK → bond_positions.position_id | No |
| trade_id | VARCHAR(40) | Reference to the trade causing the realization (sale or transfer). | 93005 | FK → bond_transactions.trade_id | No |
| event_date | DATE | Date of the sale or transfer transaction. | 2025-10-29 00:00:00 | – | No |
| sold_nominal | DECIMAL(20,2) | Nominal amount sold/reduced from position. | 20000000 | – | Yes |
| sell_clean_price_pct | DECIMAL(12,6) | Actual trade clean price (%) at realization. | 102 | – | Yes |
| avg_book_price_pct | DECIMAL(12,6) | For WAC: running weighted-avg clean price %. Null for pure FIFO/LIFO. | 100.45 | – | Yes |
| realized_gainloss | DECIMAL(20,2) | (SellClean − AvgBookClean) × SoldNominal. Gain/loss on clean price basis. Changes only when you sell or transfer out a portion of the position. | 31000 | – | ํYes |
| accrued_int_realized | DECIMAL(20,2) | Realized portion of accrued interest received or paid. • For 'Sell' / 'Maturity' trades:     – Represents the portion of accrued coupon that is actually received (or paid) in cash as part of the transaction’s dirty price. • For 'Coupon' trades:     – Represents the full coupon cash received on the coupon payment date (no change in nominal). | 25000 | – | Yes |
| method_used | VARCHAR(8) | WAC/FIFO/LIFO at time of calc. | WAC | – | No |
| created_at | DATETIME | Timestamp when event record was created in system. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-10-29 17:25:00 | – | No |

## Table: margin_calls

**Description:** This table records all daily margin call events arising from collateralized trading relationships such as repo, reverse repo, and OTC derivative agreements (e.g., GMRA, CSA).
Each record represents a calculated margin requirement based on mark-to-market exposure as of a specific valuation date, adjusted for thresholds, minimum transfer amounts (MTA), and rounding rules.
The table provides a clear workflow and audit trail from exposure calculation through to margin agreement, settlement, and reconciliation.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| margin_call_id | VARCHAR(40) | Unique system-generated identifier for the margin call event. | 1 | PK | No |
| counterparty_id | VARCHAR(40) | Identifier for the counterparty to whom the margin call relates. Links to Counterparty_Master. | 215 | FK | No |
| repo_trade_id | VARCHAR(40) | Links to the parent Repo_Trades record. | 70001 | FK | Yes |
| valuation_date | DATE | The end-of-day date on which the margin calculation was performed. | 2025-10-06 00:00:00 | - | No |
| call_currency | VARCHAR(3) | Currency of the margin call amount, typically THB for Thai repo markets. | THB | - | No |
| call_type | VARCHAR(12) | Classification of the call type: 'CALL' (we request additional margin from counterparty), 'RETURN' (we return excess margin), or 'NONE' (no margin call). | CALL | - | No |
| call_amount | DECIMAL(20,2) | Final net margin amount after applying minimum transfer amount (MTA), thresholds, and rounding rules.Always stored as a positive absolute amount. For CALL, this is the amount we require from the counterparty; for RETURN, this is the excess we return to them. | 2100000 | - | No |
| due_time | DATETIME | Contractual deadline for margin delivery as per legal agreement (e.g. CSA/GMRA). Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-10-07 11:00:00 | - | Yes |
| status | VARCHAR(20) | Workflow status of the margin call: e.g. 'Pending', 'Agreed', 'Settled', 'Cancelled'. | Pending | - | No |
| created_timestamp | DATETIME | Timestamp when the record was first created. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-10-06 18:05:00 | - | No |

## Table: cash_margin_movements

**Description:** This table records all cash-based collateral (margin) movements exchanged between the institution and its counterparties under collateralized agreements such as GMRA (Repo / Reverse Repo).
It represents the cash-side lifecycle of margining, acting as the operational mirror of exposure and margin call calculations. Each row captures a single cash event—posting, receiving, returning, or adjusting margin—and provides a full audit trail from margin call through settlement and reconciliation.
The table also maintains a running outstanding margin balance per margin_call_id and supports the accrual of interest receivable on cash margin that we have posted (typical Repo case), in accordance with GMRA terms.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| cash_margin_movement_id | VARCHAR(40) | Unique system-generated identifier for the cash margin movement. | 1 | PK | No |
| margin_call_id | VARCHAR(40) | Links to the related margin call record in Margin_Call. | 1 | FK | Yes |
| counterparty_id | VARCHAR(40) | Counterparty to whom the cash margin relates. Links to Counterparty_Master. | 215 | FK | No |
| repo_trade_id | VARCHAR(40) | Links to the underlying Repo_Trades record if cash margin is tracked at trade level. | 77002 | FK | Yes |
| call_currency | VARCHAR(3) | Currency of the cash margin movement (usually same as CallCurrency in Margin_Call). | THB | - | No |
| movement_type | VARCHAR(12) | Cash direction from our bank’s perspective: RECEIVE = cash received from counterparty; PAY = cash paid or returned by us. | PAY | - | No |
| amount | DECIMAL(20,2) | Signed cash amount of the margin movement. Positive = cash we receive (margin posted by counterparty). Negative = cash we pay/return (margin we post or return to them). | 2100000 | - | No |
| outstanding_balance | DECIMAL(20,2) | Running net margin balance per margin_call_id after this movement. Calculated as cumulative SUM(amount) ordered by value_date, created_timestamp. Positive = counterparty owes us margin / we hold their cash. Negative = we have posted cash margin and are owed by the counterparty. | 2100000 | - | No |
| value_date | DATE | Value date (settlement date) of the cash margin transfer. | 2025-10-07 00:00:00 | - | No |
| created_timestamp | DATETIME | Timestamp when this movement record was created in the system. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-10-06 20:15:00 | - | No |
| bank_account_code | VARCHAR(20) | Internal GL / nostro account code or account number used for the cash margin transfer. | IB-MARGIN-BBL-001 | - | Yes |
| daily_accrued_int_receivable | DECIMAL(20,2) | Interest accrued for this day only when outstanding_balance < 0 (i.e., we have posted cash margin, typically Repo case). Calculated on the absolute negative balance using GMRA rate and day-count convention. | 85.32 | - | Yes |
| accrued_int_receivable | DECIMAL(20,2) | Cumulative interest receivable from the counterparty on posted cash margin per margin_call_id. Rolling SUM of daily_accrued_int_receivable. | 420.15 | - | Yes |
| interest_on_margin_code | VARCHAR(30) | Identifier of the reference rate used for margin interest under GMRA (e.g., MPC). Always NULL for Reverse Repo or when outstanding_balance ≥ 0. | TH_MPC | - | Yes |
| interest_on_margin_rate | DECIMAL(9,6) | Effective annualized rate applied for this accrual row (as a percentage). NULL when no margin interest is applicable (e.g., Reverse Repo). | 1.5 | - | Yes |
| day_count_basis | VARCHAR(10) | Day-count convention used for margin interest accrual from GMRA terms. NULL for Reverse Repo. | ACT/365 | - | Yes |
| accrual_days | INTEGER | Number of calendar/business days covered by this accrual row. NULL when no accrual is performed. | 1 | - | Yes |
| interest_direction | VARCHAR(20) | Semantic indicator of margin interest obligation. Values: RECEIVABLE, NONE.  Business rule: IF repo_trades.trade_type = 'REPO'    AND margin_calls.call_type = 'RETURN' THEN interest_direction = 'RECEIVABLE' ELSE interest_direction = 'NONE' | RECEIVABLE | - | No |

## Table: limit_utilization

**Description:** This table provides a chronological, auditable record of changes in available credit lines (e.g., placement limits, repo limits) for each counterparty.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| limit_id | VARCHAR(40) | Unique identifier linking to a specific limit (e.g., Counterparty Exposure). Use non-overlapping ID sequences (e.g., REPO_LIMIT starts at 1001+, PLACEMENT_LIMIT starts at 2001+). | 1001 | PK | No |
| counterparty_id | VARCHAR(40) | The counterparty against whom the limit is being utilized. | 101 | FK → counterparty_master.counterparty_id | No |
| limit_type | VARCHAR(20) | Classification of limit used, mirroring Limit_Master.LimitType (e.g. PLACEMENT_LIMIT, REPO_LIMIT, DERIVATIVE_LIMIT). | REPO_LIMIT | - | No |
| currency | VARCHAR(3) | ISO 4217 currency code. | THB | - | No |
| available_line | DECIMAL(20,2) | Available credit line before this utilization event. | 800000000 | - | No |
| total_credit_line | DECIMAL(20,2) | The total credit line assigned to the counterparty for this limit type. | 1000000000 | - | No |
| utilization_amount | DECIMAL(20,2) | The amount of the limit consumed by this transaction. Can be negative for reductions. | 200000000 | - | No |
| credit_line_approve_date | DATE | วันที่อนุมัติวงเงิน (Credit Line Approval Date). Represents the effective date when the approved credit line became valid (approve date = effective date). | 2025-09-05 00:00:00 | - | Yes |
| timestamp | DATETIME | Precise timestamp of the utilization event. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-09-05 10:30:01 | - | No |
| created_date | DATE | Date the credit line was first created (Day-1). For the initial approval, created_date = credit_line_approve_date. | 2025-09-05 00:00:00 | - | Yes |
| entity_id | VARCHAR(40) | Top-level obligor / customer group to which this limit belongs. Links to Entity_Master.entity_id and aligns with BOT DER_CPEN Entity Id. | BBL0107536000374 | FK → entity_master.entity_id | No |

## Table: entity_counterparty

**Description:** This table defines which counterparties are linked to which entity (obligor group) and which parent limit they are allowed to use.
ใช้เก็บ mapping ว่า Entity ID ประกอบด้วย Counterparty ID อะไรบ้าง และทุกตัวใช้วงเงิน Parent ใดร่วมกัน

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| entity_counterparty_id | VARCHAR(40) | Unique identifier for this mapping record. | 1 | PK | No |
| entity_id | VARCHAR(40) | Entity/Obligor ID representing the customer group or legal entity that owns the credit line (วงเงินแม่). | BBL0107536000374 | FK → entity_master.entity_id | No |
| counterparty_id | VARCHAR(40) | Counterparty ID under this entity that can use the parent limit. Represents the dealing/operational party (branch, treasury unit, etc.). | 101 | FK → counterparty_master.counterparty_id | No |
| parent_limit_id | VARCHAR(40) | Parent/Group Limit ID that this counterparty is allowed to consume under the specified entity. | 1001 | FK → limit_utilization.limit_id | No |
| effective_from | DATE | Start date from which this mapping is valid and the counterparty may start using the parent limit. | 2025-01-01 00:00:00 | - | No |
| effective_to | DATE | End date of mapping validity. NULL = currently active; populated when mapping is closed/superseded. |  | - | Yes |
| status | VARCHAR(20) | Status of the mapping (e.g. ACTIVE, INACTIVE). | ACTIVE | - | No |
| remark | VARCHAR(255) | Free-text note, e.g. group name or special conditions. | Group KBank – shared limit | - | Yes |
| created_date | DATE | Timestamp when this mapping record was created. | 2025-01-01 00:00:00 | - | No |
| last_updated_date | DATETIME | Timestamp of the last update to this record. NULL if never updated after creation. Time zone in Thailand (GMT+7). Format: YYYY-MM-DD HH:MM:SS | 2025-02-10 18:30:00 | - | Yes |

