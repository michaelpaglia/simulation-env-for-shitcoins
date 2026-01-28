"""Tests for CT agent personas."""

import pytest
from src.agents.personas import (
    Persona,
    PersonaType,
    get_persona,
    get_all_personas,
    get_kols,
    get_random_kols,
    PERSONAS,
    KOLS,
)


class TestPersonaModel:
    """Tests for Persona model."""

    def test_persona_attributes(self, degen_persona):
        """Persona has all required attributes."""
        assert degen_persona.type == PersonaType.DEGEN
        assert degen_persona.name is not None
        assert degen_persona.handle is not None
        assert degen_persona.bio is not None
        assert 0 <= degen_persona.engagement_rate <= 1
        assert 0 <= degen_persona.influence_score <= 1
        assert 0 <= degen_persona.fomo_susceptibility <= 1
        assert 0 <= degen_persona.fud_generation <= 1

    def test_persona_system_prompt(self, degen_persona):
        """get_system_prompt() generates valid prompt."""
        prompt = degen_persona.get_system_prompt()
        assert degen_persona.name in prompt
        assert degen_persona.handle in prompt
        assert "Crypto Twitter" in prompt
        assert "280 chars" in prompt

    def test_all_persona_types_exist(self):
        """All persona types have a corresponding persona."""
        for ptype in [PersonaType.DEGEN, PersonaType.SKEPTIC, PersonaType.WHALE,
                      PersonaType.INFLUENCER, PersonaType.NORMIE, PersonaType.BOT]:
            assert ptype in PERSONAS
            persona = PERSONAS[ptype]
            assert persona.type == ptype


class TestPersonaRegistry:
    """Tests for persona registry functions."""

    def test_get_persona(self):
        """get_persona returns correct persona type."""
        degen = get_persona(PersonaType.DEGEN)
        assert degen.type == PersonaType.DEGEN

        skeptic = get_persona(PersonaType.SKEPTIC)
        assert skeptic.type == PersonaType.SKEPTIC

    def test_get_all_personas_with_kols(self):
        """get_all_personas includes KOLs by default."""
        all_personas = get_all_personas(include_kols=True)
        # Should have base personas + KOLs
        assert len(all_personas) > len(PERSONAS)

    def test_get_all_personas_without_kols(self):
        """get_all_personas can exclude KOLs."""
        base_personas = get_all_personas(include_kols=False)
        assert len(base_personas) == len(PERSONAS)

    def test_get_kols(self):
        """get_kols returns KOL list."""
        kols = get_kols()
        assert len(kols) > 0
        for kol in kols:
            assert kol.type == PersonaType.KOL

    def test_get_random_kols(self):
        """get_random_kols returns subset."""
        kols = get_random_kols(n=3)
        assert len(kols) == 3
        # All should be KOL type
        for kol in kols:
            assert kol.type == PersonaType.KOL

    def test_get_random_kols_max(self):
        """get_random_kols handles n > total KOLs."""
        kols = get_random_kols(n=100)  # More than available
        assert len(kols) == len(KOLS)  # Should return all


class TestPersonaBehavior:
    """Tests for persona behavior characteristics."""

    def test_degen_high_fomo(self, degen_persona):
        """Degen has high FOMO susceptibility."""
        assert degen_persona.fomo_susceptibility > 0.7

    def test_degen_low_fud(self, degen_persona):
        """Degen has low FUD generation."""
        assert degen_persona.fud_generation < 0.3

    def test_skeptic_high_fud(self, skeptic_persona):
        """Skeptic has high FUD generation."""
        assert skeptic_persona.fud_generation > 0.7

    def test_skeptic_low_fomo(self, skeptic_persona):
        """Skeptic has low FOMO susceptibility."""
        assert skeptic_persona.fomo_susceptibility < 0.3

    def test_whale_high_influence(self, whale_persona):
        """Whale has high influence score."""
        assert whale_persona.influence_score > 0.8

    def test_whale_low_engagement(self, whale_persona):
        """Whale has low engagement rate."""
        assert whale_persona.engagement_rate < 0.4

    def test_bot_no_fomo_or_fud(self):
        """Bot has zero FOMO and FUD."""
        bot = PERSONAS[PersonaType.BOT]
        assert bot.fomo_susceptibility == 0
        assert bot.fud_generation == 0

    def test_persona_vocabulary(self, degen_persona):
        """Personas have relevant vocabulary."""
        vocab = degen_persona.vocabulary
        assert len(vocab) > 0
        # Degen vocabulary should include slang
        assert any(word in vocab for word in ["ser", "aping", "LFG", "wagmi"])


class TestKOLPersonas:
    """Tests for real KOL personas."""

    def test_kols_have_handles(self):
        """All KOLs have Twitter handles."""
        for kol in KOLS:
            assert kol.handle is not None
            assert len(kol.handle) > 0

    def test_kols_have_influence(self):
        """KOLs have meaningful influence scores."""
        for kol in KOLS:
            assert kol.influence_score >= 0.5  # KOLs should be influential

    def test_kol_count(self):
        """Verify expected number of KOLs."""
        assert len(KOLS) >= 5  # At least 5 KOLs defined

    def test_kol_uniqueness(self):
        """KOL handles should be unique."""
        handles = [kol.handle for kol in KOLS]
        assert len(handles) == len(set(handles))


class TestPersonaPromptGeneration:
    """Tests for prompt generation consistency."""

    def test_prompt_contains_fomo_level(self, degen_persona):
        """Prompt includes FOMO level indicator."""
        prompt = degen_persona.get_system_prompt()
        assert "FOMO level:" in prompt

    def test_prompt_contains_fud_tendency(self, skeptic_persona):
        """Prompt includes FUD tendency indicator."""
        prompt = skeptic_persona.get_system_prompt()
        assert "FUD tendency:" in prompt

    def test_high_fomo_shows_high_in_prompt(self, degen_persona):
        """High FOMO persona shows HIGH in prompt."""
        prompt = degen_persona.get_system_prompt()
        assert "FOMO level: HIGH" in prompt

    def test_high_fud_shows_high_in_prompt(self, skeptic_persona):
        """High FUD persona shows HIGH in prompt."""
        prompt = skeptic_persona.get_system_prompt()
        assert "FUD tendency: HIGH" in prompt
