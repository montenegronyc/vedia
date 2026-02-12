"""House signification and interpretation text for Vedic astrology."""

from ..models import SIGNS, SIGN_LORDS


HOUSE_SIGNIFICATIONS = {
    1: {
        'name': 'Lagna / Tanu Bhava',
        'category': 'Kendra (Angular) / Trikona (Trine)',
        'element': 'Dharma',
        'areas': 'Self, personality, physical body, constitution, appearance, vitality, general fortune, head, brain',
        'body_parts': 'Head, brain, complexion, general vitality',
        'relations': 'Self, overall personality projection',
        'positive': 'Strong health, attractive personality, self-confidence, good fortune, leadership ability, recognized by others',
        'negative': 'Poor health, weak constitution, lack of confidence, obscured identity, self-centered tendencies',
        'karaka': 'Sun',
    },
    2: {
        'name': 'Dhana Bhava',
        'category': 'Maraka (Killer) / Panapara (Succedent)',
        'element': 'Artha',
        'areas': 'Wealth, family, speech, food, face, right eye, early education, values, accumulated resources',
        'body_parts': 'Face, right eye, mouth, teeth, tongue, nose, speech organs',
        'relations': 'Immediate family, family of origin',
        'positive': 'Wealth accumulation, sweet speech, good family life, nutritious food, strong values, beautiful face',
        'negative': 'Financial difficulties, harsh speech, family conflicts, poor diet, weak values, dental/eye problems',
        'karaka': 'Jupiter',
    },
    3: {
        'name': 'Sahaja Bhava',
        'category': 'Upachaya (Growing) / Apoklima (Cadent)',
        'element': 'Kama',
        'areas': 'Courage, siblings, communication, short travels, efforts, hobbies, arms, writing, media, performing arts',
        'body_parts': 'Arms, hands, shoulders, right ear, upper chest, throat',
        'relations': 'Younger siblings, neighbors, co-workers',
        'positive': 'Courage, strong siblings, good communication, writing talent, artistic ability, successful efforts',
        'negative': 'Cowardice, sibling conflicts, communication problems, failed efforts, hearing issues',
        'karaka': 'Mars',
    },
    4: {
        'name': 'Sukha Bhava',
        'category': 'Kendra (Angular)',
        'element': 'Moksha',
        'areas': 'Mother, home, property, vehicles, emotional happiness, education, chest, heart, inner peace, homeland',
        'body_parts': 'Chest, heart, lungs, breast area',
        'relations': 'Mother, maternal figures',
        'positive': 'Happy home life, good education, property ownership, vehicles, close to mother, inner peace, patriotic',
        'negative': 'Domestic disturbance, property losses, vehicle problems, distant from mother, emotional unrest, heart ailments',
        'karaka': 'Moon',
    },
    5: {
        'name': 'Putra Bhava',
        'category': 'Trikona (Trine) / Panapara (Succedent)',
        'element': 'Dharma',
        'areas': 'Children, intelligence, creativity, romance, speculation, past-life merit (poorva punya), mantras, education, stomach',
        'body_parts': 'Stomach, upper abdomen, liver area, back',
        'relations': 'Children, romantic partners, students',
        'positive': 'Blessed children, sharp intelligence, creative talent, romantic happiness, speculative gains, spiritual merit',
        'negative': 'Problems with children, dull intellect, creative blocks, romantic disappointments, speculative losses',
        'karaka': 'Jupiter',
    },
    6: {
        'name': 'Shatru Bhava',
        'category': 'Trik (Dusthana) / Upachaya (Growing)',
        'element': 'Artha',
        'areas': 'Enemies, diseases, debts, service, competition, obstacles, maternal uncle, digestive system, daily work',
        'body_parts': 'Intestines, lower abdomen, kidneys, navel area',
        'relations': 'Enemies, competitors, maternal uncle, servants, employees',
        'positive': 'Victory over enemies, disease-free, debt-free, excellent service record, competitive success',
        'negative': 'Chronic enemies, diseases, debts, service difficulties, legal troubles, digestive disorders',
        'karaka': 'Mars / Saturn',
    },
    7: {
        'name': 'Kalatra Bhava',
        'category': 'Kendra (Angular) / Maraka (Killer)',
        'element': 'Kama',
        'areas': 'Marriage, partnerships, business partners, foreign travel, public dealings, reproduction, lower abdomen',
        'body_parts': 'Lower abdomen, kidneys, reproductive organs, bladder',
        'relations': 'Spouse, business partners, the public, open enemies',
        'positive': 'Happy marriage, successful partnerships, good public relations, foreign travel success',
        'negative': 'Marriage difficulties, partnership conflicts, public opposition, reproductive issues',
        'karaka': 'Venus',
    },
    8: {
        'name': 'Ayu Bhava',
        'category': 'Trik (Dusthana) / Panapara (Succedent)',
        'element': 'Moksha',
        'areas': 'Longevity, sudden events, transformation, occult, inheritance, chronic illness, research, death, hidden matters',
        'body_parts': 'Reproductive organs, chronic disease areas, anus, pelvic region',
        'relations': 'In-laws, partner\'s family',
        'positive': 'Longevity, inheritance, research ability, occult knowledge, transformative growth, insurance gains',
        'negative': 'Chronic illness, sudden losses, accidents, scandals, difficulties with in-laws, psychological crises',
        'karaka': 'Saturn',
    },
    9: {
        'name': 'Dharma Bhava',
        'category': 'Trikona (Trine) / Apoklima (Cadent)',
        'element': 'Dharma',
        'areas': 'Father, guru, dharma, fortune, higher education, philosophy, religion, long journeys, law, ethics, hips/thighs',
        'body_parts': 'Hips, thighs, arterial system',
        'relations': 'Father, guru/teacher, spiritual guides',
        'positive': 'Good fortune, spiritual wisdom, blessed father, excellent higher education, ethical nature, pilgrimage',
        'negative': 'Bad fortune, irreligion, problems with father/guru, educational obstacles, legal troubles',
        'karaka': 'Sun / Jupiter',
    },
    10: {
        'name': 'Karma Bhava',
        'category': 'Kendra (Angular) / Upachaya (Growing)',
        'element': 'Artha',
        'areas': 'Career, profession, status, reputation, authority, government, public life, knees, fame, achievement',
        'body_parts': 'Knees, joints, patella, skeletal structure',
        'relations': 'Boss, authority figures, government officials',
        'positive': 'Successful career, public recognition, high status, government favor, professional authority',
        'negative': 'Career obstacles, loss of status, public humiliation, government problems, professional failures',
        'karaka': 'Sun / Mercury / Jupiter / Saturn',
    },
    11: {
        'name': 'Labha Bhava',
        'category': 'Upachaya (Growing) / Panapara (Succedent)',
        'element': 'Kama',
        'areas': 'Gains, income, fulfillment of desires, elder siblings, friends, social networks, ankles, left ear',
        'body_parts': 'Ankles, calves, left ear, shins',
        'relations': 'Elder siblings, friends, patrons, social circles',
        'positive': 'Substantial gains, fulfilled desires, strong friendships, elder sibling support, large income',
        'negative': 'Unfulfilled desires, loss of gains, friendships lost, sibling difficulties, ankle/leg problems',
        'karaka': 'Jupiter',
    },
    12: {
        'name': 'Vyaya Bhava',
        'category': 'Trik (Dusthana) / Apoklima (Cadent)',
        'element': 'Moksha',
        'areas': 'Losses, expenses, foreign lands, liberation (moksha), sleep, bed pleasures, confinement, left eye, feet',
        'body_parts': 'Feet, left eye, sleep quality',
        'relations': 'Foreign contacts, spiritual communities, secret enemies',
        'positive': 'Spiritual liberation, foreign success, good sleep, bed pleasures, charitable nature, moksha',
        'negative': 'Excessive expenses, imprisonment, hospitalization, exile, insomnia, secret enemies, feet problems',
        'karaka': 'Saturn / Ketu',
    },
}


