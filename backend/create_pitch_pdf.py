import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Define Palette (Modern slate blue and deep indigo theme)
PRIMARY_COLOR = colors.HexColor('#1E3A8A')    # Deep Indigo
SECONDARY_COLOR = colors.HexColor('#0F766E')  # Dark Teal
TEXT_COLOR = colors.HexColor('#1E293B')       # Slate Dark
LIGHT_BG = colors.HexColor('#F8FAFC')         # Off-white
BORDER_COLOR = colors.HexColor('#E2E8F0')     # Light Gray
ACCENT_COLOR = colors.HexColor('#7C3AED')     # Purple
WHITE = colors.HexColor('#FFFFFF')

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render "Page X of Y" and running headers.
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
            # Draw a subtle background accent on the cover page
            self.setFillColor(colors.HexColor('#EEF2F6'))
            self.rect(0, 0, 18, 792, fill=True, stroke=False) # Vertical accent strip on left
            self.restoreState()
            return
            
        # Draw header rule and text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(SECONDARY_COLOR)
        self.drawString(54, 750, "AI CUSTOMER SUPPORT — INBOX HACKATHON PITCH STRATEGY")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Draw footer rule and page number
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 9)
        self.setFillColor(TEXT_COLOR)
        self.drawString(54, 30, "Confidential — Hackathon Pitch Deck Support")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 30, page_str)
        self.restoreState()

