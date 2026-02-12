"""Nakshatra interpretation module for Vedic astrology birth chart readings.

Provides rich, authentic interpretation text for nakshatras (lunar mansions),
the 27-fold division of the zodiac that forms the backbone of Vedic astrology.
The Janma Nakshatra (Moon's birth nakshatra) is one of the most important
factors in a Vedic chart, shaping personality, karma, and life direction.
"""

import json
from pathlib import Path
from ..models import NAKSHATRA_NAMES, NAKSHATRA_LORDS, NATURAL_FRIENDS, NATURAL_ENEMIES


_DATA_PATH = Path(__file__).parent.parent / 'data' / 'nakshatras.json'
with open(_DATA_PATH) as f:
    NAKSHATRA_DATA = json.load(f)


# ---------------------------------------------------------------------------
# Pada themes keyed by pada number (Dharma-Artha-Kama-Moksha cycle)
# ---------------------------------------------------------------------------
_PADA_THEMES = {
    1: ('Dharma', 'purpose, righteous action, and self-expression'),
    2: ('Artha', 'material pursuits, practical achievement, and worldly security'),
    3: ('Kama', 'desire, pleasure, creativity, and emotional fulfillment'),
    4: ('Moksha', 'spiritual liberation, transcendence, and inner release'),
}

# Navamsha signs cycle for all 108 padas (27 nakshatras x 4 padas)
_NAVAMSHA_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
]


# ---------------------------------------------------------------------------
# Planet keywords for combining with nakshatra energy
# (domain, adjective, essence)
# ---------------------------------------------------------------------------
_PLANET_KEYWORDS = {
    'Sun': ('soul, authority, and self-identity', 'commanding', 'the ego and vital force'),
    'Moon': ('mind, emotions, and inner experience', 'receptive', 'the emotional nature'),
    'Mars': ('energy, courage, and assertive drive', 'fiery', 'the active will'),
    'Mercury': ('intellect, communication, and discrimination', 'analytical', 'the reasoning mind'),
    'Jupiter': ('wisdom, expansion, and dharmic purpose', 'expansive', 'higher knowledge and faith'),
    'Venus': ('love, beauty, and creative expression', 'harmonious', 'desire and refinement'),
    'Saturn': ('discipline, karma, and endurance', 'structured', 'duty and perseverance'),
    'Rahu': ('worldly ambition, obsession, and unconventional paths', 'amplifying', 'intense craving and innovation'),
    'Ketu': ('spirituality, detachment, and past-life wisdom', 'dissolving', 'liberation and intuitive insight'),
}


