"""
Generate IEEE-style academic PDF whitepaper.

Mimics IEEE conference paper format:
- Two-column layout
- Times font family
- Formal academic structure
- Proper citations format
"""

from fpdf import FPDF, XPos, YPos


class IEEEPaper(FPDF):
    """IEEE-style two-column academic paper."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False, margin=20)  # Manual page breaks
        self.col_width = 0
        self.col_gap = 8  # Gap between columns in mm
        self.current_col = 0  # 0 = left, 1 = right
        self.col_start_y = 0  # Y where columns start on current page
        self.two_col_mode = False
        self.left_col_x = 0
        self.right_col_x = 0
        self.bottom_margin = 25  # mm from bottom

    def set_two_column_mode(self, enabled=True):
        """Enable or disable two-column mode."""
        self.two_col_mode = enabled
        if enabled:
            usable_width = self.w - 2 * self.l_margin
            self.col_width = (usable_width - self.col_gap) / 2
            self.left_col_x = self.l_margin
            self.right_col_x = self.l_margin + self.col_width + self.col_gap
            self.current_col = 0
            self.col_start_y = self.get_y()

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 9)
        self.set_text_color(0)
        self.cell(0, 10, str(self.page_no()), new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

    def get_col_x(self):
        """Get X position for current column."""
        return self.left_col_x if self.current_col == 0 else self.right_col_x

    def switch_column(self):
        """Switch to the next column or page."""
        if self.current_col == 0:
            # Switch to right column
            self.current_col = 1
            self.set_xy(self.right_col_x, self.col_start_y)
        else:
            # Switch to new page, left column
            self.current_col = 0
            self.add_page()
            self.col_start_y = self.t_margin
            self.set_xy(self.left_col_x, self.col_start_y)

    def needs_column_break(self, height_needed=10):
        """Check if we need to switch columns."""
        if not self.two_col_mode:
            return False
        return self.get_y() + height_needed > self.h - self.bottom_margin

    def ensure_space(self, height_needed=10):
        """Ensure we have enough space, switching columns if needed."""
        if self.needs_column_break(height_needed):
            self.switch_column()

    def section_header(self, num, title):
        """Write a section header (IEEE style: Roman numerals, centered)."""
        self.ln(3)
        self.ensure_space(15)
        self.set_x(self.get_col_x())
        self.set_font('Times', 'B', 10)
        roman = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
        header_text = f"{roman[num]}. {title.upper()}"
        self.cell(self.col_width, 6, header_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(2)

    def subsection_header(self, letter, title):
        """Write a subsection header (IEEE style: A. Title)."""
        self.ln(2)
        self.ensure_space(12)
        self.set_x(self.get_col_x())
        self.set_font('Times', 'I', 9)
        header_text = f"{letter}. {title}"
        self.cell(self.col_width, 5, header_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.ln(1)

    def paragraph(self, text, indent=True):
        """Write a paragraph with optional first-line indent."""
        self.ensure_space(15)
        x = self.get_col_x()
        self.set_font('Times', '', 9)

        if indent:
            # First line indented
            self.set_x(x + 4)
            words = text.split()
            first_line_width = self.col_width - 4
            line = ""
            remaining_idx = 0
            for i, word in enumerate(words):
                test_line = line + " " + word if line else word
                if self.get_string_width(test_line) < first_line_width:
                    line = test_line
                    remaining_idx = i + 1
                else:
                    break
            self.cell(first_line_width, 4.5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            remaining_text = " ".join(words[remaining_idx:])
            if remaining_text:
                self.set_x(x)
                self.multi_cell(self.col_width, 4.5, remaining_text, align='J')
        else:
            self.set_x(x)
            self.multi_cell(self.col_width, 4.5, text, align='J')

        # Check if we overflowed
        if self.needs_column_break(0):
            self.switch_column()
        self.ln(1)

    def bullet_item(self, text):
        """Write a bullet point item."""
        self.ensure_space(10)
        x = self.get_col_x()
        self.set_x(x + 3)
        self.set_font('Times', '', 9)
        self.cell(4, 4.5, '-', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.multi_cell(self.col_width - 7, 4.5, text, align='J')
        if self.needs_column_break(0):
            self.switch_column()

    def add_table(self, caption, headers, rows, col_widths=None):
        """Add a table with IEEE-style caption."""
        self.ln(2)
        table_height = 20 + len(rows) * 6
        self.ensure_space(table_height)

        x = self.get_col_x()
        table_width = self.col_width

        if col_widths is None:
            col_widths = [table_width / len(headers)] * len(headers)

        # Caption above table
        self.set_x(x)
        self.set_font('Times', '', 8)
        self.multi_cell(table_width, 4, caption, align='C')
        self.ln(1)

        # Headers
        self.set_x(x)
        self.set_font('Times', 'B', 8)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 5, header, 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        self.ln()

        # Rows
        self.set_font('Times', '', 8)
        for row in rows:
            self.set_x(x)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 5, str(cell), 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
            self.ln()

        self.ln(2)
        if self.needs_column_break(0):
            self.switch_column()


def generate_ieee_whitepaper():
    """Generate the HOPIUM whitepaper in IEEE format."""
    pdf = IEEEPaper()
    pdf.set_margins(17, 20, 17)
    pdf.add_page()

    # Title (centered, spanning both columns)
    pdf.set_font('Times', 'B', 22)
    pdf.cell(0, 10, 'HOPIUM: A Simulation-Based Prediction', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(0, 10, 'Economy for Token Analysis', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)

    # Authors
    pdf.set_font('Times', '', 11)
    pdf.cell(0, 5, 'Hopium Lab Research', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Times', 'I', 9)
    pdf.cell(0, 5, 'research@hopiumlab.xyz', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(6)

    # Abstract (full width)
    pdf.set_font('Times', 'B', 9)
    pdf.cell(0, 5, 'Abstract', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Times', 'I', 9)
    abstract = "We present HOPIUM, a tokenized prediction economy built on a social simulation engine for cryptocurrency community dynamics. The system employs agent-based modeling with heterogeneous personas to simulate decentralized community reactions to token concepts prior to launch. Users stake HOPIUM tokens to execute simulations, participate in prediction markets, and earn rewards for accurate forecasting. The economy incorporates deflationary mechanics through transaction burns. We describe the simulation methodology, tokenomic structure, and present self-simulation results demonstrating predictive capabilities."
    pdf.multi_cell(0, 4.5, abstract, align='J')
    pdf.ln(2)

    # Keywords
    pdf.set_font('Times', 'I', 8)
    pdf.cell(0, 4, 'Keywords: tokenomics, agent-based modeling, prediction markets, social simulation, DeFi', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)

    # Enable two-column mode
    pdf.set_two_column_mode(True)

    # I. INTRODUCTION
    pdf.section_header(1, 'Introduction')
    pdf.paragraph("The cryptocurrency ecosystem witnesses thousands of token launches daily, with the majority failing to achieve sustainable adoption. Current assessment approaches rely on subjective evaluation and pattern matching, with no systematic methodology for pre-launch testing against realistic community dynamics.", False)
    pdf.paragraph("We introduce Hopium Lab, a platform that models cryptocurrency social media dynamics using agent-based simulation. Token creators test concepts against simulated community reactions before committing capital.")
    pdf.paragraph("This paper describes the HOPIUM token, which serves as both utility for simulation services and stake in prediction market outcomes. The recursive nature of this system creates unique value: a token for a platform that simulates tokens.")

    # II. BACKGROUND
    pdf.section_header(2, 'Background and Motivation')
    pdf.subsection_header('A', 'The Token Launch Problem')
    pdf.paragraph("Token launches are characterized by high uncertainty. Founders base decisions on gut feeling, historical patterns, or limited research. Studies suggest over 90% of tokens fail to maintain activity beyond 30 days.", False)

    pdf.subsection_header('B', 'Community Dynamics')
    pdf.paragraph("Despite apparent chaos, crypto community responses exhibit predictable patterns:", False)
    pdf.bullet_item("Narrative resonance varies predictably with market conditions")
    pdf.bullet_item("Skeptical actors activate on weak value propositions")
    pdf.bullet_item("Influencers follow momentum thresholds before engagement")
    pdf.bullet_item("FUD propagates through identifiable network patterns")

    # III. SYSTEM ARCHITECTURE
    pdf.section_header(3, 'System Architecture')
    pdf.subsection_header('A', 'Simulation Engine')
    pdf.paragraph("The core engine models community dynamics through discrete hourly time steps. Six persona archetypes operate with distinct behavioral parameters: Degen (high FOMO, low skepticism), Skeptic (high FUD generation), Whale (high market influence), Influencer (high reach), Normie (average behavior), and Bot (automated patterns).", False)
    pdf.paragraph("Four market regimes modify baseline behavior: Bear (reduced activity, increased skepticism), Crab (neutral baseline), Bull (elevated FOMO), and Euphoria (maximum risk tolerance). Each regime applies multipliers to persona engagement probabilities.")

    pdf.subsection_header('B', 'Output Metrics')
    pdf.paragraph("Simulations produce quantitative metrics: Viral Coefficient (spread rate), Peak Sentiment [-1,1], FUD Resistance [0,1], Sentiment Stability, Hours to Peak, Hours to Death. Outcomes classify as: Moon (sustained growth), Cult Classic (niche success), Pump and Dump (brief spike), Slow Bleed (gradual decline), or Rug (rapid collapse).", False)

    # Table I
    pdf.add_table(
        'TABLE I: Persona Behavioral Characteristics',
        ['Persona', 'Engage', 'Influence', 'FOMO', 'Skepticism'],
        [
            ['Degen', 'High', 'Low', 'Very High', 'Very Low'],
            ['Skeptic', 'Medium', 'Medium', 'Very Low', 'Very High'],
            ['Whale', 'Low', 'Very High', 'Low', 'Medium'],
            ['Influencer', 'Medium', 'High', 'Medium', 'Low'],
            ['Normie', 'Medium', 'Low', 'Medium', 'Medium'],
            ['Bot', 'High', 'Low', 'N/A', 'N/A'],
        ],
        col_widths=[18, 14, 14, 18, 18]
    )

    # IV. TOKEN ECONOMICS
    pdf.section_header(4, 'Token Economics')
    pdf.subsection_header('A', 'Token Specification')
    pdf.paragraph("HOPIUM launches on Solana via the Pump.fun fair launch mechanism. Total supply is fixed at 1,000,000,000 tokens with the following distribution: 80% public fair launch (no presale), 10% team allocation (6-month cliff, 12-month linear vest), 10% treasury for development and incentives.", False)

    pdf.subsection_header('B', 'Network Selection Rationale')
    pdf.paragraph("Solana was selected based on: sub-second finality enabling real-time prediction settlement, transaction costs averaging $0.00025 enabling micro-stakes, and ecosystem alignment with the target user base active in cryptocurrency speculation.", False)

    # Table II
    pdf.add_table(
        'TABLE II: Token Parameters',
        ['Parameter', 'Value'],
        [
            ['Symbol', 'HOPIUM'],
            ['Network', 'Solana'],
            ['Total Supply', '1,000,000,000'],
            ['Launch Mechanism', 'Pump.fun Fair Launch'],
            ['Decimals', '9'],
        ]
    )

    # V. ECONOMIC MECHANISMS
    pdf.section_header(5, 'Economic Mechanisms')
    pdf.subsection_header('A', 'Utility Functions')
    pdf.paragraph("HOPIUM tokens serve three primary functions within the ecosystem:", False)
    pdf.bullet_item("Simulation Access: Users stake tokens to execute simulations. Stake is returned upon completion minus a fee that is partially burned.")
    pdf.bullet_item("Prediction Markets: Users stake tokens on simulation outcomes. Correct predictions earn proportional rewards from incorrect predictions.")
    pdf.bullet_item("Governance: Token holders vote on platform parameters, fee structures, and treasury allocation.")

    # Table III
    pdf.add_table(
        'TABLE III: Simulation Tier Structure',
        ['Tier', 'Duration', 'Stake Required', 'Burn Rate'],
        [
            ['Quick', '12 hours', '100 HOPIUM', '3%'],
            ['Standard', '24 hours', '500 HOPIUM', '5%'],
            ['Full', '48 hours', '1,000 HOPIUM', '5%'],
            ['Gauntlet', 'Variable', '2,500 HOPIUM', '5-50%'],
        ]
    )

    pdf.subsection_header('B', 'Deflationary Mechanics')
    pdf.paragraph("Token burns create deflationary pressure through multiple mechanisms: simulation fees (5% base burn), prediction market settlements (5% of winner pool), Gauntlet failures (50% of stake burned), and premium feature access (variable burn rates).", False)

    pdf.subsection_header('C', 'The Gauntlet Mode')
    pdf.paragraph("The Gauntlet is a multi-stage stress testing mode for token concepts. Stage 1 (Crab market, 1.5x reward multiplier), Stage 2 (Bear market, 2x multiplier), Stage 3 (Bear market with amplified skeptic population, 3x multiplier). Users may exit after any stage, but failure at any stage results in 50% stake burn.", False)

    # VI. SELF-SIMULATION
    pdf.section_header(6, 'Self-Simulation Results')
    pdf.paragraph("Prior to this publication, the HOPIUM token concept was evaluated using the platform's own simulation engine under Crab market conditions. The following results were obtained:", False)

    pdf.add_table(
        'TABLE IV: Self-Simulation Metrics',
        ['Metric', 'Value', 'Interpretation'],
        [
            ['Viral Coefficient', '7.2x', 'Strong organic spread'],
            ['Peak Sentiment', '+0.73', 'Positive reception'],
            ['FUD Resistance', '0.81', 'High resilience'],
            ['Predicted Outcome', 'Cult Classic', 'Niche but loyal'],
            ['Confidence', '67%', 'Moderate certainty'],
        ]
    )

    pdf.paragraph("Identified strengths include meta-narrative resonance (self-referential appeal), clear utility proposition, and recursive credibility validation. Risk factors include niche market positioning, platform activity dependence, and regulatory uncertainty around prediction markets.", False)

    # VII. ROADMAP
    pdf.section_header(7, 'Development Roadmap')
    pdf.paragraph("Phase 1 (Launch): Fair launch execution, core simulation platform deployment, basic prediction market functionality.", False)
    pdf.paragraph("Phase 2 (Growth): Gauntlet mode implementation, public leaderboards, reputation system and user profiles.", False)
    pdf.paragraph("Phase 3 (Expansion): Public simulation feeds, curator reward mechanisms, strategy marketplace for proven templates.", False)
    pdf.paragraph("Phase 4 (Integration): Simulation-to-launch pipeline, full DAO governance transition, cross-chain expansion.", False)

    # VIII. RISKS
    pdf.section_header(8, 'Risk Factors')
    pdf.bullet_item("Model Risk: Simulations are approximations of human behavior. Actual market dynamics may diverge significantly from predictions.")
    pdf.bullet_item("Regulatory Risk: Prediction markets face legal restrictions in multiple jurisdictions. Platform operation may be limited geographically.")
    pdf.bullet_item("Adoption Risk: Platform utility requires sufficient user activity. Insufficient adoption creates liquidity and prediction accuracy challenges.")
    pdf.bullet_item("Technical Risk: Smart contract vulnerabilities, oracle manipulation, and infrastructure failures pose ongoing risks.")

    # IX. CONCLUSION
    pdf.section_header(9, 'Conclusion')
    pdf.paragraph("HOPIUM represents an experiment in recursive tokenomics: a utility token for a platform that simulates tokens, which was itself simulated prior to launch. The alignment between platform success and token utility, combined with deflationary mechanics and prediction market dynamics, creates self-reinforcing incentives for accurate token analysis.", False)
    pdf.ln(3)
    pdf.set_font('Times', 'I', 9)
    x = pdf.get_col_x()
    pdf.set_x(x)
    pdf.cell(pdf.col_width, 5, '"The only token that passed its own simulation."', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    # References
    pdf.ln(4)
    pdf.section_header(10, 'References')
    pdf.set_font('Times', '', 8)
    refs = [
        "[1] S. Nakamoto, 'Bitcoin: A Peer-to-Peer Electronic Cash System,' 2008.",
        "[2] V. Buterin, 'Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform,' 2014.",
        "[3] A. Yakovenko, 'Solana: A New Architecture for a High Performance Blockchain,' 2018.",
        "[4] Hopium Lab, 'Simulation Engine Technical Documentation,' https://hopiumlab.xyz/docs, 2026.",
    ]
    for ref in refs:
        x = pdf.get_col_x()
        pdf.set_x(x)
        pdf.multi_cell(pdf.col_width, 4, ref, align='L')
        if pdf.needs_column_break(0):
            pdf.switch_column()

    return pdf


if __name__ == '__main__':
    import sys
    output_path = sys.argv[1] if len(sys.argv) > 1 else 'HOPIUM_Whitepaper.pdf'
    pdf = generate_ieee_whitepaper()
    pdf.output(output_path)
    print(f'Generated IEEE-style PDF: {output_path}')
