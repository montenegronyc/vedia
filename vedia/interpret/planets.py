"""Planet signification and interpretation text for Vedic astrology."""

from ..models import SIGNS, SIGN_LORDS


PLANET_SIGNIFICATIONS = {
    'Sun': {
        'nature': 'Malefic (krura)',
        'element': 'Fire',
        'gender': 'Male',
        'governs': 'Soul, father, authority, government, vitality, ego, leadership, health (bones/heart)',
        'strong': 'Confidence, leadership ability, strong willpower, good health, recognition from authority, government favor',
        'weak': 'Lack of confidence, ego issues, problems with father/authority, heart/bone ailments, lack of recognition',
        'friends': 'Moon, Mars, Jupiter',
        'enemies': 'Venus, Saturn',
    },
    'Moon': {
        'nature': 'Benefic (when waxing)',
        'element': 'Water',
        'gender': 'Female',
        'governs': 'Mind, emotions, mother, public, nurturing, fluids, fertility, mental peace',
        'strong': 'Emotional stability, good relationship with mother, public popularity, mental peace, fertile imagination',
        'weak': 'Emotional instability, depression, anxiety, problems with mother, fluid-related health issues',
        'friends': 'Sun, Mercury',
        'enemies': 'None',
    },
    'Mars': {
        'nature': 'Malefic',
        'element': 'Fire',
        'gender': 'Male',
        'governs': 'Energy, courage, siblings, property, surgery, military, sports, blood, muscles',
        'strong': 'Courage, physical strength, property gains, good relationship with siblings, technical skills',
        'weak': 'Anger, accidents, conflicts, blood disorders, property disputes, relationship with siblings strained',
        'friends': 'Sun, Moon, Jupiter',
        'enemies': 'Mercury',
    },
    'Mercury': {
        'nature': 'Benefic (when alone or with benefics)',
        'element': 'Earth',
        'gender': 'Neutral',
        'governs': 'Intelligence, communication, commerce, education, writing, skin, nervous system',
        'strong': 'Sharp intellect, communication skills, business acumen, good education, writing ability',
        'weak': 'Nervous disorders, skin problems, speech issues, poor decision making, scattered thinking',
        'friends': 'Sun, Venus',
        'enemies': 'Moon',
    },
    'Jupiter': {
        'nature': 'Benefic (greatest benefic)',
        'element': 'Ether/Space',
        'gender': 'Male',
        'governs': 'Wisdom, spirituality, children, wealth, dharma, teachers/gurus, liver, expansion',
        'strong': 'Wisdom, spiritual growth, good fortune, wealth, blessed with children, good teachers appear',
        'weak': 'Lack of faith, poor judgment, problems with children, liver issues, financial mismanagement',
        'friends': 'Sun, Moon, Mars',
        'enemies': 'Mercury, Venus',
    },
    'Venus': {
        'nature': 'Benefic',
        'element': 'Water',
        'gender': 'Female',
        'governs': 'Love, marriage, beauty, luxury, arts, vehicles, reproductive system, comfort',
        'strong': 'Happy marriage, artistic talent, material comforts, beauty, luxury, good vehicles',
        'weak': 'Relationship difficulties, lack of luxury, reproductive issues, overindulgence',
        'friends': 'Mercury, Saturn',
        'enemies': 'Sun, Moon',
    },
    'Saturn': {
        'nature': 'Malefic (greatest malefic)',
        'element': 'Air',
        'gender': 'Neutral/Eunuch',
        'governs': 'Discipline, karma, longevity, delays, servants, chronic illness, old age, detachment',
        'strong': 'Discipline, longevity, patience, success through hard work, organizational ability, spiritual detachment',
        'weak': 'Delays, chronic ailments, depression, loneliness, obstacles, karmic debts, joint problems',
        'friends': 'Mercury, Venus',
        'enemies': 'Sun, Moon, Mars',
    },
    'Rahu': {
        'nature': 'Malefic (shadow planet)',
        'element': 'Air',
        'gender': 'None (node)',
        'governs': 'Obsession, foreign things, technology, illusion, unconventional paths, sudden events',
        'strong': 'Worldly success, foreign connections, technological prowess, research ability, out-of-box thinking',
        'weak': 'Confusion, deception, addictions, phobias, sudden losses, scandals, misdiagnosis',
        'friends': 'Mercury, Venus, Saturn',
        'enemies': 'Sun, Moon, Mars',
    },
    'Ketu': {
        'nature': 'Malefic (shadow planet)',
        'element': 'Fire',
        'gender': 'None (node)',
        'governs': 'Spirituality, liberation, past lives, detachment, occult, isolation, sudden insights',
        'strong': 'Spiritual advancement, intuition, research ability, liberation, healing abilities, past life gifts',
        'weak': 'Confusion, aimlessness, isolation, mysterious ailments, lack of direction, self-doubt',
        'friends': 'Mars, Jupiter',
        'enemies': 'Mercury, Venus',
    },
}