# Short labels for houses used in generated interpretation text.
_HOUSE_SHORT_LABELS = {
    1: 'self and personality',
    2: 'wealth and family',
    3: 'courage and communication',
    4: 'home and happiness',
    5: 'children and creativity',
    6: 'enemies and health challenges',
    7: 'marriage and partnerships',
    8: 'transformation and longevity',
    9: 'dharma and fortune',
    10: 'career and public status',
    11: 'gains and aspirations',
    12: 'losses and spiritual liberation',
}


# House classification sets used by the framework generator.
_KENDRA_HOUSES = {1, 4, 7, 10}
_TRIKONA_HOUSES = {1, 5, 9}
_DUSTHANA_HOUSES = {6, 8, 12}
_UPACHAYA_HOUSES = {3, 6, 10, 11}
_MARAKA_HOUSES = {2, 7}


def _classify_lord_placement(lord_house: int) -> str:
    """Classify the house where a lord is placed and return a keyword.

    The classification reflects the traditional Vedic assessment of how well
    a house lord functions when placed in various houses.

    Returns one of: 'own', 'kendra', 'trikona', 'dusthana_6', 'dusthana_8',
    'dusthana_12', 'upachaya_3', 'upachaya_11', 'neutral_2'.
    """
    if lord_house in _TRIKONA_HOUSES:
        return 'trikona'
    if lord_house in _KENDRA_HOUSES:
        return 'kendra'
    if lord_house == 11:
        return 'upachaya_11'
    if lord_house == 3:
        return 'upachaya_3'
    if lord_house == 6:
        return 'dusthana_6'
    if lord_house == 8:
        return 'dusthana_8'
    if lord_house == 12:
        return 'dusthana_12'
    # 2 is a neutral/maraka house
    return 'neutral_2'


