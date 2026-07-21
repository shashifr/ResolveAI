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
    
    def make_slide_block(slide_num, title, headline, visual, bullets, script):
        story_nodes = []
        # Header Table
        header_data = [[
            Paragraph(f"<b>SLIDE {slide_num}: {title.upper()}</b>", ParagraphStyle('SlideHeader', fontName='Helvetica-Bold', fontSize=10, textColor=WHITE))
        ]]
        header_table = Table(header_data, colWidths=[500])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story_nodes.append(header_table)
        
        # Headline
        story_nodes.append(Spacer(1, 4))
        story_nodes.append(Paragraph(f"<i>Core Headline:</i> <b>{headline}</b>", ParagraphStyle('SlideHeadline', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=SECONDARY_COLOR)))
        story_nodes.append(Spacer(1, 4))
        
        # Split content: bullets and visual layout
        bullet_text = "<br/>".join([f"• {b}" for b in bullets])
        content_data = [
            [
                Paragraph(f"<b>Key Bullet Points:</b><br/>{bullet_text}", ParagraphStyle('SlideBullets', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=TEXT_COLOR)),
                Paragraph(f"<b>Visual Layout / Mockup:</b><br/>{visual}", ParagraphStyle('SlideVisual', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=TEXT_COLOR))
            ]
        ]
        content_table = Table(content_data, colWidths=[250, 250])
        content_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story_nodes.append(content_table)
        story_nodes.append(Spacer(1, 4))
        
        # Speaker Script callout
        script_data = [[
            Paragraph(f"<b>Verbal Pitch Script (Speaker Notes):</b><br/>\"{script}\"", ParagraphStyle('SlideScript', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8.5, leading=11, textColor=colors.HexColor('#0F766E')))
        ]]
        script_table = Table(script_data, colWidths=[500])
        script_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story_nodes.append(script_table)
        story_nodes.append(Spacer(1, 15))
        
        return KeepTogether(story_nodes)

    slides_data = [
        (
            1,
            "Title & Vision",
            "Trust-Gated Support Inbox Automation",
            "Sleek dark-mode mockup of the Next.js Agent Dashboard showing: 'LangGraph Platform: ACTIVE', '82% Autonomy Rate', 'Avg Latency: 1.8s', and 'Cryptographic Chain Signature: [VERIFIED]'.",
            [
                "Auto-resolves 80%+ of inbox inquiries instantly using state-of-the-art orchestrations.",
                "Leverages Model Context Protocol (MCP) to access CRM and SQLite databases in real time.",
                "Protects customer trust with intent-specific confidence gates and continuous ledger signing."
            ],
            "Hello judges. Customer support is a massive bottleneck. Businesses want automation, but they are terrified of hallucinating agents executing rogue actions. Today, we present AI Customer Support: a trust-gated inbox automation engine built on LangGraph Platform and Model Context Protocol, resolving 80% of support queries safely, cost-effectively, and with complete mathematical auditability."
        ),
        (
            2,
            "The Core Problem",
            "The Cost, Speed, and Security Dilemma",
            "A triangular trade-off diagram (Speed, Cost, Security) showing that typical AI bots are fast/cheap but expose systems to security vulnerabilities like prompt injection or data leakage.",
            [
                "Repetitive tickets overload human agents, causing 12+ hour delays.",
                "Monolithic LLM deployments run up massive frontier model token bills.",
                "Unshielded agents are vulnerable to prompt injection attacks, risking unauthorized tool execution."
            ],
            "Support teams face a three-way dilemma. Human support is slow. Cheap LLM agents are fast but easily bypassed via prompt injections. Running everything on frontier models is cost-prohibitive. This security and cost gap has left companies unable to deploy autonomous customer service at scale."
        ),
        (
            3,
            "The Solution (AI Customer Support)",
            "Dual-LLM Guarded Stateful Execution",
            "A workflow diagram starting from Inbound channels going through a prompt injection sandbox layer, then into the LangGraph state machine, reaching the Confidence Gate, and branching to Auto-Execution or Human Review.",
            [
                "Orchestrates multi-agent support workflows securely using LangGraph Platform.",
                "Defends execution channels with a Dual-LLM prompt injection sandbox layer.",
                "Confidence score visualizations flag edge-cases for human review."
            ],
            "We solve this with a dual-LLM guarded, stateful execution pipeline on LangGraph Platform. Before any text touches our core graph, an intake model screens the request for adversarial overrides. The query then traverses distinct graph nodes, executing database tools only if the confidence score exceeds our strict intent gates."
        ),
        (
            4,
            "Stateful LangGraph Engine",
            "Multi-Agent Routing & MCP Integration",
            "Interactive node transition diagram showing how Model Context Protocol (MCP) acts as the bridge to SQLite/Postgres databases and CRM services, preserving state updates.",
            [
                "<b>Intake Node</b>: Sanitizes messages and checks prompt injection guardrails.",
                "<b>Classifier Node</b>: Identifies intents and extracts order/subscription IDs.",
                "<b>Context Node (MCP)</b>: Securely queries user transaction history and knowledge bases.",
                "<b>Resolver Node</b>: Evaluates solutions and proposes tool parameters."
            ],
            "Our engine integrates Model Context Protocol (MCP) to decouple the agent from database backends. This ensures uniform tool discovery and strict data boundaries. By isolating database fetches into independent, sandboxed nodes, we prevent the agent from fabricating details or writing rogue transaction requests."
        ),
        (
            5,
            "Cost Optimization: Mixture-of-Experts",
            "Reasoning Model Routing & Cost Efficiency",
            "Comparative bar chart showing the token cost of routing all queries to Claude 4/GPT-5 vs. our 3-tier routing (demonstrating an 80% cost reduction). Includes a real-time ticket-cost metric.",
            [
                "<b>Tier 0 (Gemini 2.5 Flash / GPT-4o-mini)</b>: Classifies and handles general FAQs ($0.00015/1k tokens).",
                "<b>Tier 1 (Claude 3.5 Sonnet / Gemini 2.0 Pro)</b>: Handles standard order status and transaction updates.",
                "<b>Tier 2 (OpenAI o1/o3 / Claude 4 Opus)</b>: Deep reasoning models for high-risk refund and legal evaluations."
            ],
            "We use Mixture-of-Experts routing to optimize costs. Instead of running every ticket on expensive models, Tier 0 handles classification. Standard queries route to Tier 1. High-risk requests—like refund requests over $50 or angry customer complaints—route to Tier 2 reasoning models (like OpenAI o1/o3) for deep planning and validation. This saves up to 80% on API costs."
        ),
        (
            6,
            "Cryptographic Audit Ledger",
            "Immutable Logs & GDPR-Compliant Erasure",
            "A block diagram showing SHA-256 hash chaining connecting decision blocks. Highlights a key-shredding node for GDPR CCPA erasure compliance.",
            [
                "Chains decision metadata (prev_hash, model, cost, tools used) using SHA-256.",
                "Ensures absolute tamper-evidence analogous to append-only immutable databases.",
                "Supports GDPR 'Right to be Forgotten' via customer-specific cryptographic salt key shredding."
            ],
            "Every autonomous action is written to an immutable cryptographic ledger chain. If database history is retroactively tampered with, the SHA-256 signature chain breaks immediately, alerting the frontend dashboard. To support GDPR erasure, we encrypt customer PII with rotatable keys; shredding a key deletes personal data while keeping the mathematical ledger structure intact."
        ),
        (
            7,
            "Production Architecture",
            "Decoupled Microservices & Closed-Loop Control",
            "System topology diagram showing API Gateway (FastAPI, SOC 2/ISO 27001 aligned), Kafka message broker, decoupled workers, and the Closed-Loop optimization controller.",
            [
                "Secured with JWT OAuth2, Rate Limiting, and SOC 2 Type II alignment.",
                "Decoupled worker microservices scale dynamically via Kafka events.",
                "<b>Closed-Loop Control</b>: Dynamic HNSW index ef_search adjustment based on latency spans."
            ],
            "In production, the architecture features event-driven microservices scaled through a Kafka broker. It is aligned with SOC 2 Type II and ISO 27001 standards. We apply closed-loop control theory directly to the vector search: if latency spikes, our system dynamically adjusts search parameters (like ef_search) in Redis to restore normal speeds."
        ),
        (
            8,
            "Simulators & Human Console",
            "Real-Time Latency & Confidence Dashboards",
            "Dashboard screenshot highlighting the pending queue with real-time latency counters, cost-per-ticket metrics, and confidence score visualizations showing the gating threshold.",
            [
                "<b>Simulators (Email, Chat, Voice)</b>: Trace LangGraph execution paths in real time.",
                "<b>Human Console</b>: Pauses execution on low-confidence tickets, presenting draft replies.",
                "<b>Telemetry HUD</b>: Displays cost-saved tracking and real-time response latency."
            ],
            "Our Next.js dashboard gives operators a high-fidelity control panel. Simulators visually trace execution paths, displaying real-time latency and ticket cost metrics. When a ticket falls below the confidence gate, the dashboard presents the agent with a pre-staged response and tool parameters, allowing 1-click approvals."
        ),
        (
            9,
            "Impact & ROI",
            "Safely Scaling Customer Operations",
            "Side-by-side comparison: Traditional Inbox (12-hour resolution, high cost) vs. AI Customer Support (2-second autonomy, low cost, 80% autonomy rate).",
            [
                "<b>80% Autonomy</b>: Repetitive support operations automated safely.",
                "<b>Patentable Ledger</b>: Cryptographic auditability provides a clear market differentiator.",
                "<b>Algorithmic Control Loops</b>: Self-optimizing search parameters ensure sub-2-second SLAs."
            ],
            "AI Customer Support shifts customer service from a manual bottleneck to a secure, autonomous engine. Automating 80% of repetitive tasks with Mixture-of-Experts routing reduces response times to 2 seconds and cuts costs by 80%. Backed by a cryptographic ledger and closed-loop performance control, it is safe, secure, and ready for deployment."
        )
    ]

    for slide_num, title, headline, visual, bullets, script in slides_data:
        story.append(make_slide_block(slide_num, title, headline, visual, bullets, script))
        story.append(Spacer(1, 10))
        
    story.append(PageBreak())
    
    # ------------------ SECTION 3: TECH SPECS & MOE ------------------
    story.append(Paragraph("3. Technical Architecture & MoE Tiers", h1_style))
    story.append(Paragraph("AI Customer Support uses a cost-performance optimized routing mechanism. Below is the active routing layout utilized by our LangGraph engine:", body_style))
    
    moe_data = [
        ["Tier", "Model Class", "Cost (per 1K tkn In/Out)", "Primary Use Cases"],
        ["Tier 0", "Gemini 2.5 Flash / GPT-4o-mini", "$0.00015 / $0.00060", "Adversarial screening, Intent Classification, General FAQs, routing"],
        ["Tier 1", "Claude 3.5 Sonnet / Gemini 2.0 Pro", "$0.00300 / $0.01500", "Standard transactions (Order Status, shipping delay, MCP actions)"],
        ["Tier 2", "OpenAI o1/o3 / Claude 4 Opus", "$0.01500 / $0.07500", "High-risk (Legal threats, high-value refunds, low-confidence reasoning)"]
    ]
    
    moe_table = Table(moe_data, colWidths=[55, 160, 120, 165])
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
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
    ]))
    story.append(moe_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Closed-Loop Production Topology:</b>", h2_style))
    story.append(Paragraph("To ensure reliability and high performance under variable load, the production topology implements three automated feedback loops monitored by OpenTelemetry:", body_style))
    
    topology_data = [
        ["Optimization Loop", "Trigger / Metric", "Action Taken"],
        [
            "Adaptive ef_search Control",
            "Latency spikes or high query traffic in OpenTelemetry spans.",
            "Dynamically writes updated ef_search values to Redis cache, tuning vector retrieval speed/recall balance."
        ],
        [
            "Event-Driven Index Maintenance",
            "High write density or page fragmentation in DB logs.",
            "Triggers targeted REINDEX operations on the SQLite/PostgreSQL vector tables asynchronously."
        ],
        [
            "Embedding Failover",
            "Primary embedding API failure (e.g., rate limit, 500 error).",
            "Redis circuit breaker trips, automatically routing vector queries to secondary embedding models."
        ]
    ]
    topology_table = Table(topology_data, colWidths=[130, 150, 220])
    topology_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('TOPPADDING', (0,0), (-1,0), 4),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('TOPPADDING', (0,1), (-1,-1), 5),
    ]))
    story.append(topology_table)
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 4: 3-MIN SCRIPT ------------------
    story.append(Paragraph("4. 3-Minute Verbal Pitch Script Flow", h1_style))
    story.append(Paragraph("This cohesive script flows slide-by-slide to walk judges through AI Customer Support in under 3 minutes:", body_style))
    
    script_sections = [
        ("Slide 1 | 0:00 - 0:20 | Introduction & Vision", 
         "Hello judges. Customer support is a massive bottleneck. Businesses want automation, but they are terrified of hallucinating agents executing unauthorized actions. Today, we present AI Customer Support: a trust-gated inbox automation engine built on LangGraph Platform and Model Context Protocol, resolving 80% of support queries safely, cost-effectively, and with complete mathematical auditability."),
        
        ("Slide 2 | 0:20 - 0:40 | The Core Dilemma", 
         "Support teams face a three-way dilemma: Speed, Cost, and Safety. Human support is slow. Cheap LLM agents are fast but easily bypassed via prompt injections. Running everything on frontier models is cost-prohibitive. This security and cost gap has left companies unable to deploy autonomous customer service at scale."),
        
        ("Slide 3 | 0:40 - 1:00 | The Solution (LangGraph Workflow)", 
         "We solve this with a dual-LLM guarded, stateful execution pipeline on LangGraph Platform. Before any text touches our core graph, an intake model screens the request for adversarial overrides. The query then traverses distinct graph nodes, executing database tools only if the confidence score exceeds our strict intent gates."),
        
        ("Slide 4 | 1:00 - 1:20 | Stateful LangGraph Engine", 
         "Our engine integrates Model Context Protocol (MCP) to decouple the agent from database backends. This ensures uniform tool discovery and strict data boundaries. By isolating database fetches into independent, sandboxed nodes, we prevent the agent from fabricating details or writing rogue transaction requests."),
        
        ("Slide 5 | 1:20 - 1:40 | Cost Optimization via MoE Routing", 
         "We use Mixture-of-Experts routing to optimize costs. Instead of running every ticket on expensive models, Tier 0 handles classification. Standard queries route to Tier 1. High-risk requests—like refund requests over $50 or angry customer complaints—route to Tier 2 reasoning models (like OpenAI o1/o3) for deep planning and validation. This saves up to 80% on API costs."),
        
        ("Slide 6 | 1:40 - 2:00 | Cryptographic Audit Ledger", 
         "Every autonomous action is written to an immutable cryptographic ledger chain. If database history is retroactively tampered with, the SHA-256 signature chain breaks immediately, alerting the frontend dashboard. To support GDPR erasure, we encrypt customer PII with rotatable keys; shredding a key deletes personal data while keeping the mathematical ledger structure intact."),
        
        ("Slide 7 | 2:00 - 2:20 | Production Architecture & Closed-Loop Topology", 
         "In production, the architecture features event-driven microservices scaled through a Kafka broker. It is aligned with SOC 2 Type II and ISO 27001 standards. We apply closed-loop control theory directly to the vector search: if latency spikes, our system dynamically adjusts search parameters (like ef_search) in Redis to restore normal speeds."),
        
        ("Slide 8 | 2:20 - 2:40 | Live Demo & Human Console", 
         "Our Next.js dashboard gives operators a high-fidelity control panel. Simulators visually trace execution paths, displaying real-time latency and ticket cost metrics. When a ticket falls below the confidence gate, the dashboard presents the agent with a pre-staged response and tool parameters, allowing 1-click approvals."),
        
        ("Slide 9 | 2:40 - 3:00 | Conclusion & Impact", 
         "AI Customer Support makes inbox automation secure, cost-effective, and fully auditable. By automating 80% of repetitive tasks, companies reduce response times to 2 seconds, cut costs by 80%, and retain absolute safety. It's the future of trust-gated AI customer operations. Thank you!")
    ]
    
    for time_title, text in script_sections:
        story.append(Paragraph(f"<b>{time_title}</b>", h2_style))
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
            "How does the system resist prompt injection attacks?",
            "We implement a Dual-LLM security pipeline at the Intake node. Before the query touches the LangGraph state machine, a specialized guardrail model (Gemini 2.5 Flash trained on adversarial datasets) screens the input for override commands. If flagged, the ticket is immediately sandboxed and routed to human review without executing any tools."
        ],
        [
            "How can you support GDPR erasure if the ledger is immutable?",
            "We encrypt customer PII using rotatable keys before writing to the ledger. When a deletion request is received, we shred the keys for that customer. The transaction hashes remain structurally intact to preserve ledger integrity, but all personal details become permanently unreadable mathematical noise."
        ],
        [
            "Why use Model Context Protocol (MCP) instead of custom connectors?",
            "MCP provides a standardized, secure protocol for tool discovery and execution. Rather than writing custom APIs for every database or CRM, we expose them as MCP servers. This decouples the agent logic from the storage layer, enabling uniform security and monitoring."
        ],
        [
            "Is closed-loop control theory really necessary for an LLM agent?",
            "Yes. LLM retrieval pipelines suffer from latency spikes when vector database loads increase. By monitoring OpenTelemetry metrics, our controllers dynamically write updated tuning parameters (like HNSW index ef_search) to Redis cache, balancing latency and recall automatically."
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
