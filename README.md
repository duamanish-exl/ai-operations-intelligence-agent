#  Insight Forge: AI-Powered KPI Investigation Agent

## Overview

**Insight Forge** is an AI-powered KPI Investigation Agent designed for utility operations teams to understand **why a business KPI changed**, identify the root causes behind the movement, and provide clear, actionable recommendations to stakeholders.

This project is not a traditional reporting dashboard. Instead of only showing KPI trends and charts, Insight Forge works as an intelligent investigation layer where users can ask business questions such as:

- Why did Debt % increase this month?
- Why is Complaint Rate rising?
- Which account segments contributed most to the KPI movement?
- What are the top root causes behind the change?
- What actions should the business take next?

The platform investigates the KPI movement by analyzing operational data across accounts, billing, payments, complaints, meter readings, calls, and contracts. It then generates a business-friendly explanation supported by evidence from the underlying data.

##  Project Objective

The main objective of Insight Forge is to reduce manual KPI investigation effort by automating the process of identifying root causes behind operational changes.

In utility operations, stakeholders often know **what changed**, but they need analysts to help explain **why it changed**. This project aims to bridge that gap by using AI to perform data-driven investigations and explain the impact in simple business language.

##  Business Problem

Utility companies monitor multiple operational KPIs across customer service, collections, billing, metering, and account health.
When a KPI changes unexpectedly, analysts usually need to manually check:

- Customer account health
- Outstanding balance and debt movement
- Billing history
- Estimated bill patterns
- Payment success and failure trends
- Complaint volumes
- Meter faults
- Customer calls
- Contract changes
- Customer risk flags

## This manual investigation process can be:

- Time-consuming
- Reactive
- Repetitive
- Dependent on analyst knowledge
- Difficult for non-technical stakeholders to understand
- Spread across multiple systems and datasets

Insight Forge solves this by allowing users to ask natural language questions and receive AI-generated root cause summaries.

##  Solution Summary

Insight Forge acts as an AI-powered investigation assistant for operational KPI analysis.
The user can select a KPI or ask a direct question. The system then:
1. Detects KPI movement
2. Compares current performance against previous periods
3. Identifies impacted account groups
4. Correlates data across multiple operational tables
5. Detects key contributing factors
6. Quantifies the impact of each driver
7. Generates a clear investigation summary
8. Suggests recommended actions

##  What Makes Insight Forge Different?

Traditional dashboards usually answer:

> What happened?

Insight Forge answers:

> Why did it happen?

A dashboard may show that Debt % increased from 18% to 22%, but Insight Forge investigates the reason behind that increase.

### Example Stakeholder Question