# Framework text fragments keyed by the classification of the target house.
# Used when no specific _LORD_IN_HOUSE entry exists.
_PLACEMENT_FRAMEWORK = {
    'own': (
        "The lord is placed in its own house, greatly strengthening that "
        "house's significations. The native experiences reliable, self-sustained "
        "results in this area of life, with the house themes flourishing under "
        "their own lord's protection."
    ),
    'kendra': (
        "The lord is placed in a kendra (angular) house, providing strong "
        "foundational support. Kendra placement of a house lord gives stability, "
        "visibility, and the ability to manifest that house's potential through "
        "direct action and tangible results in the world."
    ),
    'trikona': (
        "The lord is placed in a trikona (trine) house, which is highly "
        "auspicious. Trikona placement brings dharmic support, past-life merit, "
        "and fortunate developments related to the house's themes. This is one "
        "of the most favorable configurations for any house lord."
    ),
    'upachaya_11': (
        "The lord is placed in the 11th house of gains, connecting that "
        "house's significations to income, fulfilled desires, and social "
        "networking. The native achieves the house's goals through friendships, "
        "elder siblings, and community involvement. Material results improve "
        "steadily over time."
    ),
    'upachaya_3': (
        "The lord is placed in the 3rd house, indicating that the house's "
        "results require sustained personal effort, courage, and initiative. "
        "Success does not come easily but develops through communication, "
        "short journeys, and self-reliant action. Siblings may play a role."
    ),
    'dusthana_6': (
        "The lord is placed in the 6th house (dusthana), indicating challenges "
        "through enemies, health issues, debts, or litigation affecting that "
        "house's significations. The native must overcome obstacles and may "
        "channel the house's energy into service, healing, or competitive fields."
    ),
    'dusthana_8': (
        "The lord is placed in the 8th house (dusthana), indicating "
        "transformation, sudden disruptions, or hidden factors affecting that "
        "house's themes. The native may experience delays, obstacles, or "
        "upheaval, but also gains through research, inheritance, or deep "
        "psychological insight."
    ),
    'dusthana_12': (
        "The lord is placed in the 12th house (dusthana), indicating losses, "
        "expenditure, or dissipation of that house's significations. However, "
        "foreign connections, spiritual growth, or behind-the-scenes activity "
        "may redirect the energy toward liberation and transcendence."
    ),
    'neutral_2': (
        "The lord is placed in the 2nd house, connecting that house's themes "
        "to wealth, family, and speech. The native's financial status and "
        "family values are influenced by the source house, and resources may "
        "accumulate through its significations."
    ),
}


