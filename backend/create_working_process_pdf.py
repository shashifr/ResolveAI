import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Define Palette (Clean tech theme: deep navy primary, teal secondary, charcoal text)
PRIMARY_COLOR = colors.HexColor('#0F172A')    # Slate 900
SECONDARY_COLOR = colors.HexColor('#0284C7')  # Sky 600
TEXT_COLOR = colors.HexColor('#334155')       # Slate 700
LIGHT_BG = colors.HexColor('#F8FAFC')         # Slate 50
BORDER_COLOR = colors.HexColor('#E2E8F0')     # Slate 200
ACCENT_COLOR = colors.HexColor('#4F46E5')     # Indigo 600
WHITE = colors.HexColor('#FFFFFF')

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to render page numbers ("Page X of Y") and headers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Don't draw headers/footers on page 1 (cover page)
        if self._pageNumber == 1:
            # Draw a subtle blue vertical bar on the left edge
            self.setFillColor(SECONDARY_COLOR)
            self.rect(0, 0, 15, 792, fill=True, stroke=False)
            self.restoreState()
            return
            
        # Draw header rule and text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(SECONDARY_COLOR)
        self.drawString(54, 750, "AI CUSTOMER SUPPORT — ARCHITECTURE & WORKING PROCESS")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Draw footer rule and page number
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_COLOR)
        self.drawString(54, 30, "Confidential — System Reference Manual")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 30, page_str)
        self.restoreState()