# ---------------------------------------------------------------------------
# Detailed Moon-nakshatra personality interpretations (Janma Nakshatra)
# Each entry is 5-8 sentences of rich, distinct interpretation.
# ---------------------------------------------------------------------------
_MOON_NAKSHATRA_INTERPRETATIONS = {
    1: (
        "With the Moon in Ashwini, your Janma Nakshatra endows you with remarkable quickness, "
        "both in thought and action. Ruled by Ketu and presided over by the Ashwini Kumaras, the "
        "divine physicians, you carry an innate capacity for healing and renewal. You are a natural "
        "pioneer who thrives on fresh beginnings, and your restless energy propels you to initiate "
        "projects and blaze new trails. Your mind works with lightning speed, grasping situations "
        "instantly and arriving at solutions before others have finished analyzing the problem. "
        "However, impatience is your shadow -- you may abandon endeavors before they fully ripen. "
        "Your life themes revolve around healing, speed, adventure, and the courage to start anew. "
        "At your best, you are a compassionate first responder to life's crises, combining swift "
        "action with an intuitive understanding of what ails others."
    ),
    2: (
        "The Moon in Bharani reveals a soul acquainted with the deepest mysteries of creation and "
        "dissolution. Governed by Venus and watched over by Yama, the lord of death and dharma, "
        "you embody the fierce paradox of life emerging from destruction. Your emotional world is "
        "intensely passionate, loyal, and capable of bearing tremendous burdens that would crush "
        "others. Creativity surges through you with volcanic force, demanding responsible channels "
        "of expression. You are drawn to taboo subjects and feel most alive at the threshold between "
        "worlds. Your challenges lie in managing extremes -- of desire, of possessiveness, of the "
        "weight you carry for others. Life asks you to learn restraint without losing your primal "
        "power. When you honor both the creative and destructive currents within, you become a "
        "profound transformer of the lives you touch."
    ),
    3: (
        "Born under the Moon in Krittika, you carry the purifying flame of Agni within your emotional "
        "nature. Ruled by the Sun and blessed by the fire god, your personality is sharp, discerning, "
        "and uncompromising in its pursuit of truth. You cut through pretense and falsehood with the "
        "precision of a blade, and your critical eye can be both your greatest asset and your most "
        "isolating trait. Leadership comes naturally, as others sense your unwavering conviction. "
        "Your willpower is formidable -- once you commit, you burn steadily toward your goal. "
        "Nourishing others is a deep calling, though you do so through tough love rather than "
        "softness. The challenge is learning when to temper your fire with gentleness. Your life "
        "themes involve purification, nourishment, cutting away what is false, and the courage "
        "to stand alone for what is right."
    ),
    4: (
        "With the Moon in Rohini, you are blessed by the most fertile and creative nakshatra in the "
        "zodiac, the beloved of the Moon itself. Presided over by Brahma the creator, your emotional "
        "nature is lush, magnetic, and deeply attuned to beauty in all its forms. You possess an "
        "irresistible charm that draws people, resources, and opportunities toward you with seemingly "
        "effortless grace. Material abundance and sensual pleasure are natural to your path, yet your "
        "deepest gift is the power of growth itself -- whatever you nurture flourishes. Creativity "
        "flows through you as naturally as water finding its course. Your challenges involve "
        "possessiveness, attachment to comfort, and jealousy when your abundant gifts attract "
        "rivals. When you channel your creative magnetism with generosity, you become a source "
        "of sustenance and beauty that enriches everyone in your orbit."
    ),
    5: (
        "The Moon in Mrigashira marks you as an eternal seeker, driven by an insatiable curiosity "
        "that propels you through life like a deer following a distant scent. Ruled by Mars but "
        "presided over by Soma, the god of the lunar nectar, you combine gentle sensitivity with "
        "an adventurous drive to explore. Your mind is restless, always scanning the horizon for "
        "the next discovery, the next experience, the next answer to questions only you seem to "
        "ask. You are versatile and adaptable, comfortable in diverse settings and among varied "
        "people. Your emotional nature is lighter and more playful than the intensity of your "
        "Martian lord might suggest. The shadow side is fickleness and an inability to settle, "
        "always convinced that fulfillment lies just beyond the next hill. Your life themes "
        "center on the sacred quest, the joy of searching, and learning that the journey "
        "itself is the destination."
    ),
    6: (
        "Born with the Moon in Ardra, your emotional life is shaped by the fierce, transformative "
        "power of Rudra, the storm god. Ruled by Rahu, this nakshatra brings the tempest that clears "
        "stagnation and forces growth through upheaval. Your mind is penetrating and research-oriented, "
        "capable of extraordinary intellectual effort when a problem seizes your attention. Emotional "
        "storms are not merely something you endure -- they are the crucible in which your deepest "
        "wisdom is forged. You have likely experienced significant sorrow or disruption that "
        "catalyzed profound inner transformation. Compassion born from personal suffering is one "
        "of your greatest gifts. Your challenges include destructive tendencies, emotional volatility, "
        "and the temptation to tear things down without building anew. When you harness the storm "
        "rather than being swept away by it, you become a powerful agent of necessary change."
    ),
    7: (
        "The Moon in Punarvasu bestows the luminous gift of renewal -- the ability to return to "
        "wholeness no matter how far you have wandered or how much you have lost. Ruled by Jupiter "
        "and sheltered by Aditi, the boundless mother of the gods, your emotional nature is "
        "fundamentally optimistic, philosophical, and resilient. You bounce back from setbacks "
        "with a faith that puzzles more cynical souls. Home and belonging are central themes, "
        "yet you may travel widely before discovering that home is an inner state. Your wisdom "
        "is practical and nurturing, offered freely to those in need. Generosity and a broad "
        "worldview define your approach to relationships. The challenge is avoiding complacency "
        "or relying too heavily on good fortune. Your life purpose involves the restoration of "
        "hope, the rediscovery of truth, and the quiet heroism of beginning again."
    ),
    8: (
        "With the Moon in Pushya, you are born under what the ancient seers considered the most "
        "auspicious nakshatra for spiritual nourishment and selfless service. Ruled by Saturn yet "
        "presided over by Brihaspati, the guru of the gods, you unite discipline with devotion in "
        "a rare and powerful combination. Your emotional nature is steady, generous, and profoundly "
        "caring -- you nourish others not from overflow but from deep reserves of genuine compassion. "
        "Faith, ethics, and duty are not abstract ideals for you but lived realities that structure "
        "your days. You may appear conservative or reserved, but beneath the surface lies an "
        "unshakeable commitment to doing what is right. Your challenges involve rigidity, excessive "
        "self-sacrifice, and difficulty receiving help. When you allow yourself to be nourished "
        "as freely as you nourish others, you fulfill Pushya's highest promise as a pillar "
        "of spiritual and material sustenance."
    ),
    9: (
        "The Moon in Ashlesha coils around your emotional nature with the hypnotic, penetrating "
        "energy of the serpent. Ruled by Mercury and governed by the Nagas, your psychological "
        "insight is extraordinary -- you perceive the hidden motivations and unspoken currents "
        "that most people miss entirely. This gives you formidable power in any situation "
        "involving strategy, persuasion, or understanding the human psyche. Your mind is "
        "sharp, suspicious, and often several moves ahead. Kundalini energy may be strong, "
        "drawing you toward mystical or occult knowledge. The shadow of Ashlesha is manipulation, "
        "emotional entanglement, and the poison of distrust. Learning to use your power ethically "
        "is the central lesson. Your life themes revolve around the proper wielding of influence, "
        "the alchemy of transmuting venom into medicine, and the deep wisdom that comes from "
        "embracing the serpent within."
    ),
    10: (
        "Born with the Moon in Magha, you carry the regal weight of ancestral legacy and the "
        "authority that comes from deep rootedness in tradition. Ruled by Ketu and watched over "
        "by the Pitris, the revered ancestors, your emotional nature resonates with a sense of "
        "inherited dignity and responsibility. You command respect not through force but through "
        "a natural gravitas that others instinctively recognize. Honoring lineage, preserving "
        "heritage, and upholding the values of those who came before you are central drives. "
        "You may feel the presence of ancestral guidance in pivotal moments of your life. "
        "The challenges of Magha include arrogance, attachment to status, and living in the "
        "past at the expense of the present. Your life themes center on rightful authority, "
        "the duties that come with privilege, and learning to rule your own kingdom -- inner "
        "and outer -- with the benevolence your throne demands."
    ),
    11: (
        "The Moon in Purva Phalguni fills your emotional world with warmth, creative joy, and "
        "the intoxicating delight of being alive. Ruled by Venus and blessed by Bhaga, the god "
        "of marital bliss and fortune, you are a natural celebrant of life's pleasures. Romance, "
        "art, music, and social gathering are not mere diversions for you -- they are the very "
        "channels through which your soul expresses itself. Your charisma is magnetic, your "
        "generosity genuine, and your capacity for love expansive. You bring warmth and laughter "
        "wherever you go, creating an atmosphere of festivity and ease. The shadow side is "
        "indulgence, vanity, and a restless dissatisfaction when pleasure fades. Life asks you "
        "to discover that lasting happiness comes not from the next celebration but from the "
        "creative fire that burns steadily within, illuminating your path and those around you."
    ),
    12: (
        "With the Moon in Uttara Phalguni, your emotional nature is shaped by a deep commitment "
        "to partnership, patronage, and generous service. Ruled by the Sun and guided by Aryaman, "
        "the god of contracts and kindness, you excel at bringing people together and creating "
        "lasting alliances that benefit all parties. You are naturally responsible, fair-minded, "
        "and possess a quiet dignity that inspires trust. Where Purva Phalguni celebrates, you "
        "consolidate and build the enduring structures of relationship and society. Your approach "
        "to emotional life is steady and reliable, though you can become overly burdened by the "
        "obligations you accept. The challenge lies in balancing service to others with your own "
        "needs. Your life themes revolve around the sacredness of commitments, the nobility of "
        "benevolent leadership, and the understanding that true authority is expressed through "
        "lifting others up."
    ),
    13: (
        "The Moon in Hasta gives you hands of remarkable skill and a mind of extraordinary "
        "resourcefulness. Ruled by the Moon itself and presided over by Savitar, the creative "
        "aspect of the solar deity, you possess the power to manifest your intentions through "
        "precise, deliberate action. Craftsmanship, healing arts, sleight of hand, and any "
        "work requiring dexterity are your natural domain. Your wit is quick and your humor "
        "can be disarming, helping you navigate situations that would stymie less adaptable "
        "souls. You are an industrious problem-solver who finds creative solutions where others "
        "see only obstacles. The shadow of Hasta is cunning that crosses into manipulation, and "
        "restlessness that prevents deeper satisfaction. Your life themes center on mastery through "
        "practice, the magic of skilled hands guided by an alert mind, and learning that true "
        "control begins with mastering yourself."
    ),
    14: (
        "Born under the Moon in Chitra, you are the celestial jewel -- brilliant, multifaceted, "
        "and impossible to ignore. Ruled by Mars and blessed by Tvashtar, the divine architect, "
        "your emotional nature is fired by a vision of beauty and perfection that drives you to "
        "create, design, and transform the raw material of life into something extraordinary. You "
        "have a natural eye for aesthetics that extends to every domain, from visual art to the "
        "architecture of ideas and relationships. Charisma and physical attractiveness often "
        "accompany this placement. Your dynamic energy keeps you in constant motion, always "
        "pursuing the next creative project. The challenge is narcissism and an inability to "
        "appreciate beauty that is imperfect or unfinished. Your life purpose revolves around "
        "the sacred act of creation, the transformation of vision into form, and the recognition "
        "that you yourself are the most important work of art you will ever craft."
    ),
    15: (
        "The Moon in Swati grants you the freedom and flexibility of the wind itself. Ruled by "
        "Rahu and guided by Vayu, the wind god, your emotional nature is fiercely independent, "
        "adaptable, and resistant to any force that would constrain your movement. You bend "
        "without breaking through life's storms, maintaining an inner equilibrium that belies "
        "the changeability of your outer circumstances. Diplomacy, commerce, and negotiation "
        "are natural talents -- you instinctively find the path of least resistance toward your "
        "goals. Self-reliance is a core value, and you may resist emotional dependency even when "
        "intimacy would serve you. The challenge is restlessness and superficiality, scattering "
        "your energy across too many pursuits. Your life themes involve the art of true "
        "independence, the strength found in flexibility, and the wisdom to know when bending "
        "serves growth and when it represents avoidance."
    ),
    16: (
        "With the Moon in Vishakha, your emotional life is defined by an extraordinary single-"
        "pointedness of purpose. Ruled by Jupiter and empowered by both Indra and Agni, you "
        "possess the combined force of royal authority and sacred fire directed toward your "
        "chosen goal. Once you commit, nothing deters you -- you have the endurance to push "
        "through obstacles that would exhaust others many times over. Your ambition is not "
        "shallow striving but a deep inner compulsion to achieve something of lasting "
        "significance. The forked nature of Vishakha gives you versatility, but your greatest "
        "power lies in unwavering focus. The shadow includes obsessiveness, jealousy, and a "
        "ruthlessness that can damage relationships on the path to achievement. Your life themes "
        "center on the transformative power of dedication, the harvest that rewards patient "
        "cultivation, and learning that the goal is only meaningful if the path honors "
        "your highest values."
    ),
    17: (
        "The Moon in Anuradha bestows a remarkable capacity for devotion, friendship, and "
        "organizational leadership. Ruled by Saturn yet illuminated by Mitra, the god of "
        "friendship and sacred bonds, you combine discipline with genuine warmth in a way "
        "that draws devoted allies to your cause. Like the lotus that blooms in muddy water, "
        "you possess the gift of flourishing in harsh conditions and inspiring others through "
        "your steadfastness. Your emotional nature is deeply loyal, and you invest heavily in "
        "the relationships and organizations you believe in. Success in foreign lands or among "
        "people different from your own background is indicated. The challenges include emotional "
        "suppression, over-identification with groups, and difficulty trusting your own authority. "
        "Your life purpose revolves around the alchemy of devotion -- transforming the lead of "
        "hardship into the gold of enduring bonds and meaningful achievement."
    ),
    18: (
        "Born with the Moon in Jyeshtha, you embody the archetype of the elder protector, the "
        "one who has seen much and gained the authority to shield others. Ruled by Mercury and "
        "watched over by Indra, king of the gods, your emotional nature combines sharp intelligence "
        "with a protective fierceness that can be both inspiring and intimidating. You naturally "
        "gravitate toward positions of seniority and influence, earning your place through genuine "
        "merit and courage. The protective amulet that symbolizes Jyeshtha reflects your role as "
        "a guardian of those weaker than yourself. However, the burdens of leadership weigh "
        "heavily, and the shadows of arrogance, jealousy of peers, and the loneliness of "
        "authority are real. Your life themes involve learning that true power protects rather "
        "than dominates, that wisdom is earned through trial, and that the greatest victory "
        "is conquering your own darker impulses."
    ),
    19: (
        "The Moon in Mula places your emotional roots in the very foundation of existence, where "
        "creation and destruction are indistinguishable. Ruled by Ketu and governed by Nirriti, "
        "the goddess of calamity, your life may involve profound uprooting experiences that "
        "strip away everything superficial and force you to the bedrock of truth. You are a "
        "natural philosopher and investigator, compelled to tear apart accepted beliefs until "
        "you find what is genuinely real beneath them. This can manifest as brilliant research "
        "ability or as a destructive restlessness that sabotages the very stability you seek. "
        "The energy is fierce, uncompromising, and ultimately liberating. Your challenges include "
        "nihilism, self-destructive patterns, and the pain of repeatedly losing what you thought "
        "was permanent. Your life purpose centers on reaching the root -- of knowledge, of "
        "suffering, of existence itself -- and discovering that what cannot be destroyed is "
        "the only thing worth building upon."
    ),
    20: (
        "With the Moon in Purva Ashadha, you carry the invincible confidence of cosmic waters "
        "that purify everything they touch. Ruled by Venus and blessed by Apas, the goddess of "
        "water, your emotional nature is proud, principled, and possessed of an unshakeable "
        "conviction in your own vision. You are a natural orator and debater, able to articulate "
        "your truth with a persuasive force that can shift the thinking of those around you. "
        "Rejuvenation is a key theme -- you revitalize what has grown stale and bring fresh "
        "energy to established structures. Your artistic sensibility is refined, and you "
        "appreciate the power of declaration, of stating what you stand for with clarity. "
        "The shadow includes fanaticism, inability to compromise, and pride that blocks "
        "learning. Your life themes revolve around the purifying power of truth spoken boldly, "
        "the courage to stand by your convictions, and the wisdom to know that even the "
        "mightiest river must yield to the ocean."
    ),
    21: (
        "The Moon in Uttara Ashadha grants you the energy of final, unchallengeable victory "
        "achieved through righteousness and universal principles. Ruled by the Sun and guided "
        "by the ten Vishvadevas, your emotional nature is anchored in integrity, patience, and "
        "an unwavering commitment to doing what is right regardless of personal cost. Where "
        "Purva Ashadha declares war, you achieve the lasting peace that follows principled "
        "triumph. You are a natural leader whose authority comes not from aggression but from "
        "moral clarity. Others trust you instinctively because they sense the incorruptibility "
        "at your core. The challenges include inflexibility, self-righteousness, and an overly "
        "serious approach that denies the lighter side of life. Your life purpose involves "
        "enduring victory, the kind won not through force but through alignment with dharma -- "
        "proving that the patient, principled path ultimately prevails over all opposition."
    ),
    22: (
        "Born with the Moon in Shravana, you possess the sacred gift of deep listening -- the "
        "ability to hear what is truly being said beneath the surface of words. Ruled by the Moon "
        "and guided by Vishnu the preserver, your emotional nature is perceptive, learned, and "
        "profoundly connective. You absorb knowledge through attentive hearing and transmit it "
        "through teaching, counseling, or the arts of communication. Connection between people, "
        "between ideas, between traditions -- this is your essential work. You serve as a bridge "
        "across divides that others find impassable. Your intuition is rooted not in mystical "
        "vision but in the practical wisdom of really paying attention. The challenges include "
        "gossip, eavesdropping on what is not meant for you, and becoming so focused on "
        "listening to others that you neglect your own inner voice. Your life themes center "
        "on the transformative power of genuine listening, the preservation of sacred knowledge, "
        "and the understanding that wisdom begins with silence."
    ),
    23: (
        "The Moon in Dhanishta fills your emotional life with rhythm, abundance, and the resonant "
        "energy of the cosmic drum. Ruled by Mars and empowered by the eight Vasus, the elemental "
        "gods of nature, you are attuned to the underlying beat that orchestrates the material "
        "world. Musical talent, a sense of timing, and the ability to create wealth through "
        "action are natural gifts. You possess a generous, outgoing nature that attracts "
        "prosperity and social recognition. Your energy is dynamic, and you thrive in "
        "environments that reward boldness and rhythmic precision. The shadow side includes "
        "aggression, possessiveness over resources, and a tendency to overpower others with "
        "your forceful personality. Your life themes revolve around the harmony of abundance, "
        "the rhythm that unites effort and reward, and discovering that true wealth is measured "
        "not in possessions but in the music you bring to the world."
    ),
    24: (
        "With the Moon in Shatabhisha, you are the solitary healer, the keeper of ancient "
        "secrets, the one who sees through the veil of illusion. Ruled by Rahu and governed "
        "by Varuna, the lord of cosmic law and the deep waters, your emotional nature is "
        "philosophical, intensely private, and oriented toward unconventional wisdom. You are "
        "drawn to alternative medicine, esoteric knowledge, and the hidden patterns that govern "
        "reality. Your healing abilities operate on a different frequency than conventional "
        "approaches, often achieving results that defy explanation. Solitude is not merely "
        "comfortable for you but necessary -- you recharge through withdrawal and reflection. "
        "The challenges include isolation, paranoia, and difficulty forming intimate connections. "
        "Your life themes center on the hundred healers contained within your single being, "
        "the courage to pursue truth beyond the boundaries of accepted knowledge, and the "
        "eventual recognition that even the most solitary healer needs the warmth of human "
        "connection."
    ),
    25: (
        "The Moon in Purva Bhadrapada ignites your emotional nature with the fierce, "
        "transformative fire of spiritual aspiration. Ruled by Jupiter and governed by Aja "
        "Ekapada, the one-footed cosmic serpent of fire, you oscillate between intense worldly "
        "passion and equally intense spiritual yearning. This duality can produce remarkable "
        "range -- you may be both the ascetic and the revolutionary, the mystic and the "
        "activist. Your convictions burn with an intensity that can inspire or alarm others. "
        "The energy of radical change courses through you, demanding expression. You are "
        "unafraid of extremes, and your willingness to destroy what is corrupt makes you "
        "a potent force for transformation. The challenges include fanaticism, instability, "
        "and the tendency to burn bridges that still had value. Your life purpose involves "
        "channeling spiritual fire into constructive transformation, learning to hold both "
        "the sacred and the worldly in a single unflinching gaze."
    ),
    26: (
        "Born with the Moon in Uttara Bhadrapada, your emotional nature draws from the deepest "
        "wells of cosmic compassion and controlled spiritual power. Ruled by Saturn and watched "
        "over by Ahir Budhnya, the serpent of the deep, you embody the calm that follows the "
        "storm of Purva Bhadrapada. Where your predecessor nakshatra blazes, you contain and "
        "direct that fire with masterful discipline. Your compassion is not sentimental but "
        "profound -- rooted in genuine understanding of suffering and the patience to sit with "
        "others in their pain. You are emotionally steady to a degree that astonishes those "
        "around you, providing shelter and stability in turbulent times. The shadow includes "
        "emotional suppression, martyrdom, and withdrawal into inaccessible depths. Your life "
        "themes center on the power of deep, sustained compassion, the stability that comes "
        "from having weathered inner storms, and selfless service as the highest expression "
        "of spiritual attainment."
    ),
    27: (
        "The Moon in Revati marks the final chapter of the soul's journey through the "
        "nakshatras, and you carry the gentle, luminous wisdom of completion. Ruled by Mercury "
        "and guided by Pushan, the nourishing protector of travelers and livestock, your "
        "emotional nature is tender, empathetic, and infused with an otherworldly sweetness "
        "that touches everyone you meet. You are a natural caretaker who guides others through "
        "life's transitions with patience and understanding. Your empathy is so strong that "
        "you absorb the pain and joy of those around you, which is both your gift and your "
        "vulnerability. Creative imagination is vivid, often carrying a dreamlike, transcendent "
        "quality. The challenges include naivety, difficulty establishing boundaries, and a "
        "tendency to lose yourself in others' needs. Your life themes revolve around safe "
        "passage -- helping others navigate endings and beginnings with grace, while learning "
        "that the soul's journey, like the zodiac itself, is a circle that always returns home."
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_nakshatra_details(nakshatra_num: int) -> dict:
    """Return the full nakshatra data dictionary for a given number.

    Args:
        nakshatra_num: Nakshatra number from 1 (Ashwini) to 27 (Revati).

    Returns:
        Dictionary containing name, lord, deity, symbol, shakti, motivation,
        guna, gender, animal, caste, quality, and description.

    Raises:
        ValueError: If nakshatra_num is not between 1 and 27.
    """
    if not 1 <= nakshatra_num <= 27:
        raise ValueError(f"Nakshatra number must be 1-27, got {nakshatra_num}")
    return NAKSHATRA_DATA[nakshatra_num - 1]


def interpret_moon_nakshatra(nakshatra_num: int) -> str:
    """Generate a comprehensive Janma Nakshatra reading for the Moon's birth nakshatra.

    The Janma Nakshatra is one of the most important factors in Vedic astrology,
    shaping personality, emotional constitution, life themes, and karmic direction.

    Args:
        nakshatra_num: Nakshatra number 1-27.

    Returns:
        A rich, multi-sentence interpretation string (5-8 sentences) covering
        nakshatra name, lord, deity, symbol, motivation, guna, personality traits,
        life themes, strengths, and challenges.

    Raises:
        ValueError: If nakshatra_num is not between 1 and 27.
    """
    if not 1 <= nakshatra_num <= 27:
        raise ValueError(f"Nakshatra number must be 1-27, got {nakshatra_num}")

    data = NAKSHATRA_DATA[nakshatra_num - 1]
    name = data['name']
    lord = data['lord']
    deity = data['deity']
    symbol = data['symbol']
    motivation = data['motivation']
    guna = data['guna']

    header = (
        f"Your Janma Nakshatra is {name}, the {_ordinal(nakshatra_num)} lunar mansion, "
        f"ruled by {lord} with {deity} as its presiding deity. "
        f"Its symbol is the {symbol.lower()}, its primary motivation is {motivation}, "
        f"and it operates through the quality of {guna}."
    )

    body = _MOON_NAKSHATRA_INTERPRETATIONS.get(nakshatra_num, data['description'])

    return f"{header}\n\n{body}"


def interpret_planet_in_nakshatra(planet: str, nakshatra_num: int, pada: int) -> str:
    """Interpret how a specific planet expresses through a nakshatra and pada.

    Combines the planet's core signification with the nakshatra's energy and
    provides pada-specific notes based on the Dharma-Artha-Kama-Moksha cycle.

    Args:
        planet: Planet name (e.g., 'Sun', 'Moon', 'Mars').
        nakshatra_num: Nakshatra number 1-27.
        pada: Pada number 1-4.

    Returns:
        A 2-3 sentence interpretation combining planet signification with
        nakshatra energy and pada-specific orientation.

    Raises:
        ValueError: If nakshatra_num is not 1-27 or pada is not 1-4.
    """
    if not 1 <= nakshatra_num <= 27:
        raise ValueError(f"Nakshatra number must be 1-27, got {nakshatra_num}")
    if not 1 <= pada <= 4:
        raise ValueError(f"Pada must be 1-4, got {pada}")

    data = NAKSHATRA_DATA[nakshatra_num - 1]
    nak_name = data['name']
    nak_lord = data['lord']
    nak_deity = data['deity']
    nak_quality = data['quality'].lower()
    nak_shakti = data['shakti'].lower()

    planet_info = _PLANET_KEYWORDS.get(planet)
    if planet_info:
        planet_domain, planet_style, planet_essence = planet_info
    else:
        planet_domain = 'its natural significations'
        planet_style = 'characteristic'
        planet_essence = 'its essential nature'

    # Navamsha sign for this pada
    navamsha_index = ((nakshatra_num - 1) * 4 + (pada - 1)) % 12
    navamsha_sign = _NAVAMSHA_SIGNS[navamsha_index]

    # Pada theme
    pada_label, pada_desc = _PADA_THEMES[pada]

    # Build the interpretation
    planet_nak_text = (
        f"{planet} in {nak_name} nakshatra channels {planet_essence} through "
        f"the {nak_quality} energy of {nak_deity}, expressing the {nak_shakti}. "
        f"The themes of {planet_domain} take on a {planet_style} quality colored by "
        f"{nak_lord}'s influence, giving a distinctive approach to how this planet "
        f"operates in the chart."
    )

    pada_text = (
        f"In the {_ordinal(pada)} pada ({pada_label} orientation, {navamsha_sign} navamsha), "
        f"this placement directs {planet}'s energy toward {pada_desc}, "
        f"adding a layer of {navamsha_sign} qualities to the expression."
    )

    return f"{planet_nak_text} {pada_text}"


def get_nakshatra_compatibility(nak1: int, nak2: int) -> str:
    """Assess basic compatibility between two nakshatras for relationship analysis.

    Uses a simplified Kuta system based on nakshatra lords and their
    natural friendship/enmity relationships, supplemented by guna and
    motivation comparison for neutral cases.

    Args:
        nak1: First nakshatra number 1-27.
        nak2: Second nakshatra number 1-27.

    Returns:
        A brief compatibility statement describing the nature of the
        relationship between the two nakshatras.

    Raises:
        ValueError: If either nakshatra number is not between 1 and 27.
    """
    if not 1 <= nak1 <= 27:
        raise ValueError(f"First nakshatra number must be 1-27, got {nak1}")
    if not 1 <= nak2 <= 27:
        raise ValueError(f"Second nakshatra number must be 1-27, got {nak2}")

    name1 = NAKSHATRA_NAMES[nak1 - 1]
    name2 = NAKSHATRA_NAMES[nak2 - 1]
    lord1 = NAKSHATRA_LORDS[nak1 - 1]
    lord2 = NAKSHATRA_LORDS[nak2 - 1]

    data1 = NAKSHATRA_DATA[nak1 - 1]
    data2 = NAKSHATRA_DATA[nak2 - 1]

    # Same nakshatra
    if nak1 == nak2:
        return (
            f"Both individuals share {name1} nakshatra, ruled by {lord1}. "
            f"This creates an instinctive understanding and deep resonance between "
            f"them, as they operate on the same emotional wavelength. However, "
            f"the same weaknesses may also be amplified, requiring conscious "
            f"effort to balance shared blind spots."
        )

    # Same lord
    if lord1 == lord2:
        return (
            f"{name1} (ruled by {lord1}) and {name2} (also ruled by {lord2}) share "
            f"the same planetary lord, creating a natural affinity and sympathetic "
            f"resonance between the two individuals. They are likely to understand "
            f"each other's emotional rhythms and life approach intuitively, as "
            f"both nakshatras pulse to the same planetary frequency."
        )

    # Determine lord relationships
    lord1_friends = NATURAL_FRIENDS.get(lord1, [])
    lord1_enemies = NATURAL_ENEMIES.get(lord1, [])
    lord2_friends = NATURAL_FRIENDS.get(lord2, [])
    lord2_enemies = NATURAL_ENEMIES.get(lord2, [])

    # Mutual friendship
    if lord2 in lord1_friends and lord1 in lord2_friends:
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) enjoy "
            f"strong compatibility, as their planetary lords share a mutual "
            f"friendship. This creates a harmonious exchange of energies where "
            f"both individuals naturally support and uplift each other. "
            f"Communication flows easily, and differences tend to complement "
            f"rather than conflict."
        )

    # One-sided friendship (at least one considers the other a friend, neither is enemy)
    if (lord2 in lord1_friends or lord1 in lord2_friends) and \
       lord2 not in lord1_enemies and lord1 not in lord2_enemies:
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) have "
            f"a generally compatible relationship, though the ease of connection "
            f"may be felt more strongly by one partner than the other. Their "
            f"planetary lords are on friendly or neutral terms, allowing for "
            f"cooperation with some effort. Understanding each other's different "
            f"emotional needs will strengthen the bond."
        )

    # Mutual enmity
    if lord2 in lord1_enemies and lord1 in lord2_enemies:
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) face "
            f"significant compatibility challenges, as their planetary lords are "
            f"mutual enemies. This creates fundamental tensions in values, "
            f"emotional expression, and life priorities. The relationship requires "
            f"conscious effort, patience, and willingness to appreciate "
            f"fundamentally different approaches to life. Growth through "
            f"challenge is the gift this combination offers."
        )

    # One-sided enmity
    if lord2 in lord1_enemies or lord1 in lord2_enemies:
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) have "
            f"a mixed compatibility profile. There is an undercurrent of tension "
            f"from at least one direction, as one nakshatra lord holds the other "
            f"in enmity. This does not preclude a meaningful relationship, but it "
            f"requires awareness of friction points and a willingness to work "
            f"through periodic discord. The areas ruled by the conflicting lords "
            f"will be where adjustments are most needed."
        )

    # Neutral relationship -- use guna and motivation as tiebreakers
    same_guna = data1.get('guna') == data2.get('guna')
    same_motivation = data1.get('motivation') == data2.get('motivation')

    if same_guna and same_motivation:
        guna = data1['guna']
        motivation = data1['motivation']
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) have "
            f"a neutral lord relationship, but share both {guna} guna and "
            f"{motivation} motivation, creating a deeper resonance than their "
            f"lords alone would suggest. They approach life with a similar "
            f"fundamental orientation, and this shared rhythm can form a solid "
            f"foundation for understanding."
        )
    elif same_guna:
        guna = data1['guna']
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) have "
            f"a neutral compatibility based on their planetary lords, neither "
            f"strongly attracting nor repelling each other. Their shared {guna} "
            f"guna provides some common ground in temperament. The relationship "
            f"is workable and depends more on other chart factors and personal "
            f"effort than on inherent nakshatra chemistry."
        )
    elif same_motivation:
        motivation = data1['motivation']
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) are "
            f"neutrally disposed toward each other through their planetary lords, "
            f"but share {motivation} as their primary motivation, providing a "
            f"common sense of purpose. The relationship is neither strongly "
            f"supported nor obstructed by nakshatra compatibility, and other "
            f"chart factors will play a more decisive role."
        )
    else:
        return (
            f"{name1} (ruled by {lord1}) and {name2} (ruled by {lord2}) have "
            f"a neutral compatibility profile. Their planetary lords are neither "
            f"friends nor enemies, and their gunas and motivations differ, "
            f"creating neither strong attraction nor repulsion. This is a "
            f"relationship where individual effort and other chart factors "
            f"will determine the outcome more than inherent nakshatra affinity."
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ordinal(n: int) -> str:
    """Return ordinal string for an integer (1st, 2nd, etc.)."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"