def build_pdf(filename="inbox_hackathon_pitch.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54, # 0.75 inch
        rightMargin=54,
        topMargin=72,  # 1.0 inch for header space
        bottomMargin=72 # 1.0 inch for footer space
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=PRIMARY_COLOR,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#475569'),
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY_COLOR,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    quote_style = ParagraphStyle(
        'Quote_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#0F766E'),
        leftIndent=20,
        rightIndent=20,
        spaceBefore=8,
        spaceAfter=12
    )
    
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        leftIndent=15,
        spaceAfter=6
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("AI CUSTOMER SUPPORT", ParagraphStyle('Upper', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=SECONDARY_COLOR, spaceAfter=10)))
    story.append(Paragraph("Inbox Hackathon Pitch Strategy & Guide", title_style))
    story.append(Paragraph("Automating 80% of support inboxes safely with stateful agent graphs, Mixture-of-Experts routing, and cryptographic logs.", subtitle_style))
    
    # Thin divider line
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR, spaceBefore=10, spaceAfter=20))
    
    metadata_data = [
        [Paragraph("<b>Target Event:</b> Inbox Hackathon", body_style), Paragraph("<b>Release Version:</b> v1.0", body_style)],
        [Paragraph("<b>Author:</b> Product Pitch & Strategy Team", body_style), Paragraph("<b>Date:</b> July 2026", body_style)]
    ]
    meta_table = Table(metadata_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 150))
    
    # Quick callout box on cover
    callout_data = [[
        Paragraph("<b>Key Concept:</b> Pitch AI Customer Support not just as another AI chatbot, but as a <b>highly secure, cost-optimized, enterprise-ready automation engine</b> that bridges the speed of AI with the compliance of cryptographic hashing and Human-in-the-Loop oversight.", body_style)
    ]]
    callout_table = Table(callout_data, colWidths=[500])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BFDBFE')),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(callout_table)
    story.append(PageBreak())
    
    # ------------------ SECTION 1: THE ANGLE ------------------
    story.append(Paragraph("1. The Pitch Angle: Safe, Semi-Autonomous Inbox Scaling", h1_style))
    story.append(Paragraph("In an <b>Inbox Hackathon</b>, judges evaluate projects on productivity, realism, and handling inbox overload. Typical 'AI auto-responders' fail because businesses are terrified of hallucinations, unauthorized actions (e.g. issuing massive refunds), and general lack of accountability. AI Customer Support solves this trust deficit.", body_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>The Winning Narrative to Deliver:</b>", h2_style))
    story.append(Paragraph('"Companies want to automate their support inboxes, but they are terrified of hallucinations, accidental refunds, and lack of accountability. AI Customer Support solves this with a Multi-Tier Mixture-of-Experts (MoE) system that operates safely using Confidence Gating and a Cryptographic Audit Ledger to guarantee absolute decision integrity."', quote_style))
    
    # ------------------ SECTION 2: SLIDE OUTLINE ------------------
    story.append(Paragraph("2. Slide-by-Slide Pitch Deck Outline", h1_style))
    
    slides = [
        ("Slide 1: Title & Vision", 
         "<b>Visual:</b> Sleek dark-mode mockup of the Next.js AI Customer Support Dashboard.<br/>"
         "<b>Pitch Focus:</b> Introduce the core promise: Trust-Gated Support Inbox Automation."),
        
        ("Slide 2: The Core Problem", 
         "<b>Visual:</b> Split screen: Customer waiting 12 hours vs. Support team drowning in ticket costs.<br/>"
         "<b>Pitch Focus:</b> Inbox Overload (70% repetitive), Cost vs. Quality Dilemma (Frontier LLMs are too expensive; cheap ones are too risky), and the Trust Gap (the black-box AI issue)."),
        
        ("Slide 3: The Solution (AI Customer Support)", 
         "<b>Visual:</b> Graph flowchart showing incoming messages flowing through LangGraph state machine.<br/>"
         "<b>Pitch Focus:</b> Stateful orchestration, intent-specific gating, and Human-in-the-Loop console for 1-click approvals on edge cases."),
        
        ("Slide 4: Cost Optimization via Mixture-of-Experts", 
         "<b>Visual:</b> ROI chart showing 80% cost savings.<br/>"
         "<b>Pitch Focus:</b> Explain how Tier 0 (Haiku-class) classifies, Tier 1 (Sonnet/Flash) handles basic transactions, and Tier 2 (Pro/Opus) handles high-risk contexts (angry customers, high refunds)."),
        
        ("Slide 5: Cryptographic Audit Ledger (Safety)", 
         "<b>Visual:</b> Blockchain-like hash chain connecting node-by-node decisions.<br/>"
         "<b>Pitch Focus:</b> Real-time tamper-evident compliance. Every decision is mathematically chained using SHA-256. If a record is tampered with, the verification chain breaks immediately."),
        
        ("Slide 6: Live Demo & Impact Metrics", 
         "<b>Visual:</b> Channel simulator (Email, Live Chat, Voice) and live execution visualization.<br/>"
         "<b>Pitch Focus:</b> Highlight Trust Autonomy Rate, total API cost saved, and average response times reduced from hours to 2 seconds.")
    ]
    
    for title, text in slides:
        story.append(Paragraph(f"• <b>{title}</b>", h2_style))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 4))
        
    story.append(PageBreak())
    
    # ------------------ SECTION 3: TECH SPECS & MOE ------------------
    story.append(Paragraph("3. Technical Architecture & MoE Tiers", h1_style))
    story.append(Paragraph("AI Customer Support uses a cost-performance optimized routing mechanism. Below is the active routing layout utilized by our LangGraph engine:", body_style))
    
    moe_data = [
        ["Tier", "Model Class", "Cost (per 1K tkn In/Out)", "Primary Use Cases"],
        ["Tier 0", "Haiku-class / Cheap", "$0.00025 / $0.00125", "Intent Classification, General FAQs, routing"],
        ["Tier 1", "Sonnet/Gemini Flash", "$0.00300 / $0.01500", "Standard transactions (Order Status, shipping delay)"],
        ["Tier 2", "Opus/Gemini Pro", "$0.01500 / $0.07500", "High-risk (Legal threats, high-value refunds, low-confidence)"]
    ]
    
    moe_table = Table(moe_data, colWidths=[55, 135, 120, 190])
    moe_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
    ]))
    story.append(moe_table)
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 4: 3-MIN SCRIPT ------------------
    story.append(Paragraph("4. 3-Minute Verbal Pitch Script", h1_style))
    
    script_sections = [
        ("0:00 - 0:45 | The Hook & Problem", 
         "Every day, customer service inboxes are flooded with thousands of messages. For businesses, this is an expensive, slow bottleneck. "
         "But replacing humans with autonomous AI support leads to a terrifying trust gap. How do you stop an LLM from hallucinating refund policies, "
         "or worse, going rogue and issuing massive refunds automatically? And how do you do this without running up thousands of dollars in frontier "
         "model API costs? Meet AI Customer Support, a multi-tier customer support automation dashboard that bridges the gap between speed, safety, and operational budget."),
        
        ("0:45 - 1:45 | The Technology", 
         "Under the hood, AI Customer Support uses a stateful agentic pipeline built with LangGraph. When an email or chat lands in the inbox, "
         "we process it using: First, Mixture-of-Experts routing, reserving frontier models like Gemini Pro exclusively for high-risk tickets, "
         "angry customers, or legal threats, saving up to 80% on token costs. Second, Confidence Gating, halting execution if safety check thresholds "
         "are violated. Third, the Human Console, where low-confidence resolutions are presented as pre-staged drafts for 1-click human execution."),
        
        ("1:45 - 2:45 | Security & Demo", 
         "But what makes AI Customer Support truly enterprise-grade is our Cryptographic Audit Ledger. Every single decision—which model was called, the "
         "confidence score, the tools used—is hashed and mathematically chained to the previous action using SHA-256. This creates an immutable, "
         "tamper-evident audit log. If someone tries to modify the database history, the verification chain fails instantly. Let's look at the dashboard "
         "in action showing our simulator running node-by-node and checking off our cryptographic ledger blocks."),
        
        ("2:45 - 3:00 | Conclusion", 
         "AI Customer Support makes inbox automation secure, cost-effective, and fully auditable. It's the future of trust-gated AI customer operations. Thank you!")
    ]
    
    for time_title, text in script_sections:
        story.append(Paragraph(f"<b>[{time_title}]</b>", h2_style))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 5))
        
    story.append(PageBreak())
    
    # ------------------ SECTION 5: Q&A PLAYBOOK ------------------
    story.append(Paragraph("5. Q&A Defense Playbook", h1_style))
    story.append(Paragraph("Be prepared for tough questions from the judging panel. Here are targeted defenses based on AI Customer Support's actual design:", body_style))
    
    qa_data = [
        ["Judge's Question", "Your Bulletproof Answer"],
        [
            "Why not just build a simple agent prompt?",
            "A single prompt cannot handle multi-step workflows like database retrieval, transaction safety checks, and selective escalation. Using LangGraph, we break the workflow into distinct state machines, allowing us to enforce separate confidence gates and models for different sub-tasks."
        ],
        [
            "Why is the Cryptographic Audit Ledger necessary?",
            "In regulated industries (like FinTech or Healthcare), audit trails are legally mandated. If an AI issues a credit or cancels an account, regulators need to verify who authorized it, what context the AI had, and that the logs haven't been tampered with. Our ledger makes AI actions mathematically auditable."
        ],
        [
            "How does the Voice Simulator fit into an inbox?",
            "An inbox is no longer just email. Modern support channels aggregate tickets from emails, chat widgets, and voice transcription services. Our system normalizes all channels into the same structured Intake Node, showing unified omni-channel tracking."
        ],
        [
            "What happens if the model fails the cryptographic chain validation?",
            "If any hash doesn't match the signature chain, the Next.js dashboard immediately flags the ticket with a visual warning, and the backend halts auto-execution for all subsequent tickets related to that account until a manual security audit is completed."
        ]
    ]
    
    qa_table = Table(qa_data, colWidths=[180, 320])
    qa_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 8),
    ]))
    story.append(qa_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    build_pdf()
    print("PDF Generation complete.")
