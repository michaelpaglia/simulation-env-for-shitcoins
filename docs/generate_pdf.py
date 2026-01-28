"""Generate academic-style PDF whitepaper using fpdf2."""

from fpdf import FPDF

class WhitepaperPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Times', 'I', 9)
            self.set_text_color(128)
            self.cell(0, 10, 'HOPIUM: A Simulation-Based Prediction Economy', 0, 0, 'L')
            self.cell(0, 10, 'Hopium Lab', 0, 1, 'R')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', '', 10)
        self.set_text_color(0)
        self.cell(0, 10, str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, title):
        self.set_font('Times', 'B', 14)
        self.set_text_color(0)
        self.ln(8)
        self.cell(0, 10, f'{num}. {title.upper()}', 0, 1, 'L')
        self.ln(2)

    def section_title(self, num, title):
        self.set_font('Times', 'B', 12)
        self.ln(4)
        self.cell(0, 8, f'{num} {title}', 0, 1, 'L')
        self.ln(1)

    def subsection_title(self, title):
        self.set_font('Times', 'BI', 11)
        self.ln(2)
        self.cell(0, 7, title, 0, 1, 'L')

    def body_text(self, text, indent=True):
        self.set_font('Times', '', 11)
        self.set_text_color(0)
        if indent:
            self.set_x(self.l_margin + 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet_list(self, items):
        self.set_font('Times', '', 11)
        for item in items:
            self.set_x(self.l_margin + 10)
            self.cell(5, 6, chr(149), 0, 0)  # bullet
            self.multi_cell(0, 6, item)
        self.ln(2)

    def add_table(self, caption, headers, rows):
        self.set_font('Times', 'B', 10)
        self.cell(0, 8, caption, 0, 1, 'L')

        col_width = (self.w - 2 * self.l_margin) / len(headers)

        # Headers
        self.set_font('Times', 'B', 10)
        self.set_fill_color(240, 240, 240)
        for header in headers:
            self.cell(col_width, 8, header, 1, 0, 'L', True)
        self.ln()

        # Rows
        self.set_font('Times', '', 10)
        for row in rows:
            for cell in row:
                self.cell(col_width, 7, str(cell), 1, 0, 'L')
            self.ln()
        self.ln(4)


def generate_whitepaper():
    pdf = WhitepaperPDF()
    pdf.add_page()

    # Title block
    pdf.set_font('Times', 'B', 20)
    pdf.ln(20)
    pdf.multi_cell(0, 10, 'HOPIUM: A Simulation-Based\nPrediction Economy for\nCryptocurrency Token Analysis', 0, 'C')

    pdf.ln(8)
    pdf.set_font('Times', '', 14)
    pdf.cell(0, 8, 'Technical Whitepaper v0.1', 0, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Times', '', 12)
    pdf.cell(0, 6, 'Hopium Lab Research', 0, 1, 'C')
    pdf.set_font('Times', 'I', 11)
    pdf.cell(0, 6, 'https://hopiumlab.xyz', 0, 1, 'C')

    pdf.ln(5)
    pdf.set_font('Times', '', 11)
    pdf.cell(0, 6, 'January 2026', 0, 1, 'C')

    # Abstract
    pdf.ln(15)
    pdf.set_font('Times', 'B', 11)
    pdf.cell(0, 8, 'Abstract', 0, 1, 'L')
    pdf.set_font('Times', '', 10)
    abstract = """We present HOPIUM, a tokenized prediction economy built on a social media simulation engine designed to model cryptocurrency community dynamics. The system employs agent-based modeling with heterogeneous personas to simulate how decentralized communities react to new token concepts prior to launch. Users stake HOPIUM tokens to run simulations, participate in prediction markets, and earn rewards for accurate forecasting. The token economy incorporates deflationary mechanics through transaction burns, creating alignment between platform utility and token value. We describe the simulation methodology, tokenomic structure, and economic mechanisms, and present preliminary self-simulation results demonstrating the platform's predictive capabilities."""
    pdf.multi_cell(0, 5, abstract)

    pdf.ln(3)
    pdf.set_font('Times', 'I', 10)
    pdf.cell(0, 6, 'Keywords: cryptocurrency, tokenomics, agent-based modeling, prediction markets, social simulation', 0, 1, 'L')

    # Introduction
    pdf.chapter_title(1, 'Introduction')
    pdf.body_text('The cryptocurrency ecosystem witnesses thousands of token launches daily, with the vast majority failing to achieve sustainable community adoption. Current approaches to token launch assessment rely primarily on subjective evaluation, historical pattern matching, or post-hoc analysis of market performance. There exists no systematic methodology for pre-launch testing of token concepts against realistic community dynamics.', False)

    pdf.body_text('We introduce Hopium Lab, a simulation platform that models cryptocurrency social media (commonly referred to as "Crypto Twitter" or CT) dynamics using agent-based modeling. The platform enables token creators and analysts to test concepts against simulated community reactions before committing capital or reputation to a launch.')

    pdf.body_text('This paper describes the tokenization of the Hopium Lab platform through the HOPIUM token, which serves as both a utility token for accessing simulation services and a stake in prediction market outcomes.')

    # Background
    pdf.chapter_title(2, 'Background and Motivation')

    pdf.section_title('2.1', 'The Token Launch Problem')
    pdf.body_text('Token launches in the cryptocurrency ecosystem are characterized by high uncertainty and information asymmetry. Founders typically base launch decisions on subjective assessment, pattern matching against previous launches, limited market research, or advisor opinions with potential conflicts of interest.', False)
    pdf.body_text('This approach results in a high failure rate, with studies suggesting that over 90% of launched tokens fail to maintain meaningful trading activity beyond 30 days.')

    pdf.section_title('2.2', 'Predictability of Community Dynamics')
    pdf.body_text('Despite the apparent chaos of cryptocurrency social media, community responses exhibit predictable patterns:', False)
    pdf.bullet_list([
        'Narrative resonance: Certain themes perform better under specific market conditions',
        'Skeptic activation: Weak or derivative concepts trigger coordinated criticism',
        'Influencer dynamics: Key opinion leaders follow momentum thresholds',
        'FUD propagation: Negative sentiment spreads through identifiable patterns'
    ])

    # System Architecture
    pdf.chapter_title(3, 'System Architecture')

    pdf.section_title('3.1', 'Simulation Engine')
    pdf.body_text('The core simulation engine models community dynamics through discrete time steps representing hours of social media activity. The system employs six primary persona types: Degen (high engagement, low influence, very high FOMO), Skeptic (medium engagement, high FUD generation), Whale (low engagement, very high influence), Influencer (medium engagement, high influence), Normie (low engagement, high FOMO), and Bot (very high engagement, very low influence).', False)

    pdf.body_text('Simulations operate under four market regimes (Bear, Crab, Bull, Euphoria), each modifying persona activation probabilities and sentiment dynamics.')

    pdf.section_title('3.2', 'Output Metrics')
    pdf.body_text('Each simulation produces quantitative metrics: Viral Coefficient (new users per existing user), Peak Sentiment (maximum positive sentiment), FUD Resistance (resilience to negative attacks), Sentiment Stability (inverse variance), Hours to Peak, and Hours to Death.', False)

    pdf.body_text('Based on these metrics, the system classifies predicted outcomes into five categories: Moon (sustained viral success), Cult Classic (niche adoption), Pump and Dump (spike then decline), Slow Bleed (gradual decay), and Rug (rapid collapse).')

    # Token Economics
    pdf.chapter_title(4, 'Token Economics')

    pdf.section_title('4.1', 'Token Specification')
    pdf.add_table('Table 1: HOPIUM Token Parameters',
        ['Parameter', 'Value'],
        [
            ['Name', 'Hopium'],
            ['Symbol', 'HOPIUM'],
            ['Network', 'Solana'],
            ['Total Supply', '1,000,000,000'],
            ['Launch', 'Pump.fun Fair Launch']
        ])

    pdf.section_title('4.2', 'Distribution')
    pdf.bullet_list([
        'Public Launch (80%): Available through Pump.fun bonding curve',
        'Team Allocation (10%): 6-month cliff, 12-month linear vesting',
        'Treasury (10%): Development grants and ecosystem growth'
    ])
    pdf.body_text('No venture capital allocation, private sale, or pre-mine is conducted.', False)

    # Economic Mechanisms
    pdf.chapter_title(5, 'Economic Mechanisms')

    pdf.section_title('5.1', 'Utility Functions')
    pdf.body_text('HOPIUM tokens serve three primary utility functions: Simulation Access (stake to run simulations), Prediction Markets (stake on outcome predictions), and Governance (protocol decision participation).', False)

    pdf.add_table('Table 2: Simulation Tier Pricing',
        ['Tier', 'Duration', 'Stake'],
        [
            ['Quick', '12 hours', '100 HOPIUM'],
            ['Standard', '24 hours', '500 HOPIUM'],
            ['Full', '48 hours', '1,000 HOPIUM'],
            ['Gauntlet', 'Variable', '2,500 HOPIUM']
        ])

    pdf.section_title('5.2', 'Deflationary Mechanisms')
    pdf.bullet_list([
        '5% burn on simulation fees',
        '5% burn on prediction market settlements',
        '50% burn on Gauntlet stage failures',
        'Variable burns for premium features'
    ])

    pdf.section_title('5.3', 'The Gauntlet')
    pdf.body_text('The Gauntlet is a multi-stage stress test: Stage 1 (Crab Market, 1.5x multiplier), Stage 2 (Bear Market, 2x), Stage 3 (Bear + Skeptics, 3x). Participants may exit after any successful stage. Failure results in stake loss with 50% burned.', False)

    # Self-Simulation
    pdf.chapter_title(6, 'Self-Simulation Results')
    pdf.body_text('Prior to publication, we executed the HOPIUM token concept through our simulation engine under standard market conditions:', False)

    pdf.add_table('Table 3: HOPIUM Self-Simulation Results',
        ['Metric', 'Value'],
        [
            ['Viral Coefficient', '7.2x'],
            ['Peak Sentiment', '+0.73'],
            ['FUD Resistance', '0.81'],
            ['Predicted Outcome', 'Cult Classic'],
            ['Confidence', '67%']
        ])

    pdf.subsection_title('Identified Strengths')
    pdf.bullet_list([
        'Meta-narrative resonates with community appreciation for self-aware projects',
        'Clear utility function creates natural holder base',
        'Recursive demonstration provides inherent credibility'
    ])

    pdf.subsection_title('Identified Risks')
    pdf.bullet_list([
        'Niche positioning may limit initial audience reach',
        'Platform utility dependent on sustained user activity',
        'Prediction market components face regulatory uncertainty'
    ])

    # Roadmap
    pdf.chapter_title(7, 'Roadmap')
    pdf.body_text('Phase 1 (Launch): Fair launch execution, core simulation platform, basic prediction markets.', False)
    pdf.body_text('Phase 2 (Gamification): Gauntlet mode, leaderboards, reputation system.')
    pdf.body_text('Phase 3 (Social): Public feeds, curator incentives, strategy marketplace.')
    pdf.body_text('Phase 4 (Integration): Simulation-to-launch pipeline, community governance.')

    # Risks
    pdf.chapter_title(8, 'Risk Factors')
    pdf.bullet_list([
        'Model Risk: Simulations are approximations; actual behavior may diverge.',
        'Regulatory Risk: Prediction markets may face jurisdictional restrictions.',
        'Adoption Risk: Platform utility contingent on achieving critical mass.',
        'Competitive Risk: Similar platforms may emerge.',
        'Technical Risk: Smart contract vulnerabilities present standard DeFi risks.'
    ])

    # Disclaimer
    pdf.ln(5)
    pdf.set_fill_color(255, 243, 205)
    pdf.set_font('Times', 'I', 9)
    pdf.multi_cell(0, 5, 'Disclaimer: This document is for informational purposes only and does not constitute financial advice. HOPIUM is a utility token with speculative characteristics. Cryptocurrency investments carry substantial risk of loss. Conduct independent research before making investment decisions.', 0, 'L', True)

    # Conclusion
    pdf.chapter_title(9, 'Conclusion')
    pdf.body_text('HOPIUM represents an experiment in recursive tokenomics - a utility token for a platform that simulates token community dynamics, which itself underwent simulation prior to launch. The alignment of platform utility with token value creates a self-reinforcing ecosystem for cryptocurrency token analysis.', False)

    pdf.ln(10)
    pdf.set_font('Times', 'I', 12)
    pdf.cell(0, 8, '"The only token that passed its own simulation."', 0, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Times', '', 10)
    pdf.cell(0, 6, 'Contact: research@hopiumlab.xyz | https://hopiumlab.xyz | @hopaboratory', 0, 1, 'C')

    return pdf


if __name__ == '__main__':
    import sys
    output_path = sys.argv[1] if len(sys.argv) > 1 else 'HOPIUM_Whitepaper.pdf'
    pdf = generate_whitepaper()
    pdf.output(output_path)
    print(f'Generated: {output_path}')