```text
Why did Debt % increase this month?

Example AI Investigation Output
Debt % increased mainly due to a rise in failed Direct Debit payments, higher winter billing amounts, and increased debt among affordability-flagged customers.

Key contributing factors:
1. Failed payment volume increased by 28%.
2. Average bill value increased by 15% due to seasonal consumption.
3. Affordability-flagged customers contributed 34% of new debt accounts.
4. Residential accounts showed the highest debt growth.
5. Accounts with repeated missed payments also received more outbound collection calls.

Recommended actions:
1. Prioritize affordability-flagged customers for early intervention.
2. Review failed Direct Debit cases and retry strategy.
3. Monitor high-bill customers before the next billing cycle.
4. Create targeted payment support campaigns.

## Initial KPIs Covered
The current Proof of Concept focuses on two operational KPIs.

1. Debt %
Definition: Debt % measures the percentage of active customer accounts that currently have a debt amount greater than zero.

Debt % = (Number of active accounts where DEBT_AMOUNT > 0)/(Total active accounts)* 100

## Business Purpose

Debt % helps collections and operations teams understand how many customers are currently carrying debt. An increase in Debt % may indicate issues such as failed payments, higher bill amounts, affordability challenges, or seasonal consumption increases.

## Investigation Areas

Insight Forge investigates Debt % using:

Debt amount
Current balance
Overall balance
Arrears amount
Payment failures
Missed payments
Direct Debit status
Most recent bill amount
Seasonal bill increases
Affordability flag
Vulnerable customer flag
Contract status
Calls and collection activity

2. Complaint Rate
Definition: Complaint Rate measures the number of customer complaints relative to the number of active accounts.

Complaint Rate = (Number of complaints)/(Total active accounts)* 100

## Business Purpose

Complaint Rate helps customer service and operations teams understand if customer dissatisfaction is increasing. An increase in Complaint Rate may be driven by estimated bills, meter issues, billing spikes, payment disputes, or debt collection activity.

## Investigation Areas

Insight Forge investigates Complaint Rate using:

Complaint type
Complaint channel
Complaint status
Estimated bills
Meter faults
Bill increases
Payment failures
Debt collection events
Customer calls
Account type
Vulnerability indicators

## High-Level Architecture

User Question
     |
     v
Conversational UI
     |
     v
AI Investigation Agent
     |
     v
KPI Calculation Engine
     |
     v
Root Cause Analysis Engine
     |
     v
Cross-Table Data Investigation
     |
     v
Evidence and Impact Summary
     |
     v
Business Explanation and Recommended Actions

 ## AI Investigation Flow

The AI Investigation Agent follows a structured investigation process.

Step 1: User Asks a Question
Example: Why did Debt % increase in July?

Step 2: KPI Engine Calculates Movement
The system calculates:
Current month KPI value
Previous month KPI value
Absolute movement
Percentage movement
Impacted account count
Impacted account types

Step 3: Data Correlation
The system checks related operational datasets such as:
Account Health
Account Balance
Billing History
Payments
Complaints
Meter Information
Meter Reading
Calls
Contract

Step 4: Root Cause Detection
The investigation engine identifies drivers such as:
Failed payment increase
Estimated bill increase
High consumption increase
Meter fault increase
Complaint category spike
Specific account type impact
Vulnerable customer impact
Contract expiry impact

Step 5: Impact Quantification
The system measures how much each factor contributed to the KPI movement.
Example:
Failed payments contributed to 31% of the Debt % increase.
Estimated bills contributed to 18% of the Complaint Rate increase.
Residential accounts contributed to 46% of the total debt growth.

Step 6: AI Explanation
The AI generates a simple business explanation for stakeholders.

Step 7: Recommended Actions
The system suggests next-best actions based on the root causes.
User Interface
Insight Forge includes an investigation-first UI.
The UI is not designed only to show charts. It is designed to help users ask questions, investigate results, and understand business drivers.

## Key UI Capabilities
1. KPI Selection
Users can select the KPI they want to investigate.
Supported KPIs in current POC:
Debt %
Complaint Rate

2. Natural Language Question Input
Users can ask questions such as:
Why did Debt % increase this month?
Why are complaints rising?
Which customer group is driving debt growth?
What are the top reasons for complaint increase?
Show me the root cause for Debt % movement.

3. Investigation Summary Panel
The AI provides a short executive summary explaining the KPI movement.
Example: Debt % increased by 4.2% compared to the previous month. The main drivers were failed Direct Debit payments, higher winter bill amounts, and increased debt among affordability-flagged customers.

4. Root Cause Breakdown
The UI shows key drivers such as:
Failed payments
Missed payments
Estimated bills
Meter faults
Billing spikes
Account type impact
Customer risk segment impact

5. Evidence View
Users can view supporting evidence behind the AI explanation.
Example evidence:
Failed payment count increased from 8,420 to 10,780.
Average bill amount increased by 14.6%.
Affordability-flagged accounts contributed 32% of newly debt-positive accounts.
Estimated bills increased by 18.3%.

6. Recommended Actions
The AI suggests possible business actions.
Example:
Recommended Actions:
1. Prioritize failed Direct Debit retry cases.
2. Create payment support campaigns for affordability-flagged customers.
3. Review estimated billing accounts with repeated complaints.
4. Monitor high-balance residential accounts for early intervention.

7. Drill-Down View
Users can drill down into:
Account Type
Complaint Type
Payment Status
Meter Status
Customer Segment
Account-level details

## Data Foundation
The project uses a synthetic but realistic UK utility dataset. The dataset is designed to support KPI monitoring, root cause analysis, AI investigation, and UI testing.

Core Tables
1. ACCOUNT_HEALTH
2. ACCOUNT_BALANCE
3. BILLING_HISTORY
4. METER_READING
5. METER_INFORMATION
6. PAYMENTS
7. COMPLAINTS
8. CALLS
9. CONTRACT
10. KPI_MONTHLY_SUMMARY

## Data Model Explanation

1. ACCOUNT_HEALTH
This table provides account-level operational health snapshots.

Used for:
Debt status
Current balance
Overall balance
Recent payment details
Recent bill details
Recent meter read details
Complaint count
Call count
Payment failure count
Affordability flag
Vulnerable flag
Active account flag

Key columns:
ACCOUNT_NUMBER
ACCOUNT_TYPE
SNAPSHOT_DATE
CURRENT_BALANCE
OVERALL_BALANCE
DEBT_AMOUNT
DEBT_FLAG
MOST_RECENT_PAYMENT_DATE
MOST_RECENT_PAYMENT_AMOUNT
MOST_RECENT_BILL_DATE
MOST_RECENT_BILL_AMOUNT
PAYMENT_FAILURE_COUNT_30D
PAYMENT_FAILURE_COUNT_90D
COMPLAINT_COUNT_30D
COMPLAINT_COUNT_90D
CALL_COUNT_30D
AFFORDABILITY_FLAG
VULNERABLE_FLAG
ACTIVE_ACCOUNT_FLAG

2. ACCOUNT_BALANCE

This table stores historical balance movement.

Used for:

Debt accumulation
Arrears movement
Balance trend
Account status analysis

Key columns:

ACCOUNT_NUMBER
ACCOUNT_TYPE
BALANCE_DATE
CURRENT_BALANCE
OVERALL_BALANCE
DEBT_AMOUNT
ARREARS_AMOUNT
ACCOUNT_STATUS

3. BILLING_HISTORY

This table stores customer billing records.

Used for:

Bill amount analysis
Consumption analysis
Estimated bill detection
Billing spike investigation

Key columns:

BILL_ID
ACCOUNT_NUMBER
ACCOUNT_TYPE
MPXN
BILL_DATE
BILL_AMOUNT
CONSUMPTION_KWH
BILL_TYPE
ESTIMATED_FLAG

4. METER_READING

This table stores meter reading and consumption records.

Used for:

Consumption trend
Estimated reading investigation
Smart meter read analysis
Usage anomaly detection

Key columns:

READING_ID
ACCOUNT_NUMBER
ACCOUNT_TYPE
MPXN
READING_DATE
CONSUMPTION_KWH
READING_TYPE
READ_SOURCE

5. METER_INFORMATION

This table stores meter attributes.

Used for:

Meter type analysis
Smart meter flag analysis
Faulty meter investigation
Meter status impact on complaints

Key columns:

METER_ID
ACCOUNT_NUMBER
ACCOUNT_TYPE
MPXN
METER_TYPE
SMART_METER_FLAG
INSTALL_DATE
METER_STATUS

6. PAYMENTS

This table stores payment behavior.

Used for:

Failed payment investigation
Direct Debit performance
Missed payment analysis
Payment method impact

Key columns:

PAYMENT_ID
ACCOUNT_NUMBER
ACCOUNT_TYPE
PAYMENT_DATE
PAYMENT_AMOUNT
PAYMENT_METHOD
PAYMENT_STATUS
DIRECT_DEBIT_FLAG

7. COMPLAINTS

This table stores customer complaint details.

Used for:

Complaint Rate calculation
Complaint type analysis
Complaint channel analysis
Customer dissatisfaction investigation

Key columns:

COMPLAINT_ID
ACCOUNT_NUMBER
ACCOUNT_TYPE
COMPLAINT_DATE
COMPLAINT_TYPE
COMPLAINT_STATUS
COMPLAINT_CHANNEL

8. CALLS

This table stores customer interaction and collection call details.

Used for:

Customer contact analysis
Collection activity analysis
Complaint follow-up analysis
Promise to pay analysis

Key columns:

CALL_ID
ACCOUNT_NUMBER
ACCOUNT_TYPE
CALL_DATE
CALL_REASON
CALL_OUTCOME
CALL_DIRECTION

9. CONTRACT

This table stores contract-level account information.

Used for:

Contract status analysis
Contract expiry impact
Customer lifecycle analysis

Key columns:

CONTRACT_ID
ACCOUNT_NUMBER
ACCOUNT_TYPE
MPXN
START_DATE
END_DATE
CONTRACT_STATUS

## Table Relationships
ACCOUNT_NUMBER is the primary joining key across all major tables.

ACCOUNT_HEALTH.ACCOUNT_NUMBER
joins with:
- ACCOUNT_BALANCE.ACCOUNT_NUMBER
- BILLING_HISTORY.ACCOUNT_NUMBER
- METER_READING.ACCOUNT_NUMBER
- METER_INFORMATION.ACCOUNT_NUMBER
- PAYMENTS.ACCOUNT_NUMBER
- COMPLAINTS.ACCOUNT_NUMBER
- CALLS.ACCOUNT_NUMBER
- CONTRACT.ACCOUNT_NUMBER

MPXN is used to maintain consistency across:
- BILLING_HISTORY
- METER_READING
- METER_INFORMATION
- CONTRACT

## Primary Keys
ACCOUNT_HEALTH       ACCOUNT_NUMBER + SNAPSHOT_DATE
ACCOUNT_BALANCE      ACCOUNT_NUMBER + BALANCE_DATE
BILLING_HISTORY      BILL_ID
METER_READING        READING_ID
METER_INFORMATION    METER_ID
PAYMENTS             PAYMENT_ID
COMPLAINTS           COMPLAINT_ID
CALLS                CALL_ID
CONTRACT             CONTRACT_ID

## Synthetic Data Generation Framework

The project includes a synthetic data generation framework to create realistic utility data without using any real customer information.

Why Synthetic Data?

Synthetic data is used because:

No real customer data is required
Data can be safely used for demos
Scenarios can be controlled and embedded
KPI movements can be tested
AI investigation logic can be validated
Hackathon and POC development becomes faster
Framework Capabilities

The framework can generate:

Utility accounts
Account types
Contract details
Billing records
Meter readings
Meter attributes
Payment transactions
Complaints
Calls
Account balance history
Account health snapshots
KPI monthly summary
Supported Account Types
Residential
Business
Residential Occupier
Business Occupier

## Embedded Business Scenarios

The synthetic dataset includes realistic utility business patterns.

## Debt-Related Scenarios
1. Failed Direct Debit payments increase debt.
2. Missed payments increase arrears.
3. Winter consumption increases bill amount.
4. Higher bill amount increases debt risk.
5. Affordability-flagged customers have higher missed payment probability.
6. Vulnerable customers may show higher support needs.
7. Contract expiry may impact payment behavior.
8. Repeated missed payments trigger collection calls.
9. Promise to Pay may reduce debt in future periods.

## Complaint-Related Scenarios
1. Estimated bills increase billing complaints.
2. Faulty meters increase meter issue complaints.
3. Sudden bill increases trigger complaint spikes.
4. Payment failures may increase payment complaints.
5. Debt collection activity may increase debt collection complaints.
6. High complaint accounts generate more inbound calls.

## KPI Calculation Logic

## Debt %
SELECT
    SNAPSHOT_DATE,
    COUNT(DISTINCT CASE WHEN DEBT_AMOUNT > 0 THEN ACCOUNT_NUMBER END) * 100.0/ COUNT(DISTINCT ACCOUNT_NUMBER) AS DEBT_PERCENT
FROM ACCOUNT_HEALTH
WHERE ACTIVE_ACCOUNT_FLAG = 'Y'
GROUP BY SNAPSHOT_DATE;

## Complaint Rate
SELECT
    MONTH(COMPLAINT_DATE) AS COMPLAINT_MONTH,
    COUNT(COMPLAINT_ID) * 100.0 /COUNT(DISTINCT ACCOUNT_NUMBER) AS COMPLAINT_RATE
FROM COMPLAINTS
GROUP BY MONTH(COMPLAINT_DATE);


For production use, Complaint Rate should be calculated using complaint count divided by total active accounts for the same period.

## Root Cause Analysis Logic

The root cause engine compares KPI movement between two time periods.

## Example Logic for Debt %
If Debt % increased:
1. Check failed payment trend.
2. Check missed payment count.
3. Check average bill amount.
4. Check estimated bill impact.
5. Check account type contribution.
6. Check affordability and vulnerability flags.
7. Check contract expiry effect.
8. Check collection calls and outcomes.
9. Rank drivers by impact.
10. Generate summary and recommendations.

## Example Logic for Complaint Rate
If Complaint Rate increased:
1. Check complaint type distribution.
2. Check estimated bill count.
3. Check meter fault rate.
4. Check bill spike accounts.
5. Check payment issue complaints.
6. Check debt collection complaints.
7. Check call volume.
8. Rank drivers by contribution.
9. Generate explanation and recommended actions.

## Example Investigation Output
User Question
Why did Complaint Rate increase in March?

## AI Investigation Summary
Complaint Rate increased mainly due to billing-related complaints and meter issue complaints.

Key findings:
1. Estimated bills increased by 19% compared to the previous month.
2. Billing complaints contributed 42% of total complaints.
3. Accounts with faulty meters had 2.3x higher complaint probability.
4. Residential accounts had the highest complaint volume.
5. Inbound complaint follow-up calls also increased during the same period.

Recommended actions:
1. Review accounts with repeated estimated bills.
2. Prioritize faulty meter resolution.
3. Improve proactive communication for high bill customers.
4. Monitor complaint-prone segments in the next billing cycle.

## Technical Implementation

## Backend
The backend is responsible for:
Loading synthetic datasets
Calculating KPIs
Detecting KPI movement
Running root cause analysis
Preparing investigation context
Sending context to the AI layer
Returning structured investigation output

## AI Layer

The AI layer is responsible for:
Understanding user questions
Selecting the correct KPI
Identifying relevant tables
Interpreting root cause output
Generating business-friendly explanations
Suggesting recommended actions

## UI Layer
The UI layer is responsible for:
Taking user questions
Displaying KPI movement
Showing AI investigation summary
Showing root cause drivers
Showing supporting evidence
Allowing user drill-down

## Suggested Technology Stack
Data Generation
Python
Pandas
NumPy
Faker

## Backend
Python
FastAPI
SQLAlchemy
Pandas

## AI Layer
LLM-based investigation agent
Prompt orchestration
Context builder
Root cause summarization

## Frontend UI
React
TypeScript
Tailwind CSS
Shadcn UI

## Data Storage Options
CSV for POC
SQLite for local demo
PostgreSQL for app integration
Databricks or Fabric Lakehouse for scale

## Suggested Repository Structure
Insight_Forge/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── ACCOUNT_HEALTH.csv
│   ├── ACCOUNT_BALANCE.csv
│   ├── BILLING_HISTORY.csv
│   ├── METER_READING.csv
│   ├── METER_INFORMATION.csv
│   ├── PAYMENTS.csv
│   ├── COMPLAINTS.csv
│   ├── CALLS.csv
│   ├── CONTRACT.csv
│   └── KPI_MONTHLY_SUMMARY.csv
│
├── synthetic_data_framework/
│   ├── config.py
│   ├── generate_accounts.py
│   ├── generate_billing.py
│   ├── generate_payments.py
│   ├── generate_complaints.py
│   ├── generate_meter_data.py
│   ├── generate_calls.py
│   ├── generate_contracts.py
│   └── main.py
│
├── backend/
│   ├── app.py
│   ├── kpi_engine.py
│   ├── root_cause_engine.py
│   ├── investigation_agent.py
│   └── data_loader.py
│
├── ui/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── package.json
│
├── documentation/
│   ├── data_dictionary.md
│   ├── architecture.md
│   ├── kpi_logic.md
│   └── investigation_examples.md
│
└── outputs/
    ├── validation_report.txt
    └── investigation_samples.json

## How to Run the Project

1. Clone the Repository
git clone https://github.com/your-username/Insight_Forge.git
cd Insight_Forge

2. Install Python Dependencies
pip install -r requirements.txt

3. Generate Synthetic Data
python synthetic_data_framework/main.py

4. Run Backend API
python backend/app.py

5. Run UI
cd ui
npm install
npm run dev

## Expected Output Files

After running the synthetic data framework, the following files should be generated:

ACCOUNT_HEALTH.csv
ACCOUNT_BALANCE.csv
BILLING_HISTORY.csv
METER_READING.csv
METER_INFORMATION.csv
PAYMENTS.csv
COMPLAINTS.csv
CALLS.csv
CONTRACT.csv
KPI_MONTHLY_SUMMARY.csv
VALIDATION_REPORT.txt

## Data Quality Checks

The framework performs the following validation checks:

1. No duplicate primary keys.
2. ACCOUNT_NUMBER is consistent across all tables.
3. MPXN is consistent across billing, meter, and contract tables.
4. DEBT_FLAG is Y only when DEBT_AMOUNT > 0.
5. ACTIVE_ACCOUNT_FLAG contains only Y or N.
6. SMART_METER_FLAG contains only Y or N.
7. ESTIMATED_FLAG contains only Y or N.
8. Payment date is not before contract start date.
9. Bill date is not before contract start date.
10. Complaint date is not before contract start date.
11. Debt amount and bill amount are realistic.
12. Business rules are reflected in generated patterns.

## Future Enhancements

Phase 1: Current POC
KPI investigation
Root cause analysis
Debt % analysis
Complaint Rate analysis
Synthetic utility data
Stakeholder UI
AI-generated explanations

Phase 2: Advanced AI Capability
Predictive KPI forecasting
Early warning alerts
Customer risk scoring
Automated recommendations
Natural language follow-up questions

Phase 3: Agentic Operations Intelligence
Autonomous KPI monitoring
Multi-KPI investigation
Automated stakeholder summaries
Action workflow generation
Integration with enterprise data systems

## Project Vision

Insight Forge transforms operational analytics from passive reporting into active investigation.

Instead of asking users to manually search across datasets, the AI agent automatically identifies what changed, why it changed, who is impacted, and what should be done next.

From "What happened?"
To "Why did it happen?"
To "What should we do next?"

## Final Summary

Insight Forge is an AI-powered KPI Investigation Agent for utility operations. It combines synthetic utility data, KPI calculation, root cause analysis, and a conversational UI to help stakeholders understand KPI movement in a faster and more actionable way.

The project demonstrates how AI can support business users by converting complex operational data into clear explanations, evidence-backed insights, and practical recommendations.