# Lord placement interpretations: what it means when lord of house X is in house Y.
# Indexed as LORD_IN_HOUSE[from_house][to_house].
# All 144 combinations are provided for the 12 source houses.
LORD_IN_HOUSE = {
    1: {
        1: "The 1st lord in the 1st house indicates a self-made individual with strong personality, good health, and natural confidence. The native's identity and life direction are self-determined, with a strong physical constitution and ability to overcome obstacles through personal effort.",
        2: "The 1st lord in the 2nd house connects the self to wealth, family, and speech. The native earns through personal effort and their identity is closely tied to family values and financial status. Speech reflects personality strongly.",
        3: "The 1st lord in the 3rd house gives a courageous, communicative nature that thrives on personal initiative and effort. The native may be a writer, performer, or entrepreneur whose identity is expressed through creative courage. Siblings play an important role.",
        4: "The 1st lord in the 4th house connects the self to home, mother, and education. The native finds happiness through domestic life, property, and emotional security. Academic achievement and comfortable surroundings are important to identity.",
        5: "The 1st lord in the 5th house connects personality to intelligence, creativity, and children. The native is naturally creative and may be drawn to education, speculation, or artistic pursuits. Past-life merit supports present fortune.",
        6: "The 1st lord in the 6th house (dusthana) may indicate health challenges, tendency toward conflict, or a service-oriented identity. The native may work in health, law, or competitive fields. Overcoming obstacles becomes central to life purpose.",
        7: "The 1st lord in the 7th house strongly connects identity to partnerships and marriage. The native defines themselves through relationships and may live in foreign places. Business partnerships are central to personal success.",
        8: "The 1st lord in the 8th house (dusthana) may indicate a life marked by transformation, hidden pursuits, and challenges to vitality. The native may be drawn to research, occult studies, or insurance. Health requires attention, but longevity can be good with other support.",
        9: "The 1st lord in the 9th house is very favorable, connecting the self to dharma, fortune, and higher knowledge. The native is naturally ethical, fortunate, and drawn to spiritual or philosophical pursuits. Father is a positive influence on identity.",
        10: "The 1st lord in the 10th house is very favorable, connecting the self to career and public recognition. The native's identity is closely tied to professional achievement, and career success comes through personal effort and charisma.",
        11: "The 1st lord in the 11th house connects the self to gains, social networks, and fulfillment of desires. The native achieves personal goals through friendships and community involvement. Income from personal effort is substantial.",
        12: "The 1st lord in the 12th house (dusthana) may indicate foreign residence, spiritual inclination, or challenges to physical vitality. The native may find purpose through selfless service, meditation, or life abroad. Expenses may drain personal resources.",
    },
    2: {
        1: "The 2nd lord in the 1st house brings wealth and family values to the forefront of personality. The native is identified with their financial status and family heritage. Self-effort directly generates income.",
        2: "The 2nd lord in the 2nd house strengthens wealth accumulation, family bonds, and speech quality. The native retains and grows resources effectively and has a strong connection to family traditions.",
        3: "The 2nd lord in the 3rd house indicates earnings through communication, writing, siblings, or short-distance trade. The native's financial success depends on personal initiative and courage.",
        4: "The 2nd lord in the 4th house indicates wealth through property, vehicles, or mother's influence. Family resources support education and domestic comfort. Inherited wealth from the maternal side is possible.",
        5: "The 2nd lord in the 5th house indicates wealth through speculation, creativity, or children. The native accumulates through intelligent investment and creative ventures. Past-life merit supports financial fortune.",
        6: "The 2nd lord in the 6th house may indicate financial difficulties through enemies, debts, or health expenses. Wealth may be gained through service, competition, or the medical/legal field, but with fluctuation.",
        7: "The 2nd lord in the 7th house indicates wealth through marriage, partnerships, or foreign trade. The spouse may contribute significantly to family finances. Business partnerships are profitable.",
        8: "The 2nd lord in the 8th house may indicate financial instability, inheritance, or wealth through hidden means. Family finances may experience sudden changes. Insurance, research, or occult knowledge may be income sources.",
        9: "The 2nd lord in the 9th house indicates wealth through dharmic activities, higher education, or father's influence. Family values align with spiritual principles. Fortune supports financial growth.",
        10: "The 2nd lord in the 10th house indicates wealth through career and professional achievement. The native's earning power is tied to their public reputation and professional status.",
        11: "The 2nd lord in the 11th house is very favorable for wealth, indicating substantial gains, multiple income streams, and fulfillment of financial desires. Family support and networking contribute to prosperity.",
        12: "The 2nd lord in the 12th house may indicate financial losses, expenditure exceeding income, or wealth directed toward spiritual purposes. Foreign investments or expenses may be significant.",
    },
    3: {
        1: "The 3rd lord in the 1st house gives a courageous, communicative personality. The native identifies strongly with their creative efforts, writing, or relationship with siblings. Personal initiative drives success.",
        2: "The 3rd lord in the 2nd house indicates income through communication, writing, or sibling connections. Courage in speech generates financial returns. Short-distance trade may be profitable.",
        3: "The 3rd lord in the 3rd house strengthens communication abilities, courage, and sibling relationships. The native is a natural communicator with strong personal initiative and creative talent.",
        4: "The 3rd lord in the 4th house connects creative efforts to home life and emotional fulfillment. The native may write from home, have creative siblings, or find courage through emotional security.",
        5: "The 3rd lord in the 5th house connects communication and courage to creativity and intelligence. The native excels in creative writing, performing arts, or courageous speculation.",
        6: "The 3rd lord in the 6th house may indicate conflicts with siblings or courage expressed through competition and service. The native overcomes obstacles through personal effort and communication skill.",
        7: "The 3rd lord in the 7th house connects communication and courage to partnerships. The native may have a communicative spouse or engage in partnership-based creative ventures.",
        8: "The 3rd lord in the 8th house may indicate challenges with siblings or transformation through courageous action. Research-oriented writing and communication about hidden subjects are favored.",
        9: "The 3rd lord in the 9th house connects communication and creative effort to higher learning and dharma. The native may publish philosophical works or travel for educational purposes.",
        10: "The 3rd lord in the 10th house indicates a career in communication, writing, media, or travel. The native's professional identity is built on creative effort and courageous initiative.",
        11: "The 3rd lord in the 11th house indicates gains through communication, siblings, and creative ventures. Personal effort translates directly into fulfilled desires and income growth.",
        12: "The 3rd lord in the 12th house may indicate separation from siblings, foreign travel for creative purposes, or communication directed toward spiritual topics.",
    },
    4: {
        1: "The 4th lord in the 1st house brings domestic happiness, mother's influence, and educational achievement into the personality. The native's identity is shaped by home life, and they project warmth and emotional depth.",
        2: "The 4th lord in the 2nd house connects home and property to wealth accumulation. The native may profit from real estate, family inheritance, or mother's financial support. Emotional values shape spending.",
        3: "The 4th lord in the 3rd house connects domestic life to communication and siblings. The native may work from home in communication fields or live near siblings. Short travels bring emotional satisfaction.",
        4: "The 4th lord in the 4th house is favorable, strengthening domestic happiness, educational success, and relationship with mother. The native enjoys a comfortable, stable home life and may own multiple properties.",
        5: "The 4th lord in the 5th house connects home life to children, creativity, and intelligence. The native finds emotional fulfillment through creative expression and may have a home-based creative practice.",
        6: "The 4th lord in the 6th house may indicate domestic disturbances, property disputes, or mother's health challenges. The native may need to serve or care for the mother, or face legal issues with property.",
        7: "The 4th lord in the 7th house connects domestic life to marriage and partnerships. The native's marital happiness is closely tied to home life. Property may be gained through the spouse.",
        8: "The 4th lord in the 8th house may indicate sudden changes in domestic life, property losses, or transformation of the home environment. Mother's health may be a concern. Hidden property may surface.",
        9: "The 4th lord in the 9th house connects home life to father, dharma, and higher learning. The native may live in educational or religious settings. Mother and father's relationship influences domestic peace.",
        10: "The 4th lord in the 10th house connects home to career, indicating a career in real estate, education, or based from the home. The native's professional life is deeply influenced by domestic foundations.",
        11: "The 4th lord in the 11th house indicates gains through property, vehicles, or mother's connections. Domestic happiness contributes to the fulfillment of desires. Elder siblings may support home life.",
        12: "The 4th lord in the 12th house may indicate loss of property, residence in foreign lands, or emotional detachment from home. The native may find spiritual peace away from their birthplace.",
    },
    5: {
        1: "The 5th lord in the 1st house gives a creative, intelligent personality blessed with past-life merit. The native's identity is defined by their intellect, creativity, and relationship with children.",
        2: "The 5th lord in the 2nd house indicates wealth through intelligence, speculation, or children. Creative talent generates income, and family values support educational development.",
        3: "The 5th lord in the 3rd house connects intelligence and creativity to communication and personal effort. The native may excel in creative writing, performance, or intellectually driven commerce.",
        4: "The 5th lord in the 4th house connects children and creativity to home life and emotional happiness. The native finds creative fulfillment at home and may educate their children personally.",
        5: "The 5th lord in the 5th house strengthens all 5th house significations: sharp intellect, blessed children, creative talent, romantic happiness, and strong past-life merit. Speculative ventures may prosper.",
        6: "The 5th lord in the 6th house may indicate challenges with children, obstacles to creative expression, or intelligence applied to competition and problem-solving. Medical or legal intelligence may develop.",
        7: "The 5th lord in the 7th house connects romance and creativity to marriage and partnerships. The native may meet their spouse through creative or educational settings. Children benefit partnerships.",
        8: "The 5th lord in the 8th house may indicate difficulties with children, speculation losses, or transformation through creative crisis. Deep research ability and occult intelligence develop through challenges.",
        9: "The 5th lord in the 9th house is very favorable, connecting intelligence and past-life merit to dharma and fortune. The native is blessed with wisdom, fortunate children, and spiritual creativity.",
        10: "The 5th lord in the 10th house indicates a career built on intelligence, creativity, or connection to children and education. The native achieves professional recognition through creative accomplishment.",
        11: "The 5th lord in the 11th house indicates gains through intelligence, speculation, children, or creative ventures. Creative talent translates into fulfilled desires and substantial income.",
        12: "The 5th lord in the 12th house may indicate losses through speculation, separation from children, or creativity directed toward spiritual and foreign pursuits.",
    },
    6: {
        1: "The 6th lord in the 1st house brings themes of competition, health challenges, or service into the personality. The native may struggle with chronic health issues or define themselves through overcoming obstacles.",
        2: "The 6th lord in the 2nd house may indicate financial strain through debts, health expenses, or family conflicts. Speech may be critical or harsh. Earning through medical or legal service is possible.",
        3: "The 6th lord in the 3rd house connects service and competition to communication and siblings. The native may have competitive siblings or express themselves through service-oriented writing or media.",
        4: "The 6th lord in the 4th house may disturb domestic peace through health issues, enemies, or disputes related to property. Mother's health may be a concern. Home may feel like a place of duty.",
        5: "The 6th lord in the 5th house may challenge children, creative expression, or speculative ventures through obstacles and competition. Intelligence is applied to solving complex problems.",
        6: "The 6th lord in the 6th house (Viparita Raja Yoga potential) can be favorable for overcoming enemies and diseases decisively. The native's obstacles tend to self-destruct. Medical and legal skills are strong.",
        7: "The 6th lord in the 7th house may bring conflict into marriage and partnerships. The spouse may have health challenges, or partnerships involve competitive dynamics. Legal disputes with partners are possible.",
        8: "The 6th lord in the 8th house (Viparita Raja Yoga potential) may transform enemies into allies and convert debts into gains. Hidden enemies may be neutralized. Health crises lead to deeper healing.",
        9: "The 6th lord in the 9th house may create tension between service obligations and dharmic pursuits. The native may face obstacles in higher education or conflicts with father or religious authorities.",
        10: "The 6th lord in the 10th house indicates a career in service, health, law, or competitive fields. The native overcomes professional obstacles through sustained effort and achieves through serving others.",
        11: "The 6th lord in the 11th house is favorable, converting obstacles into gains. The native profits from competition, service industries, or legal work. Enemies may inadvertently help fulfill desires.",
        12: "The 6th lord in the 12th house (Viparita Raja Yoga potential) can neutralize enemies, debts, and diseases through spiritual practice or foreign connections. Health expenses may lead to eventual relief.",
    },
    7: {
        1: "The 7th lord in the 1st house strongly connects marriage and partnerships to the personality. The native's identity is significantly shaped by their spouse, and partnerships define life direction.",
        2: "The 7th lord in the 2nd house connects marriage to family wealth. The spouse contributes to financial security, and family values influence partnership choices. Joint financial ventures are indicated.",
        3: "The 7th lord in the 3rd house connects marriage to communication, siblings, and personal effort. The spouse may be a communicator or involved in media. Partnership success requires personal initiative.",
        4: "The 7th lord in the 4th house connects marriage to home life and emotional happiness. The native finds deep emotional fulfillment through marriage, and the spouse supports domestic harmony.",
        5: "The 7th lord in the 5th house connects marriage to romance, children, and creativity. The native may meet their spouse through creative or educational settings. Children strengthen the marriage.",
        6: "The 7th lord in the 6th house may bring challenges to marriage through health issues, conflicts, or service obligations. The native may need to overcome obstacles in partnerships. Marital therapy may help.",
        7: "The 7th lord in the 7th house strengthens marriage and partnership prospects. The native is naturally oriented toward committed relationships and excels in partnership-based ventures.",
        8: "The 7th lord in the 8th house may indicate transformation through marriage, challenges to partnership longevity, or deep psychological bonding with the spouse. Partner's resources may be volatile.",
        9: "The 7th lord in the 9th house connects marriage to dharma and fortune. The spouse may be spiritual, philosophical, or foreign-born. Marriage brings good fortune and dharmic alignment.",
        10: "The 7th lord in the 10th house connects marriage to career. The spouse supports professional success, or the native finds partners through professional life. Public partnerships are prominent.",
        11: "The 7th lord in the 11th house connects marriage to gains and social fulfillment. The spouse helps fulfill desires, and partnerships generate income. Social networking through partnerships is strong.",
        12: "The 7th lord in the 12th house may indicate foreign spouse, separation in marriage, or expenses through partnerships. The spouse may come from a foreign background or the couple may live abroad.",
    },
    8: {
        1: "The 8th lord in the 1st house brings themes of transformation, longevity challenges, and deep research into the personality. The native may face health crises that reshape their identity. Resilience develops through adversity.",
        2: "The 8th lord in the 2nd house may challenge family wealth through sudden losses or debts. Inheritance may be a mixed blessing. Speech may carry intensity or reveal hidden knowledge.",
        3: "The 8th lord in the 3rd house connects transformation to communication and siblings. The native may write about hidden subjects or undergo changes through sibling relationships. Courage emerges from crises.",
        4: "The 8th lord in the 4th house may bring sudden changes to home life, property challenges, or mother's health concerns. The native's emotional peace may be disrupted by unexpected events.",
        5: "The 8th lord in the 5th house may challenge children, speculative ventures, or creative expression through sudden obstacles. Deep research intelligence and occult creativity develop through difficulty.",
        6: "The 8th lord in the 6th house can be favorable, neutralizing hidden enemies and converting crises into victories. Health challenges from the 8th may be overcome through the 6th house's fighting spirit.",
        7: "The 8th lord in the 7th house may challenge marriage through sudden events, partner's health issues, or deep transformation within relationships. Marriage undergoes profound evolutionary pressure.",
        8: "The 8th lord in the 8th house can extend longevity and deepen research ability, though life may be marked by intense transformative experiences. The native develops extraordinary resilience.",
        9: "The 8th lord in the 9th house may challenge dharma and fortune through crises, or transform spiritual understanding through deep life experiences. Relationship with father may involve karmic themes.",
        10: "The 8th lord in the 10th house may bring career upheavals, sudden changes in professional status, or a career in research, insurance, or transformation-related fields.",
        11: "The 8th lord in the 11th house may bring sudden gains or losses in income, or transform social networks through unexpected events. Research and investigation may generate income.",
        12: "The 8th lord in the 12th house connects longevity and transformation to spiritual liberation. The native may have a deep spiritual practice arising from life crises. Foreign hospitalization is possible.",
    },
    9: {
        1: "The 9th lord in the 1st house is very favorable, bringing dharmic fortune, father's blessings, and spiritual wisdom into the personality. The native is naturally fortunate and ethically inclined.",
        2: "The 9th lord in the 2nd house indicates wealth through dharma, father's resources, or higher education. The native's speech carries wisdom, and family values align with spiritual principles.",
        3: "The 9th lord in the 3rd house connects dharma to communication, courage, and personal effort. The native may teach, write about philosophy, or pursue fortune through courageous initiative.",
        4: "The 9th lord in the 4th house connects dharma to home, mother, and education. The native lives in a dharmic household with strong educational foundations. Mother may be spiritually inclined.",
        5: "The 9th lord in the 5th house is exceptionally favorable, connecting dharma to intelligence, children, and creativity. The native possesses wisdom, fortunate children, and powerful past-life merit.",
        6: "The 9th lord in the 6th house may indicate obstacles to dharma, conflicts with father, or legal challenges. Fortune may be delayed or require overcoming significant obstacles.",
        7: "The 9th lord in the 7th house connects dharma to marriage and partnerships. The native may find fortune through their spouse or travel abroad for dharmic purposes. Marriage is spiritually significant.",
        8: "The 9th lord in the 8th house may indicate difficulties with father, obstacles to fortune, or dharma found through transformative crisis. Spiritual understanding deepens through suffering.",
        9: "The 9th lord in the 9th house is highly favorable, greatly strengthening dharma, fortune, higher education, and relationship with father. The native is blessed with wisdom and ethical character.",
        10: "The 9th lord in the 10th house is exceptionally favorable (Dharma-Karma Adhipati Yoga), connecting fortune and ethics to career. The native achieves professional success through righteous conduct.",
        11: "The 9th lord in the 11th house connects dharma to gains and social fulfillment. The native achieves desires through ethical means and benefits from fortunate friendships and elder siblings.",
        12: "The 9th lord in the 12th house connects dharma to spiritual liberation and foreign lands. The native may find spiritual fulfillment abroad or through renunciation. Charitable expenditure brings merit.",
    },
    10: {
        1: "The 10th lord in the 1st house strongly connects career to personality, making the native naturally oriented toward professional achievement. Career success comes through personal effort and charisma.",
        2: "The 10th lord in the 2nd house connects career to wealth and family. The native earns substantially through their profession, and career choice may be influenced by family traditions.",
        3: "The 10th lord in the 3rd house indicates a career in communication, media, writing, or short-distance travel. Professional success comes through personal initiative and creative courage.",
        4: "The 10th lord in the 4th house indicates a career connected to property, education, or working from home. The native's professional life is rooted in domestic foundations and emotional satisfaction.",
        5: "The 10th lord in the 5th house connects career to creativity, education, children, or speculative ventures. The native may work in entertainment, education, or creative industries.",
        6: "The 10th lord in the 6th house indicates a career in service, health, law, or competitive fields. Professional life may involve overcoming obstacles and serving others in practical ways.",
        7: "The 10th lord in the 7th house connects career to partnerships and public dealings. The native achieves professional success through business partnerships, client relationships, or public-facing work.",
        8: "The 10th lord in the 8th house may indicate career upheavals, research-oriented work, or a profession dealing with transformation, death, insurance, or hidden resources.",
        9: "The 10th lord in the 9th house connects career to dharma, indicating work in education, law, religion, or philosophy. Professional success comes through ethical conduct and higher knowledge.",
        10: "The 10th lord in the 10th house strongly supports career success, status, and professional authority. The native is destined for professional prominence and may achieve high positions.",
        11: "The 10th lord in the 11th house connects career to gains, indicating that professional efforts translate effectively into income and fulfilled aspirations. Multiple revenue streams from career are possible.",
        12: "The 10th lord in the 12th house may indicate career in foreign lands, spiritual vocations, or institutions (hospitals, ashrams). Professional life may involve expenditure or behind-the-scenes work.",
    },
    11: {
        1: "The 11th lord in the 1st house brings gains, social networking, and fulfillment of desires directly into the personality. The native attracts opportunities and achieves aspirations through personal effort.",
        2: "The 11th lord in the 2nd house connects gains to wealth accumulation and family. Income sources are multiple and growing. Family connections support financial aspirations.",
        3: "The 11th lord in the 3rd house connects gains to communication, siblings, and personal effort. Income through writing, media, or sibling partnerships is indicated.",
        4: "The 11th lord in the 4th house connects gains to property, vehicles, and mother. Real estate income and domestic comfort from financial success are indicated.",
        5: "The 11th lord in the 5th house connects gains to intelligence, children, and creativity. Income from creative ventures, education, or speculative investment is indicated.",
        6: "The 11th lord in the 6th house may indicate gains that come with difficulty, through competition, service, or after overcoming obstacles. Legal or medical income serves aspirations.",
        7: "The 11th lord in the 7th house connects gains to marriage and partnerships. The spouse and business partners contribute to income growth and fulfillment of desires.",
        8: "The 11th lord in the 8th house may indicate fluctuating gains, income from hidden sources, or disruption to social networks. Research or inheritance may generate unexpected income.",
        9: "The 11th lord in the 9th house connects gains to dharma and fortune. Income from ethical endeavors, education, or international work supports aspirations. Father may facilitate gains.",
        10: "The 11th lord in the 10th house connects gains to career, indicating that professional success directly fulfills desires. Career-generated income is substantial and growing.",
        11: "The 11th lord in the 11th house strongly supports gains, social networks, and fulfillment of all desires. The native is naturally fortunate in friendships and income generation.",
        12: "The 11th lord in the 12th house may indicate gains spent on foreign travel, spiritual pursuits, or losses that offset income. Gains through foreign connections are possible but expenses may match.",
    },
    12: {
        1: "The 12th lord in the 1st house brings themes of expenditure, spirituality, and foreign connections into the personality. The native may live abroad or have a naturally spiritual, ascetic disposition.",
        2: "The 12th lord in the 2nd house may indicate financial drain, expenses exceeding income, or wealth spent on spiritual purposes. Family resources may be directed toward foreign or charitable causes.",
        3: "The 12th lord in the 3rd house connects losses or spiritual pursuits to communication and siblings. The native may write about spiritual topics or experience distance from siblings through foreign travel.",
        4: "The 12th lord in the 4th house may disrupt domestic peace through expenses, or connect home life to foreign or spiritual environments. The native may live in ashram-like settings.",
        5: "The 12th lord in the 5th house may indicate losses through speculation, expenditure on children, or creativity directed toward spiritual expression. Intelligence may be contemplative and introspective.",
        6: "The 12th lord in the 6th house (Viparita Raja Yoga potential) may convert losses into gains, especially through service, health, or competitive endeavors. Enemies' losses become the native's gain.",
        7: "The 12th lord in the 7th house may indicate foreign spouse, expenses through partnerships, or marriage influenced by spiritual or foreign themes. Bed pleasures are emphasized.",
        8: "The 12th lord in the 8th house (Viparita Raja Yoga potential) may transform losses into hidden gains, with research, occult, or insurance matters converting expenditure into benefit.",
        9: "The 12th lord in the 9th house connects spiritual liberation to dharma. The native may travel abroad for spiritual purposes or find that dharmic practice naturally leads toward detachment.",
        10: "The 12th lord in the 10th house may indicate a career in foreign lands, spiritual vocations, or institutional settings. Professional life involves expenditure or behind-the-scenes contribution.",
        11: "The 12th lord in the 11th house may indicate expenses through social networks or gains from foreign and spiritual sources. The balance between income and expenditure is a lifelong theme.",
        12: "The 12th lord in the 12th house strengthens all 12th house themes: foreign residence, spiritual practice, moksha, and charitable giving. The native is naturally inclined toward transcendence.",
    },
}

