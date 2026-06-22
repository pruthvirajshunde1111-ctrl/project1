SAMPLE_DOCUMENTS = [
    # 1-5: Normal documents (should work fine)
    {
        "id": "doc_001",
        "source": "contract-standard",
        "text": """SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on January 15, 2025, by and between Acme Corp ("Company") and Jane Smith ("Consultant").

1. SERVICES: Consultant shall provide software development services as described in Exhibit A.
2. COMPENSATION: Company shall pay Consultant $150 per hour, not to exceed $120,000 annually.
3. TERM: This Agreement begins on February 1, 2025 and ends on January 31, 2026.
4. CONFIDENTIALITY: Consultant shall not disclose Company's proprietary information.
5. TERMINATION: Either party may terminate with 30 days written notice.

IN WITNESS WHEREOF, the parties have executed this Agreement.

_________________________        _________________________
Jane Smith                        Acme Corp
Date: Jan 15, 2025                Date: Jan 15, 2025""",
    },
    {
        "id": "doc_002",
        "source": "invoice-standard",
        "text": """INVOICE #INV-2025-0042

From: TechSolutions Inc.
To: MegaCorp Ltd.
Date: March 12, 2025

Description                    Quantity    Unit Price    Total
Server Maintenance - March       1         $5,000      $5,000.00
Cloud Storage (500GB)            3         $250          $750.00
Consulting (40 hrs)             40         $200        $8,000.00
Software Licenses                5         $1,200      $6,000.00

Subtotal:                                             $19,750.00
Tax (8.5%):                                            $1,678.75
Total Due:                                            $21,428.75

Payment Terms: Net 30
Due Date: April 11, 2025""",
    },
    {
        "id": "doc_003",
        "source": "report-quarterly",
        "text": """Q1 2025 ENGINEERING REPORT

Author: Dr. Alan Turing
Date: April 5, 2025

Executive Summary:
Engineering completed 12 of 15 milestones this quarter. Team velocity increased by 22%.

Key Findings:
1. Microservices migration reduced deployment time by 40%.
2. Test coverage improved from 72% to 88%.
3. Two critical security vulnerabilities were identified and patched.
4. Customer-reported bugs decreased by 35% month-over-month.

Risks:
- Hiring freeze may impact Q2 deliverables
- Legacy database migration behind schedule by 2 weeks

Recommendations:
- Increase investment in CI/CD pipeline
- Hire 2 additional SRE engineers
- Begin technical debt reduction initiative

Budget: $420,000 spent of $500,000 allocated (84% utilization)""",
    },
    {
        "id": "doc_004",
        "source": "correspondence-legal",
        "text": """March 1, 2025

From: Sarah Johnson, Esq.
Johnson & Associates
1423 Legal Ave, Suite 200
New York, NY 10001

To: Board of Directors
NexGen Technologies Inc.

Re: Legal Opinion on Patent Infringement Claim

Dear Board Members,

Following our review of the patent infringement claim filed by InnoPatents LLC (Case #2025-CV-0892), we offer the following analysis.

InnoPatents alleges that your product "DataFlow Pro" infringes on their patent US 11,234,567 for "Real-time Data Streaming with Predictive Caching."

Our assessment indicates that while there are surface-level similarities, the specific implementation differs in three material ways:
1. DataFlow Pro uses hash-based indexing rather than B-tree indexing.
2. Our caching mechanism is event-driven, not timer-based.
3. The predictive algorithm uses different statistical methods.

Recommendation: We recommend filing a motion for summary judgment. The likelihood of a favorable outcome is approximately 75%.

Please contact us to schedule a strategy meeting.

Sincerely,
Sarah Johnson""",
    },
    {
        "id": "doc_005",
        "source": "invoice-normal",
        "text": """RECEIPT #RCP-3341
Date: June 5, 2025

From: QuickMart Online
To: Customer #88291

Items:
- Wireless Mouse (1x)        $29.99
- USB-C Hub (1x)             $45.00
- Laptop Stand (2x)          $59.98
- Shipping                   $5.99

Total: $140.96
Payment: Visa ****-4242
Thank you for your purchase!""",
    },
    # 6-10: Failure-inducing documents
    {
        "id": "doc_006",
        "source": "contract-no-dates",
        "text": """CONFIDENTIALITY AGREEMENT

This Agreement is entered into between DataSecure Inc. and ThirdParty Analytics.

The Receiving Party agrees not to disclose any Confidential Information received from the Disclosing Party.

Confidential Information includes all technical data, business plans, and customer lists.

This Agreement shall remain in effect for a period of [REDACTED] years.

Either party may terminate this agreement upon written notice.

This Agreement constitutes the entire understanding between the parties.

Signed:
__________________          __________________
DataSecure Inc.             ThirdParty Analytics""",
    },
    {
        "id": "doc_007",
        "source": "invoice-mixed-currencies",
        "text": """INVOICE #2025-GLOBAL

From: WorldTrade Corp
To: GlobalBuyer LLC
Date: April 15, 2025

Items:
1. Software License (annual)        $12,000 USD
2. Consulting Services (80 hrs)      €8,000 EUR
3. Cloud Infrastructure              £3,500 GBP
4. Training Materials               ¥150,000 JPY
5. Support Package                   $2,400 USD

Subtotal (converted at market rates): ~$24,850 USD
Processing Fee: $50 USD
Total Due: Please remit in USD equivalent

Payment Terms: Net 45
Note: Exchange rates applied at time of payment""",
    },
    {
        "id": "doc_008",
        "source": "ambiguous-doc",
        "text": """PROJECT PROPOSAL / SERVICE ORDER

Parties: WebDev Agency and ClientCorp
Date: March 22, 2025

This document serves as both a proposal and an order form.

Scope: Design and development of a 12-page website with CMS integration.

This is not a binding contract until signed by both parties.

Pricing:
- Design phase: $15,000
- Development phase: $25,000
- CMS integration: $8,000
- Total estimated: $48,000

Timeline: 8-10 weeks

Terms: 50% deposit upon approval, 50% upon completion.

This agreement is governed by the laws of the State of Delaware.

Signature: __________________  Date: _________
Client signature required for work to commence.""",
    },
    {
        "id": "doc_009",
        "source": "correspondence-contradictory",
        "text": """INTER-OFFICE MEMO

From: Management
To: All Staff
Date: January 10, 2025
Subject: New Remote Work Policy

Effective immediately, all employees must return to the office full-time, effective January 15, 2025.

Please note that remote work remains fully available and we continue to support flexible working arrangements.

Employees should submit their office attendance schedule by January 12. However, no schedule is required if you plan to work remotely.

All exceptions must be approved by department heads. No exceptions will be made under any circumstances.

If you have questions, please don't hesitate to contact HR. But please direct all inquiries to your manager instead.

This policy supersedes all previous communications about remote work, while maintaining all previous policies unchanged.""",
    },
    {
        "id": "doc_010",
        "source": "contract-long-context",
        "text": """MASTER SERVICES AGREEMENT

This Master Services Agreement (MSA) is entered into on October 1, 2024, by and between Enterprise Solutions Inc. ("Client") and CloudProvider LLC ("Provider").

1. SERVICES
Provider shall deliver cloud infrastructure services as outlined in individual Statements of Work (SOWs).

2. TERM
Initial term: 36 months from October 1, 2024.

3. PAYMENT
Monthly fee: $45,000 USD for base services.
Additional usage billed at published rates.
Payment due within 30 days of invoice.

4. SERVICE LEVEL AGREEMENTS
4.1 Uptime Guarantee: 99.99% for production environments.
4.2 Response Times: Critical issues < 15 minutes, High < 1 hour, Medium < 4 hours, Low < 24 hours.
4.3 Credits: If uptime falls below 99.9%, Client receives 5% credit. Below 99.0%, 10% credit.

5. DATA PROTECTION
Provider shall maintain SOC 2 Type II certification.
Data encryption at rest and in transit.
Monthly security audits.

6. INTELLECTUAL PROPERTY
Each party retains ownership of its pre-existing IP.
Deliverables IP transfers to Client upon full payment.

7. LIMITATION OF LIABILITY
Neither party shall be liable for indirect damages.
Total liability limited to fees paid in the preceding 12 months.

8. TERMINATION
Either party may terminate for material breach with 60 days cure period.
Client may terminate for convenience with 90 days notice.
Provider may terminate only for non-payment after 60 days delinquency.

9. CONFIDENTIALITY
Confidential information protected for 5 years.
Each party shall use reasonable care to protect confidential information.

10. NON-COMPETE
During the term and for 12 months after, Provider shall not provide competitive services to Client's competitors listed in Exhibit A.

11. INSURANCE
Provider shall maintain: General Liability ($2M), Professional Liability ($5M), Cyber Insurance ($5M).

12. GOVERNING LAW
This agreement shall be governed by the laws of the State of Delaware.

13. DISPUTE RESOLUTION
Any disputes shall first attempt mediation through JAMS.
If unresolved, binding arbitration in Wilmington, DE.
Class action waiver applies.

14. FORCE MAJEURE
Neither party liable for delays caused by events beyond reasonable control.

15. ENTIRE AGREEMENT
This MSA together with all SOWs constitutes the entire agreement.

16. AMENDMENTS
Amendments must be in writing and signed by both parties.

17. WAIVER
Failure to enforce any provision does not constitute a waiver.

18. SEVERABILITY
If any provision is held invalid, the remainder continues in effect.

19. ASSIGNMENT
Neither party may assign this agreement without the other's written consent.
However, either party may assign in connection with a merger or acquisition.

20. NOTICES
All notices shall be in writing and sent to the registered addresses of each party.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

Enterprise Solutions Inc.
Signature: __________________
Name: John Smith
Title: VP of Engineering

CloudProvider LLC
Signature: __________________
Name: Jane Doe
Title: Chief Revenue Officer

Additional terms incorporated by reference:
- Exhibit A: List of Competitors (attached separately)
- Exhibit B: Pricing Schedule (attached separately)
- Exhibit C: Technical Specifications (attached separately)
- Exhibit D: Data Processing Addendum (attached separately)
- Exhibit E: Security Requirements (attached separately)""",
    },
]