# Detailed planet-in-sign interpretations (sign 1-12)
_PLANET_IN_SIGN = {
    'Sun': {
        1: "The Sun is exalted in Aries, bestowing powerful self-confidence, natural leadership, and a pioneering spirit. The native possesses strong willpower and a commanding presence that draws respect from others. Initiative and courage define the approach to life.",
        2: "The Sun in Taurus gives a steady, determined nature with a focus on material security and aesthetic values. The native seeks recognition through accumulated wealth and possessions. There can be a fixed, sometimes stubborn approach to self-expression.",
        3: "The Sun in Gemini produces a versatile, intellectually curious personality drawn to communication and learning. The native shines through writing, teaching, or commerce and may have diverse interests. Adaptability is strong, though focus may scatter.",
        4: "The Sun in Cancer creates tension between the ego and emotional sensitivity, as the Sun is in the sign of its friend the Moon. The native may seek authority through nurturing roles, with domestic matters and mother being important. There is patriotic feeling and attachment to homeland.",
        5: "The Sun in Leo occupies its own sign, producing maximum confidence, dignity, and a regal bearing. Leadership comes naturally, and the native commands attention and respect wherever they go. Creative self-expression, authority, and generosity define the personality.",
        6: "The Sun in Virgo gives an analytical, service-oriented nature with attention to detail and a desire for perfection. The native may shine in healing professions, organizational roles, or analytical fields. There is a tendency toward self-criticism despite genuine competence.",
        7: "The Sun is debilitated in Libra, indicating challenges with self-identity in the context of relationships and partnerships. The native may lose their sense of self in trying to please others or maintain harmony. Lessons around balancing personal authority with cooperation are central.",
        8: "The Sun in Scorpio produces an intensely private, research-oriented personality with deep psychological insight. The native may be drawn to hidden matters, investigation, and transformation. Willpower is formidable, but there can be power struggles.",
        9: "The Sun in Sagittarius gives a dharmic, principled nature oriented toward higher knowledge, philosophy, and spiritual teaching. The native may gain authority through wisdom and ethical conduct. There is natural optimism and a broad worldview.",
        10: "The Sun in Capricorn places the luminary in Saturn's sign, blending ambition with discipline. The native pursues authority and status through sustained effort and organizational skill. Career achievements define identity, though relationships with father may be complex.",
        11: "The Sun in Aquarius brings a humanitarian, reform-minded approach to self-expression. The native seeks recognition through social causes, innovation, and group leadership. There can be tension between ego desires and collective ideals.",
        12: "The Sun in Pisces gives a compassionate, spiritually inclined personality that finds fulfillment through selfless service and dissolution of ego. The native may shine in behind-the-scenes roles, spiritual pursuits, or charitable work. There is sensitivity and imagination.",
    },
    'Moon': {
        1: "The Moon in Aries creates an emotionally impulsive, action-oriented mind that needs independence and stimulation. Emotions are fiery and quickly expressed but also quickly resolved. The mother may have been a strong, independent figure.",
        2: "The Moon is exalted in Taurus, producing exceptional emotional stability, contentment, and a love of comfort and beauty. The mind is steady and sensual, finding peace through material security and natural pleasures. Relationship with mother is generally nurturing.",
        3: "The Moon in Gemini gives a quick, curious, and communicative mind that needs constant mental stimulation. Emotions are processed through intellect and verbalization. The native may be restless, with fluctuating moods tied to their social environment.",
        4: "The Moon in Cancer occupies its own sign, giving deep emotional sensitivity, strong maternal instincts, and powerful intuition. The native is deeply connected to home, family, and ancestral roots. Emotional memory is profound, and nurturing others comes naturally.",
        5: "The Moon in Leo produces a generous, dramatic emotional nature that craves recognition and appreciation. The mind is creative and expressive, finding joy through performance and romance. There is an inherent nobility and warmth in the emotional expression.",
        6: "The Moon in Virgo gives an analytical, service-oriented mind with a tendency toward worry and self-improvement. Emotions are processed through practical analysis, and the native may find emotional fulfillment through helping others or perfecting skills. Health awareness is heightened.",
        7: "The Moon in Libra creates a mind oriented toward partnerships, harmony, and aesthetic beauty. Emotional well-being is strongly tied to the quality of relationships. The native seeks balance and fairness, with a natural diplomatic instinct.",
        8: "The Moon is debilitated in Scorpio, indicating intense, transformative emotional experiences that test mental resilience. The mind probes deeply into hidden matters, with powerful intuition but also vulnerability to emotional upheaval. Psychological depth is remarkable.",
        9: "The Moon in Sagittarius gives an optimistic, philosophically inclined mind that finds emotional fulfillment through higher learning, travel, and spiritual exploration. The native is naturally expansive in outlook, with a generous and open-hearted emotional nature.",
        10: "The Moon in Capricorn produces a serious, ambitious emotional nature shaped by a sense of duty and responsibility. The mind is disciplined but can tend toward melancholy. Emotional satisfaction comes through career achievement and public recognition.",
        11: "The Moon in Aquarius gives a detached, humanitarian emotional nature oriented toward social ideals and group belonging. The mind is innovative and future-oriented, though personal emotional connections may feel secondary to larger causes.",
        12: "The Moon in Pisces creates a deeply imaginative, compassionate, and spiritually receptive mind. Emotional boundaries can be porous, leading to absorption of others' feelings. The native finds peace through spiritual practice, creative expression, and solitude.",
    },
    'Mars': {
        1: "Mars in Aries occupies its own sign, producing exceptional courage, physical energy, and competitive drive. The native is a natural warrior, direct in approach and fearless in action. Leadership through force of will is characteristic.",
        2: "Mars in Taurus gives tenacious determination in the pursuit of material resources, though it operates in the sign of its enemy Venus. The native may be possessive and stubborn, with strong desires for physical comfort. Earning power is driven by sustained effort.",
        3: "Mars in Gemini produces a mentally aggressive, sharp-witted communicator who excels in debate and quick thinking. Energy is directed toward communication, short travels, and interactions with siblings. There may be restlessness and scattered efforts.",
        4: "Mars is debilitated in Cancer, indicating suppressed anger and emotional volatility that disrupts domestic peace. The native may struggle with property matters and conflicts in the home. Courage is undermined by emotional sensitivity, though protective instincts are strong.",
        5: "Mars in Leo gives a dramatically courageous, creative, and authoritative energy expression. The native is bold in self-expression and fiercely protective of loved ones. There is a natural flair for leadership, sports, and competitive pursuits.",
        6: "Mars in Virgo produces a precise, methodical application of energy toward service, health, and problem-solving. The native excels in competitive situations through careful strategy rather than brute force. Technical and analytical skills are formidable.",
        7: "Mars in Libra places the warrior planet in the sign of diplomacy, creating tension between aggression and harmony in partnerships. The native may attract assertive partners or experience conflict in relationships. Balancing personal drive with cooperation is a lifelong theme.",
        8: "Mars in Scorpio occupies its own sign (moolatrikona), giving extraordinary willpower, investigative ability, and transformative energy. The native possesses deep reserves of strength and fearlessness in facing the unknown. Research, surgery, and occult sciences are favored.",
        9: "Mars in Sagittarius gives a crusading, righteous energy directed toward defending beliefs and pursuing higher knowledge. The native may be militant about their philosophical or religious convictions. Physical activity and adventure in foreign lands are favored.",
        10: "Mars is exalted in Capricorn, producing the highest expression of disciplined, strategic, and effective action. The native achieves career success through persistent effort, organizational skill, and practical courage. Professional accomplishments are substantial.",
        11: "Mars in Aquarius directs energy toward social causes, innovation, and group achievement. The native may be a revolutionary or reformer, with friends who are strong-willed. Gains come through technology, networking, and unconventional methods.",
        12: "Mars in Pisces gives energy that is directed inward toward spiritual pursuits, charity, or may dissipate through escapism. The native may channel martial energy through artistic expression or spiritual discipline. Foreign residence and behind-the-scenes activity are indicated.",
    },
    'Mercury': {
        1: "Mercury in Aries gives a quick, decisive, and pioneering intellect that favors direct communication. Thinking is fast but may lack thoroughness. The native excels in initiating ideas and entrepreneurial ventures.",
        2: "Mercury in Taurus produces a steady, practical intellect oriented toward financial calculation and material assessment. Communication style is deliberate and measured. The native has strong capacity for business and valuation.",
        3: "Mercury in Gemini occupies its own sign, giving exceptional versatility, communication skill, and intellectual agility. The native is a natural communicator, writer, or merchant with multiple interests. Mental activity is ceaseless and adaptable.",
        4: "Mercury in Cancer places the intellect in an emotional context, blending logic with intuition and memory. The native thinks with their feelings and communicates through storytelling. There is talent for understanding public sentiment.",
        5: "Mercury in Leo gives a confident, creative intellect suited to dramatic expression, teaching, and leadership communication. The native speaks with authority and flair. Intellectual pride may occasionally overshadow receptivity to others' ideas.",
        6: "Mercury in Virgo is exalted, producing the sharpest analytical mind with exceptional attention to detail and discrimination. The native excels in analysis, editing, healing diagnostics, and problem-solving. Communication is precise and methodical.",
        7: "Mercury in Libra gives a diplomatic, balanced intellect skilled in negotiation, mediation, and partnership communication. The native weighs all sides before deciding and communicates with charm. Legal and counseling abilities are enhanced.",
        8: "Mercury in Scorpio produces a penetrating, research-oriented intellect drawn to mysteries and hidden knowledge. The native thinks deeply and strategically, with an instinct for uncovering truth. Communication may be guarded but powerful.",
        9: "Mercury in Sagittarius gives a philosophical, broad-thinking intellect interested in higher learning, publishing, and cross-cultural exchange. The native communicates with enthusiasm and optimism. Detail orientation may be sacrificed for the bigger picture.",
        10: "Mercury in Capricorn produces a practical, structured, and ambitious intellect suited to organizational communication and management. The native thinks in terms of long-term strategy and career advancement. Communication is authoritative and efficient.",
        11: "Mercury in Aquarius gives an innovative, humanitarian intellect oriented toward progressive ideas and social networking. The native thinks in unconventional ways and communicates through technology and groups. Scientific and reform-oriented thinking is strong.",
        12: "Mercury is debilitated in Pisces, indicating an imaginative but sometimes confused intellect that blends logic with intuition. The native may struggle with practical details but excels in creative, spiritual, or artistic communication. Discrimination can be clouded.",
    },
    'Jupiter': {
        1: "Jupiter in Aries gives an optimistic, principled, and adventurous approach to wisdom and spiritual growth. The native is enthusiastic about learning and teaching, with a pioneering approach to philosophy. Confidence in one's beliefs is strong.",
        2: "Jupiter in Taurus gives a practical approach to wisdom, with an emphasis on material abundance as a foundation for dharmic life. The native accumulates wealth through ethical means and values family traditions. Speech is pleasant and truthful.",
        3: "Jupiter in Gemini produces a curious, communicative approach to wisdom that may spread across many subjects. The native is a natural teacher and writer, though philosophical depth may be sacrificed for breadth. Siblings may be fortunate.",
        4: "Jupiter is exalted in Cancer, producing the highest expression of wisdom combined with emotional intelligence and nurturing compassion. The native is blessed with inner peace, strong education, and a comfortable home. Mother is a source of wisdom.",
        5: "Jupiter in Leo gives a generous, dramatic expression of wisdom with a natural talent for teaching and guiding children. The native is confident in their beliefs and inspires others through creative and intellectual pursuits. Speculation may be fortunate.",
        6: "Jupiter in Virgo places expansive wisdom in an analytical, service-oriented framework. The native may find dharma through healing, service, and practical problem-solving. There can be tension between faith and critical analysis.",
        7: "Jupiter in Libra gives a balanced, partnership-oriented approach to wisdom and dharma. The native finds spiritual growth through relationships and values fairness as a guiding principle. Marriage may be to a wise or fortunate partner.",
        8: "Jupiter in Scorpio gives deep, transformative wisdom gained through crisis and investigation of hidden truths. The native may be drawn to occult studies, psychology, or research. Inheritance and sudden gains through others' resources are possible.",
        9: "Jupiter in Sagittarius occupies its own sign, producing the purest expression of wisdom, dharma, and spiritual teaching. The native is naturally philosophical, fortunate in higher education, and drawn to long journeys. Teaching and guiding others is their calling.",
        10: "Jupiter is debilitated in Capricorn, indicating challenges in expressing wisdom within rigid, materialistic structures. The native may prioritize worldly ambition over spiritual growth, or may face delays in receiving recognition for their knowledge. Patience develops wisdom.",
        11: "Jupiter in Aquarius gives a humanitarian, progressive approach to wisdom directed toward social improvement. The native gains through networks, elder siblings, and large organizations. Idealistic goals can be achieved through collective effort.",
        12: "Jupiter in Pisces occupies its own sign, giving profound spiritual wisdom, compassion, and eventual liberation. The native is naturally drawn to meditation, charity, and transcendental knowledge. Expenses may be for spiritual purposes or education.",
    },
    'Venus': {
        1: "Venus in Aries gives a passionate, impulsive approach to love and beauty that favors direct romantic pursuit. The native is attractive and charming but may rush into relationships. Artistic expression tends toward the bold and dynamic.",
        2: "Venus in Taurus occupies its own sign, producing refined aesthetic taste, love of luxury, and harmonious speech. The native values material comfort and beauty in all forms. Family life is generally pleasant, and accumulated wealth supports a comfortable lifestyle.",
        3: "Venus in Gemini gives a communicative, intellectually stimulating approach to love and art. The native is charming in speech and may have multiple romantic interests or creative pursuits. Artistic expression through writing or media is favored.",
        4: "Venus in Cancer gives a nurturing, emotionally deep approach to love with strong attachment to home and family. The native seeks comfort and emotional security in relationships. Domestic environment is beautifully maintained.",
        5: "Venus in Leo produces a dramatic, generous expression of love with a flair for creative romance and artistic performance. The native loves grandly and craves admiration. Entertainment, speculation, and children bring pleasure.",
        6: "Venus is debilitated in Virgo, indicating perfectionism and critical analysis that can undermine romantic happiness. The native may struggle to accept imperfection in partners or may attract challenging relationship situations. Service to others can be a path to love.",
        7: "Venus in Libra occupies its own sign, giving the most harmonious expression of partnership, beauty, and social grace. The native is naturally attractive, diplomatic, and skilled in relationships. Marriage is often fortunate and artistically fulfilling.",
        8: "Venus in Scorpio gives intense, transformative experiences in love with deep emotional and physical passion. The native may experience dramatic relationship changes and hidden romantic situations. Inheritance or partner's resources may provide luxury.",
        9: "Venus in Sagittarius gives an adventurous, philosophical approach to love that may favor foreign partners or long-distance relationships. The native finds beauty in wisdom and cultural diversity. Artistic expression has a philosophical or spiritual dimension.",
        10: "Venus in Capricorn produces a practical, status-conscious approach to love and beauty where relationships serve ambition. The native may attract older partners or find love through professional connections. Artistic achievement comes through disciplined effort.",
        11: "Venus in Aquarius gives an unconventional, friendship-oriented approach to love that values intellectual connection and social ideals. The native may have unusual relationship structures or find love through groups and networks. Gains through arts and women are indicated.",
        12: "Venus is exalted in Pisces, producing the most compassionate, spiritual, and transcendent expression of love. The native experiences love as a spiritual force and may find the deepest romantic fulfillment. Artistic expression is inspired and otherworldly.",
    },
    'Saturn': {
        1: "Saturn is debilitated in Aries, indicating frustration when discipline and patience are demanded in a sign that favors impulsive action. The native may struggle with self-imposed limitations or face early-life challenges that build eventual resilience. Lessons about patient leadership develop over time.",
        2: "Saturn in Taurus gives a cautious, persistent approach to wealth accumulation with an emphasis on financial security. The native may experience delays in building resources but achieves stability through sustained effort. Speech is measured and serious.",
        3: "Saturn in Gemini gives disciplined communication skills and methodical learning ability, well-suited to research and technical writing. The native may have a serious relationship with siblings or take on responsibilities for them. Mental effort is sustained and structured.",
        4: "Saturn in Cancer places the planet of discipline in the emotional sign of the Moon, creating tension between detachment and attachment. The native may experience a restricted or dutiful home environment. Relationship with mother may involve karmic lessons.",
        5: "Saturn in Leo creates tension between the need for creative self-expression and the constraints of discipline. The native may face challenges with children, romance, or creative pursuits that ultimately build character. Authority comes through earned respect.",
        6: "Saturn in Virgo produces exceptional discipline in service, health maintenance, and analytical work. The native excels in structured problem-solving and may work in health, law, or organizational management. Chronic health awareness promotes preventive care.",
        7: "Saturn is exalted in Libra, producing the highest expression of fair, just, and enduring partnerships. The native takes relationships seriously and may marry later but with lasting commitment. Legal matters and business partnerships benefit from Saturn's discipline.",
        8: "Saturn in Scorpio gives endurance through transformation and deep karmic experiences involving shared resources and mortality. The native may face significant challenges that ultimately lead to spiritual strengthening. Longevity is indicated despite periods of hardship.",
        9: "Saturn in Sagittarius gives a serious, disciplined approach to philosophy, religion, and higher learning. The native may be drawn to traditional wisdom systems and structured spiritual practice. Father may be austere or absent, prompting self-reliance in dharmic matters.",
        10: "Saturn in Capricorn occupies its own sign, producing exceptional career discipline, organizational ability, and ambition. The native achieves professional success through sustained effort, patience, and structural thinking. Authority positions come in the second half of life.",
        11: "Saturn in Aquarius occupies its own sign, giving disciplined pursuit of social ideals, strong networks, and steady gains. The native builds lasting friendships and achieves goals through patient, systematic effort within organizations and communities.",
        12: "Saturn in Pisces gives karmic lessons around spiritual detachment, isolation, and surrender. The native may experience periods of solitude or confinement that serve spiritual growth. Foreign lands or ashram-like settings may become significant in later life.",
    },
    'Rahu': {
        1: "Rahu in Aries amplifies desire for independence, leadership, and personal identity, often driving the native toward unconventional expressions of self. There is a powerful drive to be recognized as unique and pioneering. Worldly ambitions are pursued with obsessive intensity.",
        2: "Rahu in Taurus amplifies desire for material accumulation, sensual experience, and financial security through unconventional means. The native may acquire wealth through foreign connections or technology. Speech may be persuasive but potentially misleading.",
        3: "Rahu in Gemini (exalted per some traditions) amplifies communication abilities, technological skill, and media engagement. The native excels in unconventional communication, research, and networking. Relationships with siblings may be complex but ultimately beneficial.",
        4: "Rahu in Cancer creates intense desire for emotional security and domestic comfort, often through unconventional family arrangements. The native may have an unusual relationship with the motherland or seek property through foreign connections. Emotional restlessness is present.",
        5: "Rahu in Leo amplifies desire for creative recognition, dramatic expression, and power over others. The native may pursue fame through unconventional creative paths or speculative ventures. Relationships with children may involve karmic themes.",
        6: "Rahu in Virgo amplifies analytical abilities and drives the native toward service, healing, or competitive success through unconventional methods. The native may overcome enemies and obstacles through strategic, sometimes manipulative means. Health interests may include alternative medicine.",
        7: "Rahu in Libra creates intense desire for partnership and social recognition through relationships. The native may marry someone from a different cultural background or enter unconventional partnerships. Diplomatic skills are amplified but may mask ulterior motives.",
        8: "Rahu in Scorpio amplifies desire for hidden knowledge, transformation, and power over the mysteries of life and death. The native is drawn to research, occult studies, and investigation. Sudden events and inheritance through foreign or unconventional sources are indicated.",
        9: "Rahu in Sagittarius (debilitated per some traditions) creates tension between conventional dharma and unconventional spiritual or philosophical paths. The native may challenge religious orthodoxy or pursue wisdom through foreign traditions. Father's influence may be unusual.",
        10: "Rahu in Capricorn amplifies worldly ambition, career obsession, and desire for status through unconventional professional paths. The native may achieve sudden career elevation or work in technology, foreign trade, or media. Public image management is important.",
        11: "Rahu in Aquarius amplifies desire for social networking, gains through technology, and fulfillment of unconventional aspirations. The native may achieve extraordinary gains through innovation, foreign connections, or large organizations. Friend circles may be diverse and influential.",
        12: "Rahu in Pisces creates desire for spiritual experiences, foreign travel, and transcendence, though the path may involve confusion or illusion. The native may live abroad or be drawn to spiritual practices from foreign traditions. Expenses may be unexpected.",
    },
    'Ketu': {
        1: "Ketu in Aries gives a natural but detached approach to self-identity and initiative, as if the native has already mastered independence in past lives. There is spiritual disinterest in personal glory. The native may appear selfless or absent-minded about personal needs.",
        2: "Ketu in Taurus produces detachment from material accumulation and sensual comfort, indicating past-life mastery over resources. The native may be indifferent to wealth or have an unusual relationship with food and speech. Spiritual values override material ones.",
        3: "Ketu in Gemini (debilitated per some traditions) produces detachment from conventional communication and intellectual pursuits. The native may have intuitive rather than analytical intelligence. Relationship with siblings may be distant or karmic.",
        4: "Ketu in Cancer produces detachment from emotional attachment and domestic comfort. The native may feel disconnected from home or mother, having resolved these themes in past lives. There is natural spiritual maturity around emotional matters.",
        5: "Ketu in Leo gives detachment from creative ego-expression and personal recognition. The native may have past-life mastery in creative or leadership domains, now seeking subtler forms of expression. Relationship with children may involve spiritual dimensions.",
        6: "Ketu in Virgo gives natural ability to overcome obstacles and enemies through spiritual or intuitive means rather than analytical strategy. The native may have healing abilities or interest in alternative medicine. Service is performed without desire for recognition.",
        7: "Ketu in Libra produces detachment from partnerships and social conventions. The native may find conventional marriage unfulfilling and seek deeper spiritual connection. Past-life mastery of relationship dynamics gives natural but detached diplomatic skill.",
        8: "Ketu in Scorpio (own sign per some traditions) gives natural mastery over occult knowledge, transformation, and matters of life and death. The native possesses deep intuitive insight and spiritual fearlessness. Research and investigation yield breakthrough discoveries.",
        9: "Ketu in Sagittarius (exalted per some traditions) gives innate spiritual wisdom and past-life dharmic merit that manifests as natural philosophical understanding. The native may find formal religious education redundant, preferring direct spiritual experience.",
        10: "Ketu in Capricorn produces detachment from career ambition and worldly status. The native may appear uninterested in professional achievement despite possessing considerable organizational ability from past lives. Service-oriented work is preferred.",
        11: "Ketu in Aquarius gives detachment from social networking and material gains. The native may be indifferent to friendships or large group participation, preferring spiritual solitude. Past-life gains provide a natural sense of having enough.",
        12: "Ketu in Pisces gives natural spiritual attainment and past-life liberation tendencies. The native is innately drawn to meditation, moksha, and dissolution of worldly attachments. Foreign lands or isolated spiritual settings may be significant.",
    },
}