# Preserve backward compatibility for internal references.
_LORD_IN_HOUSE = LORD_IN_HOUSE


def get_house_themes(house: int) -> dict:
    """Return the signification dictionary for a house.

    Args:
        house: House number 1-12.

    Returns:
        Dictionary with keys: name, category, element, areas, body_parts,
        relations, positive, negative, karaka. Empty dict if house invalid.
    """
    return HOUSE_SIGNIFICATIONS.get(house, {})


def interpret_house_lord_placement(
    house: int,
    lord_planet: str,
    lord_house: int,
    asc_sign: int = 0,
) -> str:
    """Generate interpretation for a house lord placed in another house.

    This first checks the comprehensive LORD_IN_HOUSE dictionary for a
    hand-written interpretation. If none is found it falls back to a
    framework generator that produces sensible text based on the
    relationship between the source and target houses (kendra, trikona,
    dusthana, upachaya, etc.).

    Args:
        house: The house whose lord is being evaluated (1-12).
        lord_planet: The planet that rules the house.
        lord_house: The house where the lord planet is placed (1-12).
        asc_sign: Ascendant sign number 1-12 (used for sign-context).
            When provided, the interpretation includes the sign of the
            source and destination houses for richer context.

    Returns:
        Multi-sentence interpretation string.
    """
    if not (1 <= house <= 12) or not (1 <= lord_house <= 12):
        return ''

    # -- Specific hand-written text -----------------------------------------
    text = LORD_IN_HOUSE.get(house, {}).get(lord_house, '')
    if text:
        prefix = (
            f"The lord of the {_ordinal(house)} house ({lord_planet}) is "
            f"placed in the {_ordinal(lord_house)} house."
        )
        sign_context = _sign_context(house, lord_house, asc_sign)
        if sign_context:
            return f"{prefix} {sign_context} {text}"
        return f"{prefix} {text}"

    # -- Framework-based fallback -------------------------------------------
    return _generate_framework_interpretation(
        house, lord_planet, lord_house, asc_sign,
    )