def build_process_pdf(filename="working_process.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,  # 0.75 in
        rightMargin=54,
        topMargin=72,   # 1.0 in
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom typography
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=PRIMARY_COLOR,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=TEXT_COLOR,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=SECONDARY_COLOR,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_COLOR,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        backColor=LIGHT_BG,
        borderColor=BORDER_COLOR,
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 120))
    story.append(Paragraph("TECHNICAL REFERENCE MANUAL", ParagraphStyle('Upper', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=ACCENT_COLOR, spaceAfter=8)))
    story.append(Paragraph("AI Customer Support Agent", title_style))
    story.append(Paragraph("System Architecture, LangGraph State Workflows, Mixture-of-Experts (MoE) Routing, and Cryptographic Ledger Integrity", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceBefore=10, spaceAfter=20))
    
    meta_data = [
        [Paragraph("<b>Document Type:</b> System Specifications", body_style), Paragraph("<b>Version:</b> v1.0.0", body_style)],
        [Paragraph("<b>Author:</b> Technical Architecture Team", body_style), Paragraph("<b>Release Date:</b> July 2026", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 160))
    
    callout_data = [[
        Paragraph("<b>Abstract:</b> This document outlines the backend execution flow and design aesthetics of the AI Customer Support project. The platform integrates stateful multi-tier LLM routing via LangGraph, intent-based confidence gating, a real-time human console intervention workflow, and an immutable cryptographic audit ledger verifying every decision step.", body_style)
    ]]
    callout_table = Table(callout_data, colWidths=[500])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(callout_table)
    story.append(PageBreak())
    
    # ------------------ SECTION 1: SYSTEM OVERVIEW & INBOUND INTAKE ------------------
    story.append(Paragraph("1. System Overview & Inbound Intake", h1_style))
    story.append(Paragraph("The AI Customer Support platform provides an enterprise-ready ticket resolution framework. Incoming support requests from channels such as Email, Live Chat, and Voice Call Transcripts are ingested, normalized, and processed. The system is designed to achieve maximum autonomy while strictly mitigating risks associated with automated AI operations (such as rogue tool execution or refund leakage).", body_style))
    
    story.append(Paragraph("<b>The Pipeline at a Glance:</b>", h2_style))
    story.append(Paragraph("• <b>Ingestion:</b> Tickets are registered in the local SQLite database. A unique cryptographic block is initialized in the audit ledger.", bullet_style))
    story.append(Paragraph("• <b>Classification:</b> Ticket text is analyzed to detect user intent, extract metadata entities (such as order IDs, subscription IDs, and dollar amounts), and calculate sentiment/risk flags.", bullet_style))
    story.append(Paragraph("• <b>Context Retreival:</b> System loads database information regarding the user (CRM profiles, active subscriptions, recent orders) and searches the local Knowledge Base for FAQ matching.", bullet_style))
    story.append(Paragraph("• <b>Model Routing:</b> Tiers route requests dynamically according to intent and risk profile to balance speed, cost, and safety.", bullet_style))
    story.append(Paragraph("• <b>Confidence Gating:</b> The resolution score must exceed the threshold set for the specific intent. If it falls below, it is securely escalated to the human agent dashboard.", bullet_style))
    story.append(Spacer(1, 10))

    # ------------------ SECTION 2: STATEFUL LANGGRAPH WORKFLOW ------------------
    story.append(Paragraph("2. Stateful LangGraph Engine Workflow", h1_style))
    story.append(Paragraph("The core processing pipeline is modeled as a stateful graph using <b>LangGraph</b>. Each node in the graph represents a distinct system function that modifies the shared ticket state. Transactions are transactional and fully auditable.", body_style))
    
    story.append(Paragraph("<b>Graph Node Breakdown:</b>", h2_style))
    
    story.append(Paragraph("<b>1. Intake Node (intake_node):</b><br/>"
                           "Creates the initial database ticket entry. Sets the status to <code>Open</code> and token costs to 0. Generates the first block of the SHA-256 hash verification chain.", body_style))
    
    story.append(Paragraph("<b>2. Classifier Node (classify_node):</b><br/>"
                           "Analyzes text to extract intents (e.g. <code>refund_request</code>, <code>subscription_cancel</code>, <code>order_status</code>) and entities. Checks for risk flags (angry language, legal threats, high refund values). High risks automatically lower confidence parameters.", body_style))
    
    story.append(Paragraph("<b>3. Context Retriever (context_retriever_node):</b><br/>"
                           "Queries customer profiles, order history, subscription statuses, and relevant local FAQ articles. This creates a unified context block passed to the resolving agent.", body_style))
    
    story.append(Paragraph("<b>4. Resolution Agent (resolve_node):</b><br/>"
                           "Chooses the optimal LLM class (Mixture-of-Experts) to draft a response message and propose actions (e.g., <code>issue_refund</code> or <code>cancel_subscription</code>). Details the rationale behind its decisions.", body_style))
    
    story.append(Paragraph("<b>5. Confidence Gate (gate_node):</b><br/>"
                           "Inspects the resolution confidence score against predefined intent thresholds. If it passes, the ticket routes to autonomous execution; if it fails (or carries risk flags), it escalates.", body_style))
    
    story.append(Paragraph("<b>6. Execution Node (execute_node):</b><br/>"
                           "Executes backend database changes automatically for high-confidence tickets. For escalated tickets, it holds changes, logs the draft response, and pushes the ticket to the Human Console.", body_style))
    
    story.append(PageBreak())
    
    # ------------------ SECTION 3: MIXTURE-OF-EXPERTS (MOE) ROUTING ------------------
    story.append(Paragraph("3. Mixture-of-Experts (MoE) Routing & Costs", h1_style))
    story.append(Paragraph("To optimize API token expenditure and response latency while maintaining absolute resolution quality, the system routes requests through three distinct model tiers based on intent, classification, and safety risk profiles:", body_style))
    
    moe_data = [
        ["Model Class / Tier", "Avg Cost per 1K Tkns", "Primary Intents & Triggers"],
        ["Tier 0: Haiku-class (Cheap)", "$0.00025 / $0.00125", "Basic classification, general FAQ resolution, low-complexity routing."],
        ["Tier 1: Sonnet-class (Standard)", "$0.00300 / $0.01500", "Standard transactional workflows (Order status lookup, shipping delays, simple refund calculations)."],
        ["Tier 2: Opus-class (Frontier)", "$0.01500 / $0.07500", "High-risk scenarios, low classification confidence, legal threats, angry customers, and high-value refund reviews."]
    ]
    
    moe_table = Table(moe_data, colWidths=[140, 120, 240])
    moe_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
    ]))
    story.append(moe_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Intent-Specific Confidence Thresholds:</b>", h2_style))
    story.append(Paragraph("• <b>order_status</b>: 0.80 | <b>shipping_delay</b>: 0.80 | <b>account_access</b>: 0.80", bullet_style))
    story.append(Paragraph("• <b>refund_request</b>: 0.85 (Refunds > $50 are immediately flagged for human review regardless of score)", bullet_style))
    story.append(Paragraph("• <b>subscription_cancel</b>: 0.90 (High-strict retention policy for customer retention analysis)", bullet_style))
    story.append(Spacer(1, 10))

    # ------------------ SECTION 4: CRYPTOGRAPHIC LEDGER ------------------
    story.append(Paragraph("4. Cryptographic Audit Ledger Chaining", h1_style))
    story.append(Paragraph("For security and regulatory compliance, the system records every state transition inside a tamper-evident, SHA-256 hashed ledger chain. Each state modification writes an entry to the <code>audit_logs</code> table, pointing back to the previous hash.", body_style))
    
    story.append(Paragraph("<b>The Hashing Chain Formula:</b>", h2_style))
    story.append(Paragraph("<code>Current Hash = SHA-256(prev_hash | ticket_id | node_name | input_summary | model_used | token_cost | confidence | action_taken)</code>", code_style))
    
    story.append(Paragraph("<b>Ledger Validation Mechanism:</b>", h2_style))
    story.append(Paragraph("When an agent opens a ticket in the Human Console dashboard, the Next.js frontend retrieves the entire history of the ticket's audit logs. It recalculates the hashes from the genesis block onward. If any value in the database has been modified retroactively, the verification chain breaks. The UI visually marks this state with a green checkmark (Verified Ledger) or a red warning sign (Tampered Log).", body_style))
    
    story.append(Spacer(1, 10))

    # ------------------ SECTION 5: DATABASE SCHEMA & CONSOLE ------------------
    story.append(Paragraph("5. Database Schema & Console Features", h1_style))
    story.append(Paragraph("The SQL database represents relational mappings between key system components:", body_style))
    
    story.append(Paragraph("• <b>Customer:</b> Stores names, email, and phone contact cards.", bullet_style))
    story.append(Paragraph("• <b>Order:</b> Details order history, tracking IDs, addresses, and purchase amounts.", bullet_style))
    story.append(Paragraph("• <b>Subscription:</b> Tracks active, cancelled, or trial software licenses and plans.", bullet_style))
    story.append(Paragraph("• <b>Ticket / Message:</b> Keeps conversations, channels, status, and accumulated API costs.", bullet_style))
    story.append(Paragraph("• <b>AuditLog:</b> Holds the immutable cryptographic blocks for chain verification.", bullet_style))
    
    story.append(Paragraph("<b>Human Console Features:</b>", h2_style))
    story.append(Paragraph("The Next.js Frontend dashboard features real-time metric counters (Autonomy Rate, Costs Saved, Response Speedups), channel simulation boxes (Email forms, Transcript-based audio playback, Chat widgets), and a queue of Escalated Tickets. Human agents can review system-proposed drafts and confirm actions with one click.", body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=10, spaceAfter=20))
    story.append(Paragraph("<i>End of Reference Manual. AI Customer Support System Specification Guide.</i>", ParagraphStyle('FooterText', parent=body_style, alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=8)))

    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    build_process_pdf()
    print("PDF Generation complete.")