# Planet in house interpretations (house 1-12)
_PLANET_IN_HOUSE = {
    'Sun': {
        1: "The Sun in the 1st house gives a strong, confident personality with natural leadership ability and a commanding presence. The native is self-reliant, health-conscious, and drawn to positions of authority. Physical constitution is generally robust, with a regal bearing.",
        2: "The Sun in the 2nd house focuses identity on wealth, family lineage, and speech. The native may earn through government or authority-related work and speaks with confidence. Family relationships, particularly with the father, influence financial patterns.",
        3: "The Sun in the 3rd house gives courage, initiative, and a strong will expressed through communication and short journeys. The native may be an effective writer or speaker with leadership among siblings. Self-effort and personal courage bring success.",
        4: "The Sun in the 4th house indicates prominence through land, property, or domestic matters, though inner peace may be elusive due to ego-driven restlessness. Relationship with the mother may be complex, with the native seeking authority in the home. Government connection to property or vehicles is possible.",
        5: "The Sun in the 5th house is very favorable, giving creative intelligence, leadership in education, and strong connection to children. The native may work in government, politics, or speculative ventures with authority. Romance carries a quality of admiration and regal courtship.",
        6: "The Sun in the 6th house gives the ability to overcome enemies and obstacles through personal authority and willpower. The native may work in health, law, or government service. There is strength in competition, though health issues related to digestion or heart require attention.",
        7: "The Sun in the 7th house brings ego dynamics into partnerships and marriage, with the native potentially attracting authoritative or dominating partners. Business partnerships may involve government or high-status individuals. Learning to balance personal authority with cooperation is essential.",
        8: "The Sun in the 8th house indicates transformation of identity through crisis, and potential government or insurance-related resources. The native may research hidden matters or face challenges to their authority. Father's longevity or relationship may be a source of concern.",
        9: "The Sun in the 9th house is highly favorable for dharma, giving a righteous, principled nature with strong connection to father and spiritual teachers. The native may gain recognition through higher education, philosophy, or religious leadership. Government favor in foreign lands is possible.",
        10: "The Sun in the 10th house (digbala) gives maximum career authority, public recognition, and success in government or leadership roles. The native is destined for professional prominence and commands respect in their field. The father may be a significant influence on career direction.",
        11: "The Sun in the 11th house brings gains through government, authority figures, and leadership in social networks. The native achieves their aspirations through personal influence and may have powerful friends. Income from authoritative positions is steady.",
        12: "The Sun in the 12th house directs identity toward spiritual pursuits, foreign lands, or behind-the-scenes activity. The native may work in institutions or find purpose through selfless service. Father may be distant or connected to foreign places.",
    },
    'Moon': {
        1: "The Moon in the 1st house gives a nurturing, emotionally expressive personality with strong public appeal. The native is sensitive, intuitive, and deeply connected to their mother. Physical appearance tends toward softness, and moods fluctuate visibly.",
        2: "The Moon in the 2nd house brings emotional connection to family wealth, food, and speech patterns. The native's finances may fluctuate but involvement with the public brings earnings. Speech is gentle and nurturing, with a love of family traditions around food.",
        3: "The Moon in the 3rd house gives an emotionally driven communication style with creative writing ability and strong attachment to siblings. The native's courage fluctuates with mood, and short travels bring emotional satisfaction. Mental restlessness may be present.",
        4: "The Moon in the 4th house (digbala) is very favorable, giving deep emotional contentment, a beautiful home, and a close relationship with the mother. The native finds peace through domestic comforts and may have multiple residences. Public popularity is strong.",
        5: "The Moon in the 5th house gives a creative, emotionally rich intellect with a strong connection to children and romance. The native is imaginative and may be drawn to counseling, education, or entertainment. Emotional investment in speculative ventures fluctuates.",
        6: "The Moon in the 6th house may bring emotional disturbances through enemies, health issues, or service obligations. The native's mind may be drawn to worry and anxiety, particularly regarding health matters. Emotional healing through service to others is possible.",
        7: "The Moon in the 7th house brings emotional fulfillment through marriage and partnerships, with a strong need for companionship. The native attracts nurturing partners and may marry someone with Moon-like qualities. Public relations and business partnerships are emotionally satisfying.",
        8: "The Moon in the 8th house gives emotional intensity, psychic sensitivity, and a mind drawn to investigating mysteries. The native may experience emotional upheavals that drive psychological transformation. Mother's health or longevity may be a concern.",
        9: "The Moon in the 9th house gives a devotional, emotionally connected approach to spirituality and higher learning. The native finds peace through pilgrimage, philosophical study, and connection to teachers. Mother may be spiritually inclined.",
        10: "The Moon in the 10th house gives public prominence, popularity, and a career connected to nurturing, the public, or emotional support. The native's professional life may fluctuate but generally trends toward public-facing roles. Mother may influence career direction.",
        11: "The Moon in the 11th house brings emotional fulfillment through friendships, social networks, and achievement of desires. The native has many friends, particularly women, and gains through public dealings. Emotional satisfaction comes from community involvement.",
        12: "The Moon in the 12th house gives a contemplative, spiritually inclined mind that needs periodic solitude for emotional renewal. The native may live abroad or find peace in ashrams and isolated settings. Sleep may be light, with vivid dreams and psychic impressions.",
    },
    'Mars': {
        1: "Mars in the 1st house gives a strong, athletic, courageous personality with a competitive spirit and physical vitality. The native is direct, assertive, and may bear scars or marks on the face or head. Initiative and independence define the approach to life.",
        2: "Mars in the 2nd house can create harsh speech, financial volatility through impulsive spending, and conflicts within the family. The native may earn through engineering, military, surgery, or real estate. Dietary habits may be spicy or irregular.",
        3: "Mars in the 3rd house is very favorable, giving exceptional courage, strong will, and an adventurous spirit in communication and short travels. The native has a powerful relationship with siblings and excels in competitive ventures. Physical courage is remarkable.",
        4: "Mars in the 4th house may disturb domestic peace through conflicts, property disputes, or an aggressive home environment. The native may own land or vehicles but experience turbulence in their use. Relationship with mother may involve friction.",
        5: "Mars in the 5th house gives competitive intelligence, athletic children, and a bold approach to romance and speculation. The native may be drawn to sports coaching, competitive education, or risky investments. Creative expression has a fiery, dynamic quality.",
        6: "Mars in the 6th house is very favorable, giving the ability to decisively defeat enemies, overcome obstacles, and excel in competitive situations. The native may work in military, law enforcement, surgery, or competitive sports. Health is generally strong through active lifestyle.",
        7: "Mars in the 7th house (Kuja Dosha) brings intense passion and potential conflict into marriages and partnerships. The native attracts assertive partners and relationships may be volatile but passionate. Business partnerships require careful conflict management.",
        8: "Mars in the 8th house gives research ability, surgical skill, and resilience through crisis, though accidents and sudden events may occur. The native faces danger with courage and may work in emergency services, investigation, or transformative healing. Longevity is generally good despite risks.",
        9: "Mars in the 9th house gives a militant, action-oriented approach to beliefs and may indicate conflicts with father or religious institutions. The native may travel for competitive purposes or pursue dharma through martial discipline. Younger siblings to teachers may be significant.",
        10: "Mars in the 10th house gives an ambitious, action-oriented career with success in engineering, military, surgery, sports, or real estate. The native is a natural leader in professional settings and achieves through decisive action. Career involves physical effort and competition.",
        11: "Mars in the 11th house is very favorable, giving fulfillment of ambitions through courage and competition. The native gains through siblings, engineering, property, or military connections. Friendships may be with athletic or assertive individuals.",
        12: "Mars in the 12th house directs energy toward foreign lands, spiritual practice, or may dissipate through confinement and losses. The native may experience expenses through litigation, accidents, or hospitalization. Channeling energy into meditation or charitable action is beneficial.",
    },
    'Mercury': {
        1: "Mercury in the 1st house gives a youthful, communicative, and intellectually curious personality. The native is a natural communicator, quick-witted and adaptable, with an appearance that remains youthful. Multiple interests and a talent for commerce or writing define the character.",
        2: "Mercury in the 2nd house gives eloquent, intelligent speech and a mind oriented toward financial calculation and commerce. The native may earn through writing, teaching, accounting, or trade. Family education and intellectual heritage are valued.",
        3: "Mercury in the 3rd house is very favorable, giving exceptional communication skills, writing talent, and strong relationships with siblings. The native excels in media, publishing, short travel, and all forms of information exchange. Mental agility is remarkable.",
        4: "Mercury in the 4th house gives a home-based intellectual life with interest in education, real estate analysis, and domestic technology. The native's mind finds peace through study and may have an extensive home library. Educational achievements bring domestic happiness.",
        5: "Mercury in the 5th house gives creative intelligence, skill in speculation and investment analysis, and a communicative approach to romance. The native may have intellectually gifted children and excels in education, writing for entertainment, or advisory roles.",
        6: "Mercury in the 6th house gives analytical problem-solving ability, skill in health diagnostics, and a methodical approach to overcoming obstacles. The native may work in accounting, editing, health analysis, or legal documentation. Nervous health requires attention.",
        7: "Mercury in the 7th house gives a communicative, intellectually stimulating approach to partnerships with a preference for mentally compatible partners. The native excels in business partnerships, counseling, and negotiation. Marriage may involve a younger or intellectual partner.",
        8: "Mercury in the 8th house gives a research-oriented mind drawn to investigation, occult study, and hidden knowledge. The native may work in insurance, taxation, forensic analysis, or psychological research. Communication about taboo subjects comes naturally.",
        9: "Mercury in the 9th house gives a scholarly, philosophical intellect with love of higher learning, publishing, and cross-cultural communication. The native may excel in academia, translation, or religious scholarship. Father may be an intellectual influence.",
        10: "Mercury in the 10th house gives a career in communication, commerce, writing, or intellectual pursuits. The native achieves professional success through mental agility, networking, and adaptability. Multiple career interests or simultaneous professional roles are common.",
        11: "Mercury in the 11th house brings gains through intelligence, communication networks, and commercial ventures. The native has many intellectually stimulating friendships and achieves aspirations through networking and information exchange. Income from multiple sources is likely.",
        12: "Mercury in the 12th house directs intelligence toward spiritual study, foreign communication, or behind-the-scenes analytical work. The native may write in solitude, study foreign languages, or apply intellect to meditation practices. Discrimination about expenses may be lacking.",
    },
    'Jupiter': {
        1: "Jupiter in the 1st house gives a wise, optimistic, and generous personality with good fortune, physical well-being, and a natural inclination toward dharma. The native appears blessed, with a large or dignified physical frame. Wisdom and ethical conduct define the character.",
        2: "Jupiter in the 2nd house is highly favorable for wealth, giving eloquent and truthful speech, family prosperity, and accumulation through wisdom. The native may earn through teaching, counseling, finance, or religious activities. Food and family life are abundant.",
        3: "Jupiter in the 3rd house may not fully express its beneficence, as the great benefic in the house of effort can indicate over-reliance on luck over personal initiative. The native may have a philosophical relationship with siblings and communicate with wisdom. Courage comes through faith rather than aggression.",
        4: "Jupiter in the 4th house is very favorable, giving a blessed home life, good education, comfortable vehicles, and a wise mother. The native finds peace through learning and may own multiple properties. Domestic life is expansive and dharmic.",
        5: "Jupiter in the 5th house is exceptionally favorable, giving creative wisdom, blessed children, and good fortune in education and speculation. The native is a natural teacher and counselor with strong poorva punya (past-life merit). Romance is dignified and fortunate.",
        6: "Jupiter in the 6th house gives the ability to overcome obstacles through wisdom and ethical conduct, though it may also expand health issues or debts. The native may work in legal, health, or service fields. Enemies are defeated through righteous action.",
        7: "Jupiter in the 7th house gives a fortunate, dharmic marriage and beneficial partnerships. The native attracts wise, generous partners and may marry someone from a noble or learned family. Business partnerships are generally prosperous and ethical.",
        8: "Jupiter in the 8th house gives longevity, protection during crises, and wealth through inheritance or partner's resources. The native has deep spiritual insight gained through transformative experiences. Interest in metaphysics and life after death is profound.",
        9: "Jupiter in the 9th house (own house for Sagittarius) is supremely favorable, giving the highest dharmic fortune, wisdom, spiritual grace, and connection to great teachers. The native may be a teacher, priest, judge, or philosopher. Father is generally a positive influence.",
        10: "Jupiter in the 10th house gives a prestigious, ethical career with recognition for wisdom and integrity. The native may work in law, education, religion, finance, or advisory roles. Professional success comes through ethical conduct and good reputation.",
        11: "Jupiter in the 11th house is very favorable, giving fulfillment of desires, substantial gains, and fortunate friendships. The native achieves aspirations through wisdom and ethical networking. Income is generous, especially from Jupiter-related fields.",
        12: "Jupiter in the 12th house gives spiritual wisdom, eventual liberation, and expenditure for dharmic purposes. The native may travel to foreign lands for spiritual growth or live near temples and places of learning. Charitable giving is natural and abundant.",
    },
    'Venus': {
        1: "Venus in the 1st house gives an attractive, charming, and artistic personality with a love of beauty and social grace. The native has a pleasant appearance and draws people naturally. Comfort, luxury, and harmonious relationships are life priorities.",
        2: "Venus in the 2nd house is favorable for wealth through beauty, arts, or women-related businesses. The native has a sweet, melodious voice and appreciates fine food and luxurious family life. Financial accumulation through artistic or relationship-oriented work is indicated.",
        3: "Venus in the 3rd house gives artistic communication ability, pleasant relationships with siblings, and enjoyment of short travels. The native may express creativity through writing, media, or performing arts. Courage is expressed through charm rather than force.",
        4: "Venus in the 4th house gives a beautiful, comfortable home, luxury vehicles, and a loving domestic environment. The native finds happiness through home decoration, gardening, and creating harmonious spaces. Relationship with mother is generally affectionate.",
        5: "Venus in the 5th house gives romantic happiness, creative artistic talent, and pleasure through children and entertainment. The native is drawn to music, drama, and romantic pursuits. Speculation in arts or luxury goods may be fortunate.",
        6: "Venus in the 6th house may challenge relationships through service obligations, health issues, or conflicts. The native may work in beauty, fashion, or entertainment-related service industries. Overcoming relationship obstacles requires practical adjustment.",
        7: "Venus in the 7th house (digbala) is exceptionally favorable for marriage, giving a beautiful, loving partner and harmonious partnerships. The native excels in all forms of partnership and has strong social appeal. Business ventures involving beauty or luxury prosper.",
        8: "Venus in the 8th house gives intensity in romantic life, potential inheritance of luxury, and transformation through relationships. The native may experience deep, passionate connections that fundamentally change them. Secret relationships or hidden artistic talents are possible.",
        9: "Venus in the 9th house gives a love of philosophy, art, and beauty expressed through spiritual or cultural pursuits. The native may travel for pleasure, study arts abroad, or find romance through religious or educational settings. Father may be artistic or wealthy.",
        10: "Venus in the 10th house gives a career in arts, beauty, luxury, entertainment, or diplomacy. The native achieves professional success through charm, aesthetic sensibility, and relationship skills. Public image is polished and attractive.",
        11: "Venus in the 11th house brings gains through arts, women, luxury goods, and social networking. The native has many pleasant friendships and achieves desires related to comfort and beauty. Income from artistic or entertainment ventures is favorable.",
        12: "Venus in the 12th house gives pleasure through foreign travels, spiritual retreat, and bedroom comforts. The native may find the deepest romantic satisfaction in privacy or distant lands. Expenditure on luxury and pleasure may be significant.",
    },
    'Saturn': {
        1: "Saturn in the 1st house gives a serious, disciplined, and enduring personality that matures with age. The native may face early-life challenges that build character and resilience. Physical constitution improves after the first Saturn return, and longevity is indicated.",
        2: "Saturn in the 2nd house may restrict early wealth and create a serious, sometimes harsh speaking style. The native accumulates resources slowly through disciplined effort and frugality. Family responsibilities and financial obligations are taken seriously.",
        3: "Saturn in the 3rd house gives disciplined communication, methodical effort, and a serious relationship with siblings who may be older or more responsible. The native achieves through sustained effort rather than quick action. Writing and research benefit from patience.",
        4: "Saturn in the 4th house may restrict domestic happiness, delay property acquisition, or create a sense of duty around home and mother. The native may live in older structures or have a spartan home. Emotional contentment develops later in life.",
        5: "Saturn in the 5th house may delay children, restrict romantic expression, or bring a serious approach to creative work. The native's intelligence is deep but slow-developing. Speculation should be avoided; disciplined creative practice yields results over time.",
        6: "Saturn in the 6th house is favorable, giving the ability to methodically overcome enemies and obstacles through patience and strategic effort. The native excels in law, administration, or disciplined service. Chronic health awareness promotes preventive care.",
        7: "Saturn in the 7th house may delay marriage or bring an older, serious, and responsible partner. The native takes partnerships very seriously and may experience relationship challenges that build wisdom. Long-term commitment is valued over romantic excitement.",
        8: "Saturn in the 8th house gives longevity and the ability to endure severe hardships, though chronic health issues may develop. The native may work in insurance, research, or industries dealing with death and transformation. Inheritance may be delayed or involve obligations.",
        9: "Saturn in the 9th house gives a structured, traditional approach to religion and philosophy with possible delays in higher education. The native may be drawn to ascetic or disciplined spiritual practices. Relationship with father may involve duty or distance.",
        10: "Saturn in the 10th house (digbala) gives maximum career authority through discipline, patience, and organizational ability. The native rises slowly but surely to positions of significant responsibility. Professional success comes in the second half of life.",
        11: "Saturn in the 11th house is favorable, giving steady, reliable gains and enduring friendships built over time. The native achieves long-term aspirations through patient effort and may benefit from older friends or established organizations. Income stabilizes with age.",
        12: "Saturn in the 12th house may bring isolation, foreign residence, or spiritual practice through renunciation and detachment. The native may face institutional confinement or choose monastic life. Expenses are controlled, and spiritual wisdom develops through solitude.",
    },
    'Rahu': {
        1: "Rahu in the 1st house gives an unconventional, ambitious personality with a powerful drive for worldly achievement and unique self-expression. The native may appear mysterious or exotic to others and is drawn to breaking social conventions. Foreign connections and technology play important roles.",
        2: "Rahu in the 2nd house amplifies desire for wealth accumulation through unconventional or foreign means. The native's speech may be persuasive but potentially deceptive, and dietary habits may be unusual. Family dynamics may involve foreign or cross-cultural elements.",
        3: "Rahu in the 3rd house gives exceptional courage, communication prowess, and success through media, technology, or unconventional means. The native is bold in self-expression and may have a powerful online or media presence. Relationships with siblings may be unusual.",
        4: "Rahu in the 4th house creates desire for domestic comfort through unconventional means, with potential upheaval in home life. The native may own property in foreign locations or have an unusual relationship with the mother. Mental peace may require deliberate cultivation.",
        5: "Rahu in the 5th house amplifies creative and speculative desires with a tendency toward unconventional romance and innovative artistic expression. The native may have children under unusual circumstances or be involved in technology-based creative work. Intelligence is unorthodox.",
        6: "Rahu in the 6th house is favorable, giving the ability to overcome enemies and obstacles through unconventional, strategic, or technological means. The native may work in foreign health services, technology-based problem-solving, or competitive environments. Diseases may be unusual or misdiagnosed.",
        7: "Rahu in the 7th house creates desire for unconventional partnerships, possibly with someone from a foreign culture or different social background. The native may experience multiple significant relationships or a marriage that defies social norms. Business partnerships may involve foreign entities.",
        8: "Rahu in the 8th house gives intense fascination with hidden knowledge, transformation, and the occult. The native may experience sudden, dramatic life changes and gain through unconventional research or inheritance. Mysterious health issues and foreign resources are indicated.",
        9: "Rahu in the 9th house challenges conventional religious and philosophical beliefs, driving the native toward unconventional spiritual paths. The native may study foreign philosophies or have a complex relationship with their father. Higher education may involve unorthodox subjects.",
        10: "Rahu in the 10th house gives powerful worldly ambition and potential for sudden career elevation through unconventional means. The native may achieve fame or notoriety in their profession and work with foreign organizations or technology. Public image management is important.",
        11: "Rahu in the 11th house is very favorable, amplifying gains through technology, foreign connections, and large networks. The native achieves ambitious desires through unconventional means and may have influential friends from diverse backgrounds. Income from innovation is substantial.",
        12: "Rahu in the 12th house drives desire for foreign residence, spiritual experiences, or may indicate losses through deception and confusion. The native may travel extensively abroad or be drawn to foreign spiritual traditions. Expenditure may be difficult to control.",
    },
    'Ketu': {
        1: "Ketu in the 1st house gives a spiritually inclined, detached personality that may appear mysterious or otherworldly to others. The native has past-life spiritual attainments that manifest as natural intuition and disinterest in worldly self-promotion. Health may involve mysterious symptoms.",
        2: "Ketu in the 2nd house produces detachment from family wealth and conventional speech patterns. The native may have an unusual or sparse speaking style and show disinterest in material accumulation. Past-life resources provide a subtle sense of sufficiency.",
        3: "Ketu in the 3rd house gives introverted communication style, detachment from siblings, and courage that comes from spiritual fearlessness rather than physical aggression. The native may be a naturally gifted but understated communicator. Short travels may have spiritual purposes.",
        4: "Ketu in the 4th house produces detachment from domestic comforts and conventional home life. The native may feel restless at home or live in unusual domestic arrangements. Past-life resolution of emotional issues gives a naturally detached inner peace.",
        5: "Ketu in the 5th house gives intuitive intelligence, spiritual creativity, and a detached approach to romance and children. The native may have past-life creative mastery that manifests as natural talent without ego attachment. Speculation is generally not favored.",
        6: "Ketu in the 6th house is favorable, giving the ability to overcome obstacles through spiritual means and intuition. The native may have natural healing abilities and show detachment from enemies and competitors. Health issues may resolve through alternative or spiritual healing.",
        7: "Ketu in the 7th house produces detachment from conventional partnerships and may bring a spiritually inclined partner. The native may find worldly relationship expectations unfulfilling, seeking deeper spiritual connection. Past-life relationship karma requires resolution.",
        8: "Ketu in the 8th house gives natural insight into occult matters, spiritual transformation, and the mysteries of existence. The native may have psychic abilities and deep meditative capacity. Sudden spiritual awakenings and past-life knowledge emerge naturally.",
        9: "Ketu in the 9th house gives innate spiritual wisdom and past-life dharmic merit without need for formal religious instruction. The native may find organized religion stifling and prefer direct spiritual experience. Father may be spiritually significant or absent.",
        10: "Ketu in the 10th house produces detachment from career ambition and worldly status. The native may struggle to find professional direction or choose a spiritual vocation. Past-life professional accomplishments allow freedom from career anxiety.",
        11: "Ketu in the 11th house gives detachment from gains, friendships, and fulfillment of worldly desires. The native may find social networking unfulfilling and prefer spiritual community. Past-life abundance creates present contentment without striving.",
        12: "Ketu in the 12th house is very favorable for spiritual liberation, giving natural meditative ability and past-life moksha tendencies. The native is drawn to ashrams, monasteries, and spiritual isolation. Final liberation is a genuine possibility in this lifetime.",
    },
}