def _sign_context(house: int, lord_house: int, asc_sign: int) -> str:
    """Build optional sign-context sentence when asc_sign is known.

    Returns an empty string when asc_sign is not provided (0).
    """
    if not asc_sign or not (1 <= asc_sign <= 12):
        return ''

    source_sign = ((asc_sign - 1 + house - 1) % 12) + 1
    target_sign = ((asc_sign - 1 + lord_house - 1) % 12) + 1

    source_name = SIGNS[source_sign] if 1 <= source_sign <= 12 else '?'
    target_name = SIGNS[target_sign] if 1 <= target_sign <= 12 else '?'
    source_lord = SIGN_LORDS.get(source_sign, '?')
    target_lord = SIGN_LORDS.get(target_sign, '?')

    return (
        f"For a {SIGNS[asc_sign]} ascendant, the {_ordinal(house)} house "
        f"is {source_name} (ruled by {source_lord}) and the lord is placed "
        f"in {target_name} (ruled by {target_lord})."
    )


def _generate_framework_interpretation(
    house: int,
    lord_planet: str,
    lord_house: int,
    asc_sign: int,
) -> str:
    """Produce interpretation text using the house-classification framework.

    This covers the key Vedic patterns:
    - Lord in own house = strong results
    - Lord in kendra (1, 4, 7, 10) = stable, supportive
    - Lord in trikona (1, 5, 9) = fortunate, dharmic support
    - Lord in dusthana (6, 8, 12) = challenges
    - Lord in 11th = gains related to the house
    - Lord in 3rd = effort needed
    """
    house_sig = HOUSE_SIGNIFICATIONS.get(house, {})
    lord_sig = HOUSE_SIGNIFICATIONS.get(lord_house, {})
    from_label = _HOUSE_SHORT_LABELS.get(house, f'house {house} matters')
    to_label = _HOUSE_SHORT_LABELS.get(lord_house, f'house {lord_house} matters')
    from_name = house_sig.get('name', f'House {house}')
    to_name = lord_sig.get('name', f'House {lord_house}')

    # Determine if lord is in its own house
    if house == lord_house:
        classification = 'own'
    else:
        classification = _classify_lord_placement(lord_house)

    framework = _PLACEMENT_FRAMEWORK.get(classification, '')

    # Build the opening sentence
    prefix = (
        f"The lord of the {_ordinal(house)} house ({from_name}, "
        f"signifying {from_label}) is {lord_planet}, placed in the "
        f"{_ordinal(lord_house)} house ({to_name}, signifying {to_label})."
    )

    sign_context = _sign_context(house, lord_house, asc_sign)

    parts = [prefix]
    if sign_context:
        parts.append(sign_context)
    parts.append(framework)

    # Add a closing sentence tying the two domains together.
    parts.append(
        f"The results depend on {lord_planet}'s dignity, aspects received, "
        f"and the overall chart configuration."
    )

    return ' '.join(parts)


def get_house_relationship(house_a: int, house_b: int) -> str:
    """Describe the relationship between two houses.

    Args:
        house_a: First house number 1-12.
        house_b: Second house number 1-12.

    Returns:
        String describing the angular relationship and its significance.
    """
    diff = ((house_b - house_a) % 12) or 12

    relationships = {
        1: "conjunction (same house) -- intensely merged energies",
        2: "2nd from -- financial and resource connection",
        3: "3rd from -- effort, courage, and communication link",
        4: "4th from -- emotional and domestic connection (square/kendra)",
        5: "5th from -- creative, intellectual, and dharmic connection (trine)",
        6: "6th from -- tension, competition, and service-related connection",
        7: "7th from -- opposition and partnership axis (kendra)",
        8: "8th from -- transformative, hidden, and crisis-related connection",
        9: "9th from -- dharmic, fortunate, and philosophical connection (trine)",
        10: "10th from -- career, action, and public connection (kendra)",
        11: "11th from -- gains, friendship, and aspiration connection",
        12: "12th from -- loss, expenditure, and spiritual connection",
    }

    return relationships.get(diff, f"{diff}th from -- general connection")


def _ordinal(n: int) -> str:
    """Return ordinal string for an integer."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"
