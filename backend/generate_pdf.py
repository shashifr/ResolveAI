import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def create_pdf(filename="working_process.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, fontSize=18, spaceAfter=20, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name='Heading2Custom', fontSize=14, spaceAfter=10, spaceBefore=15, fontName="Helvetica-Bold"))
    
    Story = []
    
    # Title
    Story.append(Paragraph("ResolveAI: Working Process & Architecture", styles['CenterTitle']))
    Story.append(Spacer(1, 12))
    
    # Section 1: Overview
    Story.append(Paragraph("1. System Overview", styles['Heading2Custom']))
    overview = ("ResolveAI is a stateful, trust-gated Mixture-of-Experts (MoE) customer support engine. "
                "Instead of exposing a single LLM to a database (which invites hallucinations and prompt injection), "
                "ResolveAI strictly isolates reasoning from execution using a multi-node LangGraph state machine.")
    Story.append(Paragraph(overview, styles['Justify']))
    Story.append(Spacer(1, 12))
    
    # Section 2: The LangGraph State Machine
    Story.append(Paragraph("2. The LangGraph State Machine", styles['Heading2Custom']))
    langgraph_desc = ("Every incoming support query traverses a deterministic pipeline:")
    Story.append(Paragraph(langgraph_desc, styles['Justify']))
    
    pipeline = [
        ListItem(Paragraph("<b>Intake Node:</b> Sanitizes the incoming request and performs initial prompt-injection screening.", styles['Normal'])),
        ListItem(Paragraph("<b>Classifier Node:</b> Identifies the exact customer intent (e.g., 'refund_request', 'order_status').", styles['Normal'])),
        ListItem(Paragraph("<b>Context Retrieval:</b> Fetches relevant internal CRM data (e.g., Order ORD-1001 details) and Knowledge Base articles via semantic search.", styles['Normal'])),
        ListItem(Paragraph("<b>Resolver Node:</b> Generates a proposed action and calculates a mathematical confidence score.", styles['Normal'])),
        ListItem(Paragraph("<b>Safety Gate:</b> Intercepts high-risk requests. If the confidence is below the intent-specific threshold (or if it's a high-value transaction like a $100 refund), execution is halted and sent to the Human-in-the-Loop console.", styles['Normal'])),
        ListItem(Paragraph("<b>Execution Node:</b> Only reached if the safety gate passes. Safely executes the database mutation.", styles['Normal']))
    ]
    Story.append(ListFlowable(pipeline, bulletType='bullet', spaceAfter=10))
    Story.append(Spacer(1, 12))
    
    # Section 3: Mixture-of-Experts (MoE) Routing
    Story.append(Paragraph("3. Mixture-of-Experts (MoE) Routing Engine", styles['Heading2Custom']))
    moe_desc = ("To drastically reduce API costs while maintaining high intelligence, ResolveAI triages requests to different tiers of models:")
    Story.append(Paragraph(moe_desc, styles['Justify']))
    
    moe_tiers = [
        ListItem(Paragraph("<b>Tier 0 (Gemini 2.5 Flash):</b> Ultra-fast and cheap. Handles routine tasks like intent classification and simple FAQ responses.", styles['Normal'])),
        ListItem(Paragraph("<b>Tier 1 (Claude 3.5 Sonnet):</b> Balanced cost and reasoning. Manages logistics, order tracking, and mid-level account updates.", styles['Normal'])),
        ListItem(Paragraph("<b>Tier 2 (OpenAI o1 / Claude Opus):</b> Expensive frontier reasoning. Strictly reserved for high-risk queries, angry escalations, or massive refunds.", styles['Normal']))
    ]
    Story.append(ListFlowable(moe_tiers, bulletType='bullet', spaceAfter=10))
    Story.append(Spacer(1, 12))

    # Section 4: Cryptographic Audit Ledger
    Story.append(Paragraph("4. Cryptographic SHA-256 Audit Ledger", styles['Heading2Custom']))
    ledger_desc = ("Absolute accountability is required for enterprise AI. Every node transition, token cost metric, and database action "
                   "is logged in a tamper-evident cryptographic ledger. Each block is hashed using SHA-256 and mathematically chained to the `prev_hash` of the previous block. "
                   "If any internal employee or attacker attempts to retroactively alter a log (e.g., to cover up an unauthorized refund), the hash chain breaks instantly, "
                   "and the Dashboard rejects the verified badge. To ensure GDPR compliance (Right to be Forgotten), Customer PII is encrypted with a rotatable key before hashing. "
                   "Shredding the key anonymizes the data without breaking the mathematical integrity of the chain.")
    Story.append(Paragraph(ledger_desc, styles['Justify']))
    
    doc.build(Story)
    print(f"PDF generated successfully at {os.path.abspath(filename)}")

if __name__ == "__main__":
    create_pdf()