# Dignity interpretation text snippets
_DIGNITY_TEXT = {
    'exalted': "is exalted, operating at peak strength and bestowing its finest qualities with ease and abundance",
    'moolatrikona': "is in moolatrikona, functioning with great strength and producing highly favorable results in its domain",
    'own': "is in its own sign, comfortable and strong, able to deliver its natural significations with reliability and authority",
    'friendly': "is in a friendly sign, reasonably comfortable and able to produce good results with some external support",
    'neutral': "is in a neutral sign, producing mixed results depending on other chart factors and planetary aspects",
    'enemy': "is in an enemy sign, facing obstacles in expressing its natural qualities and requiring extra effort to produce results",
    'debilitated': "is debilitated, struggling to express its natural significations and requiring remedial measures or cancellation yogas to function well",
}


def interpret_planet_in_sign(planet: str, sign: int, dignity: str) -> str:
    """Generate interpretation for a planet in a sign with its dignity.

    Args:
        planet: Planet name (e.g. 'Sun', 'Moon').
        sign: Sign number 1-12.
        dignity: Dignity string from PlanetPosition.dignity.

    Returns:
        Multi-sentence interpretation string.
    """
    sign_name = SIGNS[sign] if 1 <= sign <= 12 else 'Unknown'
    sign_lord = SIGN_LORDS.get(sign, 'Unknown')

    # Base sign interpretation
    sign_text = _PLANET_IN_SIGN.get(planet, {}).get(sign, '')
    if not sign_text:
        sign_text = (
            f"{planet} in {sign_name} expresses its significations through "
            f"the lens of {sign_name}'s qualities, ruled by {sign_lord}."
        )

    # Dignity overlay
    dignity_key = dignity.lower() if dignity else 'neutral'
    dignity_desc = _DIGNITY_TEXT.get(dignity_key, _DIGNITY_TEXT['neutral'])

    result = f"{planet} in {sign_name} {dignity_desc}. {sign_text}"
    return result


def interpret_planet_in_house(planet: str, house: int) -> str:
    """Generate interpretation for a planet in a house.

    Args:
        planet: Planet name.
        house: House number 1-12.

    Returns:
        Multi-sentence interpretation string.
    """
    text = _PLANET_IN_HOUSE.get(planet, {}).get(house, '')
    if not text:
        sig = PLANET_SIGNIFICATIONS.get(planet, {})
        governs = sig.get('governs', 'its natural significations')
        text = (
            f"{planet} in the {_ordinal(house)} house brings the themes of "
            f"{governs} into the domain of house {house}. The results depend "
            f"on the planet's dignity, aspects, and the overall chart context."
        )
    return text


def get_planet_summary(planet: str) -> dict:
    """Return the full signification dictionary for a planet.

    Args:
        planet: Planet name.

    Returns:
        Dictionary with nature, element, gender, governs, strong, weak,
        friends, enemies keys, or empty dict if planet not found.
    """
    return PLANET_SIGNIFICATIONS.get(planet, {})


def _ordinal(n: int) -> str:
    """Return ordinal string for an integer (1st, 2nd, etc.)."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"
