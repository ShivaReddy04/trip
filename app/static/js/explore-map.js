// Indian Tourism Explorer - Vanilla JS with state management
(function() {
    'use strict';

    // ── Place Data ──────────────────────────────────────────────────
    const PLACES = [
        {
            id: 1,
            name: 'Taj Mahal',
            location: 'Agra, Uttar Pradesh',
            category: 'Heritage',
            description: 'An ivory-white marble mausoleum and UNESCO World Heritage Site, widely regarded as the jewel of Muslim art in India.',
            hero: 'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800&q=80',
                'https://images.unsplash.com/photo-1585135497273-1a86b09fe70e?w=800&q=80',
                'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
                'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&q=80',
            ],
            history: 'The Taj Mahal was commissioned in 1632 by the Mughal emperor Shah Jahan to house the tomb of his favourite wife, Mumtaz Mahal. It was built over a period of 22 years by over 20,000 artisans under the guidance of a board of architects led by Ustad Ahmad Lahauri. The monument is a masterpiece of Mughal architecture, combining elements of Islamic, Persian, Ottoman Turkish and Indian architectural styles. The complex covers 17 hectares and includes a mosque, guest house, and formal gardens bounded on three sides by a crenellated wall.',
            facts: { bestTime: 'October – March', entryFee: '₹50 (Indians) / ₹1,100 (Foreigners)', timings: 'Sunrise to Sunset (Closed on Fridays)', unesco: true, builtIn: '1632–1653' },
            highlights: ['Sunrise view from Mehtab Bagh', 'Moonlight viewing on full moon nights', 'Intricate pietra dura inlay work', 'The reflecting pool & charbagh garden', 'The mosque and guest house (Jawab)'],
            howToReach: { air: 'Agra Airport (Kheria) – 12 km away', rail: 'Agra Cantt Railway Station – 5 km away', road: 'Well connected via Yamuna Expressway from Delhi (3-4 hrs)' }
        },
        {
            id: 2,
            name: 'Varanasi Ghats',
            location: 'Varanasi, Uttar Pradesh',
            category: 'Heritage',
            description: 'The spiritual capital of India, where ancient ghats along the Ganges host centuries-old rituals at dawn and dusk.',
            hero: 'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800&q=80',
                'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800&q=80',
                'https://images.unsplash.com/photo-1571536802086-8b4acf079e1c?w=800&q=80',
                'https://images.unsplash.com/photo-1627894483216-2138af692e32?w=800&q=80',
            ],
            history: 'Varanasi, also known as Kashi and Banaras, is one of the oldest continuously inhabited cities in the world, with a history dating back over 3,000 years. It is considered the holiest of seven sacred cities in Hinduism and Jainism. The city is known for its ghats — a series of 88 stone steps leading down to the river Ganges, where pilgrims perform ritual bathing. The Ganga Aarti ceremony at Dashashwamedh Ghat is one of the most spectacular spiritual rituals in India, performed every evening with fire, incense, and ancient chants.',
            facts: { bestTime: 'October – March', entryFee: 'Free (Ghats are public)', timings: 'Ganga Aarti: 6:30 PM daily', unesco: false, builtIn: 'Ancient (3000+ years)' },
            highlights: ['Ganga Aarti at Dashashwamedh Ghat', 'Sunrise boat ride on the Ganges', 'Visit Kashi Vishwanath Temple', 'Explore the narrow old-city lanes', 'Silk weaving workshops in Banaras'],
            howToReach: { air: 'Lal Bahadur Shastri Airport – 25 km', rail: 'Varanasi Junction – centrally located', road: 'Connected by NH-2 from Delhi, Kolkata & Lucknow' }
        },
        {
            id: 3,
            name: 'Kerala Backwaters',
            location: 'Alleppey, Kerala',
            category: 'Nature',
            description: 'A network of tranquil lagoons, canals and lakes stretching along the Malabar Coast — best explored on a traditional houseboat.',
            hero: 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80',
                'https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&q=80',
                'https://images.unsplash.com/photo-1609340381668-1668a2e5e5e5?w=800&q=80',
                'https://images.unsplash.com/photo-1506461883276-594a12b11cf3?w=800&q=80',
            ],
            history: 'The Kerala backwaters are a chain of brackish lagoons and lakes lying parallel to the Arabian Sea coast of Kerala state in southern India. The network includes five large lakes linked by canals, both man-made and natural, fed by 38 rivers, and extends virtually half the length of Kerala state. The backwaters were formed by the action of waves and shore currents creating low barrier islands across the mouths of the many rivers flowing down from the Western Ghats. The houseboats (kettuvallam) were traditionally used for rice transport and have been converted into floating hotels.',
            facts: { bestTime: 'September – March', entryFee: 'Houseboat rentals from ₹6,000/day', timings: 'All day (overnight stays available)', unesco: false, builtIn: 'Natural Formation' },
            highlights: ['Overnight houseboat cruise', 'Toddy shop & Kerala cuisine tasting', 'Village walks through paddy fields', 'Canoe rides through narrow canals', 'Bird watching at Kumarakom sanctuary'],
            howToReach: { air: 'Cochin International Airport – 85 km', rail: 'Alleppey Railway Station – in town', road: 'NH-66 connects Alleppey to Kochi (1.5 hrs) and Trivandrum (3.5 hrs)' }
        },
        {
            id: 4,
            name: 'Goa Beaches',
            location: 'North & South Goa',
            category: 'Beaches',
            description: 'India\'s beach paradise with golden sands, Portuguese colonial architecture, and a vibrant nightlife scene.',
            hero: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&q=80',
                'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
                'https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=800&q=80',
                'https://images.unsplash.com/photo-1614082242765-7c98ca0f3df3?w=800&q=80',
            ],
            history: 'Goa was a Portuguese territory for over 450 years, from 1510 until its liberation by India in 1961. This long colonial period has left a distinctive cultural imprint, visible in the Latin Quarter of Panjim, the churches of Old Goa (a UNESCO World Heritage Site), and the unique Indo-Portuguese cuisine. Before the Portuguese, Goa was ruled by the Kadamba dynasty, the Delhi Sultanate, and the Vijayanagara Empire. Today, Goa is India\'s smallest state by area and is famous for its beaches, nightlife, places of worship and World Heritage-listed architecture.',
            facts: { bestTime: 'November – February', entryFee: 'Free (Beaches are public)', timings: 'All day', unesco: true, builtIn: 'Churches of Old Goa (16th-17th century)' },
            highlights: ['Baga & Calangute for nightlife', 'Palolem for serene beauty', 'Basilica of Bom Jesus (UNESCO)', 'Dudhsagar Waterfalls trek', 'Spice plantation tours'],
            howToReach: { air: 'Dabolim Airport (GOI) – centrally located', rail: 'Madgaon & Thivim Railway Stations', road: 'NH-66 connects Goa to Mumbai (10 hrs) and Bangalore (10 hrs)' }
        },
        {
            id: 5,
            name: 'Amber Fort',
            location: 'Jaipur, Rajasthan',
            category: 'Forts & Palaces',
            description: 'A majestic hilltop fort-palace with stunning mix of Hindu and Mughal architecture, overlooking Maota Lake.',
            hero: 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&q=80',
                'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800&q=80',
                'https://images.unsplash.com/photo-1603262110263-fb0112e7cc33?w=800&q=80',
                'https://images.unsplash.com/photo-1598091383021-15ddea10925d?w=800&q=80',
            ],
            history: 'Amber Fort, also known as Amer Fort, was built in 1592 by Raja Man Singh I as the capital of the Kachwaha Rajputs. Perched on a hill overlooking Maota Lake, the fort is a stunning example of Rajput architecture. Its construction continued under successive rulers for over 150 years. The fort complex includes the Diwan-i-Aam (Hall of Public Audience), Diwan-i-Khas (Hall of Private Audience), the stunning Sheesh Mahal (Mirror Palace), and the Sukh Niwas where a natural air-conditioning system was used. It is part of the Hill Forts of Rajasthan UNESCO World Heritage Site.',
            facts: { bestTime: 'October – March', entryFee: '₹100 (Indians) / ₹500 (Foreigners)', timings: '8:00 AM – 5:30 PM', unesco: true, builtIn: '1592 AD' },
            highlights: ['Sheesh Mahal (Mirror Palace)', 'Light & Sound show in the evening', 'Elephant ride up to the fort (ethical alternatives available)', 'Panoramic views of Jaipur', 'Ganesh Pol – the ornate gateway'],
            howToReach: { air: 'Jaipur International Airport – 27 km', rail: 'Jaipur Junction – 11 km', road: '11 km from Jaipur city center via NH-8' }
        },
        {
            id: 6,
            name: 'Jim Corbett National Park',
            location: 'Nainital, Uttarakhand',
            category: 'Wildlife',
            description: 'India\'s oldest national park and a premier tiger reserve, set in the foothills of the Himalayas.',
            hero: 'https://images.unsplash.com/photo-1615824996195-f780bba7cfab?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1615824996195-f780bba7cfab?w=800&q=80',
                'https://images.unsplash.com/photo-1549366021-9f761d450615?w=800&q=80',
                'https://images.unsplash.com/photo-1574068468488-20f948fde7ba?w=800&q=80',
                'https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=800&q=80',
            ],
            history: 'Jim Corbett National Park was established in 1936 as Hailey National Park, making it the oldest national park in India and all of Asia. It was the first area to come under the Project Tiger initiative in 1973. Named after the legendary hunter-turned-conservationist Jim Corbett, the park spans 520 square kilometres of hills, rivers, marshy depressions, grasslands and large lakes. The park is home to about 160 Bengal tigers, along with leopards, elephants, deer and over 600 species of birds. The Ramganga River flows through the park, creating diverse habitats.',
            facts: { bestTime: 'November – June', entryFee: '₹200 (Indians) / ₹1,500 (Foreigners) + Jeep safari charges', timings: '6:00 AM – 6:00 PM (varies by zone)', unesco: false, builtIn: 'Established 1936' },
            highlights: ['Jeep safari in Dhikala zone', 'Tiger spotting at dawn', 'Bird watching (600+ species)', 'Elephant safari through grasslands', 'Stay at forest rest houses'],
            howToReach: { air: 'Pantnagar Airport – 80 km', rail: 'Ramnagar Railway Station – 12 km', road: 'Well connected from Delhi via NH-9 (5-6 hrs)' }
        },
        {
            id: 7,
            name: 'Hampi',
            location: 'Ballari, Karnataka',
            category: 'Heritage',
            description: 'The spectacular ruins of the Vijayanagara Empire, scattered across a surreal boulder-strewn landscape.',
            hero: 'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?w=800&q=80',
                'https://images.unsplash.com/photo-1600100396929-2e4144e0cca8?w=800&q=80',
                'https://images.unsplash.com/photo-1621996659490-3275b4d0d951?w=800&q=80',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80',
            ],
            history: 'Hampi was the capital of the Vijayanagara Empire from the 14th to the 16th century, and at its peak was one of the largest and richest cities in the world, reportedly larger than Rome. The empire fell after the Battle of Talikota in 1565, and the city was looted and destroyed over six months. The ruins spread over 26 square kilometres include temples, palaces, market streets, aquatic structures and royal pavilions. The Virupaksha Temple, dedicated to Lord Shiva, has been in continuous worship since the 7th century. Hampi was designated a UNESCO World Heritage Site in 1986.',
            facts: { bestTime: 'October – February', entryFee: '₹40 (Indians) / ₹600 (Foreigners) for key monuments', timings: '6:00 AM – 6:00 PM', unesco: true, builtIn: '14th–16th century' },
            highlights: ['Virupaksha Temple at sunrise', 'Stone chariot at Vittala Temple', 'Coracle ride on Tungabhadra River', 'Sunset from Matanga Hill', 'Royal Enclosure & elephant stables'],
            howToReach: { air: 'Hubli Airport – 145 km', rail: 'Hospet Junction – 13 km', road: 'Well connected from Bangalore (6 hrs) and Goa (6 hrs)' }
        },
        {
            id: 8,
            name: 'Meenakshi Temple',
            location: 'Madurai, Tamil Nadu',
            category: 'Temples',
            description: 'A vibrant kaleidoscope of Dravidian architecture with thousands of colourful sculptures adorning its towering gopurams.',
            hero: 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&q=80',
                'https://images.unsplash.com/photo-1625731226721-b4d51ae70e20?w=800&q=80',
                'https://images.unsplash.com/photo-1621777525972-07de3b86f928?w=800&q=80',
                'https://images.unsplash.com/photo-1574956324730-b3b3e93c4b67?w=800&q=80',
            ],
            history: 'The Meenakshi Amman Temple is a historic Hindu temple located on the southern bank of the Vaigai River in Madurai. It is dedicated to Meenakshi (a form of Parvati) and Sundareshwar (a form of Shiva). The original temple was built by the Pandyan king Kulasekara Pandya around the 6th century BC, but the current structure dates back to the 17th century, rebuilt by Thirumalai Nayak. The temple complex covers 14 acres and has 14 gopurams (gateway towers), the tallest being 170 feet. There are an estimated 33,000 sculptures within the complex.',
            facts: { bestTime: 'October – March', entryFee: 'Free (Camera: ₹50)', timings: '5:00 AM – 12:30 PM, 4:00 PM – 9:30 PM', unesco: false, builtIn: '6th century BC (rebuilt 17th century)' },
            highlights: ['Hall of 1000 Pillars', 'Evening ceremony at the temple', 'Golden Lotus Tank', 'Temple Art Museum', 'Thirumalai Nayak Palace nearby'],
            howToReach: { air: 'Madurai Airport – 12 km', rail: 'Madurai Junction – 1 km', road: 'Well connected from Chennai (8 hrs), Bangalore (7 hrs)' }
        },
        {
            id: 9,
            name: 'Ladakh',
            location: 'Leh, Ladakh',
            category: 'Nature',
            description: 'The "Land of High Passes" — a stark, stunning high-altitude desert with turquoise lakes and ancient Buddhist monasteries.',
            hero: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800&q=80',
                'https://images.unsplash.com/photo-1589556264800-08ae9e129a8c?w=800&q=80',
                'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800&q=80',
                'https://images.unsplash.com/photo-1573496130103-a07e9d65e885?w=800&q=80',
            ],
            history: 'Ladakh, meaning "land of high passes", has been a crossroads of Central Asian trade routes for centuries. Historically part of the Tibetan cultural sphere, it became an independent kingdom in the 10th century under King Nyima-Gon. The region was absorbed into the Dogra dynasty of Jammu in the 19th century. Ladakh is known for its remote mountain beauty and Buddhist culture. The Hemis Monastery, dating to 1672, is the largest and wealthiest monastery in Ladakh. The region\'s strategic location between India, China, and Pakistan has given it immense geopolitical importance. In 2019, Ladakh was reorganized as a Union Territory of India.',
            facts: { bestTime: 'June – September', entryFee: 'Inner Line Permit required for some areas', timings: 'Varies by site', unesco: false, builtIn: 'Hemis Monastery (1672)' },
            highlights: ['Pangong Tso Lake', 'Nubra Valley & sand dunes', 'Khardung La – one of the highest motorable passes', 'Thiksey & Hemis Monasteries', 'Magnetic Hill & Zanskar River rafting'],
            howToReach: { air: 'Kushok Bakula Rimpochee Airport, Leh – direct flights from Delhi', rail: 'Nearest station: Jammu Tawi – 700 km', road: 'Manali-Leh Highway (2 days) or Srinagar-Leh Highway (2 days)' }
        },
        {
            id: 10,
            name: 'Rann of Kutch',
            location: 'Kutch, Gujarat',
            category: 'Nature',
            description: 'A vast expanse of white salt desert that transforms into a magical moonscape under the full moon.',
            hero: 'https://images.unsplash.com/photo-1588096344356-9b497042e9a8?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1588096344356-9b497042e9a8?w=800&q=80',
                'https://images.unsplash.com/photo-1609766857041-ed402ea8069a?w=800&q=80',
                'https://images.unsplash.com/photo-1623069789895-1781bf734856?w=800&q=80',
                'https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=800&q=80',
            ],
            history: 'The Rann of Kutch is a vast salt marsh in the Thar Desert in the Kutch district of Gujarat. It is divided into the Great Rann and the Little Rann, covering approximately 30,000 square kilometres. During the monsoon, the Arabian Sea floods the flat desert, and when it recedes, a vast white salt plain remains — one of the largest salt deserts in the world. The Gujarat government organizes the Rann Utsav (Rann Festival) from November to February, which showcases the region\'s unique culture, handicrafts, music, and dance. The region is also home to the Indian Wild Ass Sanctuary.',
            facts: { bestTime: 'November – February (Rann Utsav season)', entryFee: '₹100 entry + tent/resort stay', timings: 'Rann Utsav: Nov–Feb', unesco: false, builtIn: 'Natural Formation' },
            highlights: ['Full moon night on the white desert', 'Rann Utsav cultural festival', 'Kutchi handicraft villages', 'Wild Ass Sanctuary in Little Rann', 'Sunset & sunrise on the salt flat'],
            howToReach: { air: 'Bhuj Airport – 80 km', rail: 'Bhuj Railway Station – 80 km', road: 'From Ahmedabad via NH-8A (5-6 hrs)' }
        },
        {
            id: 11,
            name: 'Mysore Palace',
            location: 'Mysuru, Karnataka',
            category: 'Forts & Palaces',
            description: 'A dazzling Indo-Saracenic palace illuminated by 97,000 light bulbs every Sunday and during Dasara.',
            hero: 'https://images.unsplash.com/photo-1600100397608-de81ee2e2a6e?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1600100397608-de81ee2e2a6e?w=800&q=80',
                'https://images.unsplash.com/photo-1580581096469-8afb1c5ee4a2?w=800&q=80',
                'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800&q=80',
                'https://images.unsplash.com/photo-1614082242765-7c98ca0f3df3?w=800&q=80',
            ],
            history: 'The Mysore Palace, also known as Amba Vilas Palace, is the official residence of the Wadiyar dynasty, the former royal family of the Kingdom of Mysore. The current palace was built between 1897 and 1912 after the old wooden palace was destroyed by fire. Designed by the British architect Henry Irwin, the palace is a three-storey stone structure with marble domes, a 145-foot five-storey tower, and interiors decorated with carvings, stained glass, mosaic floors, and paintings. It is the most visited monument in India after the Taj Mahal, with over 6 million visitors annually.',
            facts: { bestTime: 'October (Dasara festival)', entryFee: '₹70 (Indians) / ₹200 (Foreigners)', timings: '10:00 AM – 5:30 PM', unesco: false, builtIn: '1897–1912' },
            highlights: ['Palace illumination on Sundays (7-8 PM)', 'Dasara festival celebrations (October)', 'Golden Howdah in the palace', 'Devaraja Market nearby', 'Chamundi Hills & Nandi Bull statue'],
            howToReach: { air: 'Mysore Airport (limited flights) or Bangalore Airport – 170 km', rail: 'Mysore Junction – 3 km', road: 'From Bangalore via Mysore Expressway (3 hrs)' }
        },
        {
            id: 12,
            name: 'Golden Temple',
            location: 'Amritsar, Punjab',
            category: 'Temples',
            description: 'The holiest Gurdwara in Sikhism, its gilded sanctum gleaming over the sacred Amrit Sarovar pool.',
            hero: 'https://images.unsplash.com/photo-1609947017136-9dfc44a35fa6?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1609947017136-9dfc44a35fa6?w=800&q=80',
                'https://images.unsplash.com/photo-1588096344356-9b497042e9a8?w=800&q=80',
                'https://images.unsplash.com/photo-1514222134-b57cbb8ce073?w=800&q=80',
                'https://images.unsplash.com/photo-1518002054494-3a6f94352e9d?w=800&q=80',
            ],
            history: 'Sri Harmandir Sahib, commonly known as the Golden Temple, is the holiest Gurdwara and most important pilgrimage site of Sikhism. The construction was initiated by Guru Ram Das, the fourth Sikh Guru, in 1577. The temple sits in the center of the Amrit Sarovar (Pool of Nectar), from which the city of Amritsar derives its name. The upper floors of the temple are covered with 750 kg of pure gold, giving it its distinctive appearance. The Langar (community kitchen) serves free meals to over 100,000 people every day regardless of religion, caste, or background — making it the largest free kitchen in the world.',
            facts: { bestTime: 'October – March', entryFee: 'Free', timings: 'Open 24 hours', unesco: false, builtIn: '1577–1604 AD' },
            highlights: ['Palki Sahib ceremony at night', 'Langar – world\'s largest free kitchen', 'Jallianwala Bagh memorial nearby', 'Wagah Border ceremony (30 km)', 'Night view of the illuminated temple'],
            howToReach: { air: 'Sri Guru Ram Dass Jee Airport – 11 km', rail: 'Amritsar Junction – 2 km', road: 'From Delhi via NH-1 (7-8 hrs)' }
        },
        {
            id: 13,
            name: 'Andaman Islands',
            location: 'Port Blair, Andaman & Nicobar',
            category: 'Beaches',
            description: 'Crystal clear waters, pristine coral reefs, and untouched tropical forests in India\'s island paradise.',
            hero: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80',
                'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=800&q=80',
                'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
                'https://images.unsplash.com/photo-1468413253725-0d5181091126?w=800&q=80',
            ],
            history: 'The Andaman and Nicobar Islands are a group of 572 islands at the junction of the Bay of Bengal and the Andaman Sea. They have been inhabited for thousands of years by indigenous peoples. During British colonial rule, the islands were used as a penal colony. The Cellular Jail in Port Blair, built between 1896 and 1906, housed Indian political prisoners and freedom fighters. The islands were occupied by Japan during World War II. Today, only about 38 islands are inhabited, and they are famous for their biodiversity, coral reefs, and pristine beaches like Radhanagar Beach, rated among Asia\'s best.',
            facts: { bestTime: 'October – May', entryFee: 'Varies by attraction (Cellular Jail: ₹30)', timings: 'Varies by site', unesco: false, builtIn: 'Cellular Jail (1896–1906)' },
            highlights: ['Radhanagar Beach – Asia\'s best beach', 'Scuba diving at Havelock Island', 'Cellular Jail light & sound show', 'Sea walking at North Bay Island', 'Limestone caves at Baratang Island'],
            howToReach: { air: 'Veer Savarkar Airport, Port Blair – direct flights from Delhi, Chennai, Kolkata', rail: 'No railway (island)', road: 'Inter-island ferries from Port Blair' }
        },
        {
            id: 14,
            name: 'Khajuraho Temples',
            location: 'Chhatarpur, Madhya Pradesh',
            category: 'Temples',
            description: 'UNESCO-listed medieval Hindu and Jain temples renowned for their stunning erotic sculptures and nagara-style architecture.',
            hero: 'https://images.unsplash.com/photo-1600100356729-4b566a02cafa?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1600100356729-4b566a02cafa?w=800&q=80',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80',
                'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&q=80',
                'https://images.unsplash.com/photo-1625731226721-b4d51ae70e20?w=800&q=80',
            ],
            history: 'The Khajuraho Group of Monuments is a collection of Hindu and Jain temples built between 950 and 1050 AD by the Chandela dynasty. Of the original 85 temples, only 25 survive today, spread across an area of about 6 square kilometres. The temples are famous for their nagara-style architectural symbolism and erotic sculptures that celebrate the theme of love, life, and divine creation. Only about 10% of the carvings are erotic — the rest depict everyday life, mythological stories, and celestial beings. The temples were rediscovered by the British in 1838 and declared a UNESCO World Heritage Site in 1986.',
            facts: { bestTime: 'October – March', entryFee: '₹40 (Indians) / ₹600 (Foreigners)', timings: 'Sunrise to Sunset', unesco: true, builtIn: '950–1050 AD' },
            highlights: ['Kandariya Mahadeva Temple', 'Light & Sound show in the evening', 'Sculpture museum', 'Panna National Park nearby', 'Raneh Falls (20 km away)'],
            howToReach: { air: 'Khajuraho Airport – 5 km (flights from Delhi & Varanasi)', rail: 'Khajuraho Railway Station – 6 km', road: 'From Jhansi (175 km) or Satna (117 km)' }
        },
        {
            id: 15,
            name: 'Sundarbans',
            location: 'South 24 Parganas, West Bengal',
            category: 'Wildlife',
            description: 'The world\'s largest mangrove forest and a UNESCO site, home to the legendary Royal Bengal Tiger.',
            hero: 'https://images.unsplash.com/photo-1568454537842-d933259bb258?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1568454537842-d933259bb258?w=800&q=80',
                'https://images.unsplash.com/photo-1615824996195-f780bba7cfab?w=800&q=80',
                'https://images.unsplash.com/photo-1549366021-9f761d450615?w=800&q=80',
                'https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=800&q=80',
            ],
            history: 'The Sundarbans is the largest single block of tidal halophytic mangrove forest in the world, spanning approximately 10,000 square kilometres across India and Bangladesh. The Indian portion covers about 4,264 square kilometres and was designated a UNESCO World Heritage Site in 1987. The name "Sundarbans" is thought to derive from "Sundari" (Heritiera fomes), the dominant mangrove species in the area. The forest is home to around 100 Royal Bengal Tigers — the only tigers in the world adapted to swimming in salt water. The Sundarbans also supports rich biodiversity including saltwater crocodiles, Indian pythons, and over 260 bird species.',
            facts: { bestTime: 'September – March', entryFee: '₹60 (Indians) / ₹200 (Foreigners) + boat charges', timings: 'Day trips 8 AM – 5 PM', unesco: true, builtIn: 'Natural Formation (Tiger Reserve since 1973)' },
            highlights: ['Boat safari through mangrove channels', 'Tiger spotting from watchtowers', 'Sajnekhali Bird Sanctuary', 'Dobanki canopy walk', 'Local fishing village visits'],
            howToReach: { air: 'Netaji Subhas Chandra Bose Airport, Kolkata – 100 km', rail: 'Canning Railway Station – 48 km from Gosaba', road: 'From Kolkata to Godkhali jetty (3-4 hrs), then boat' }
        },
        {
            id: 16,
            name: 'Hawa Mahal',
            location: 'Jaipur, Rajasthan',
            category: 'Forts & Palaces',
            description: 'The iconic "Palace of Winds" with 953 small windows, built so royal women could observe street life unseen.',
            hero: 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&q=80',
                'https://images.unsplash.com/photo-1603262110263-fb0112e7cc33?w=800&q=80',
                'https://images.unsplash.com/photo-1598091383021-15ddea10925d?w=800&q=80',
                'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800&q=80',
            ],
            history: 'Hawa Mahal, literally "Palace of Winds," was built in 1799 by Maharaja Sawai Pratap Singh as an extension of the Royal City Palace. Its unique five-storey honeycomb facade with 953 small windows (jharokhas) was designed to allow royal women of the court to observe everyday life and processions on the street below without being seen — in accordance with the practice of purdah. The building was designed by Lal Chand Ustad in the form of the crown of Krishna. Despite its height, the structure is only one room deep in most places, making it essentially an elaborate facade.',
            facts: { bestTime: 'October – March', entryFee: '₹50 (Indians) / ₹200 (Foreigners)', timings: '9:00 AM – 5:00 PM', unesco: false, builtIn: '1799 AD' },
            highlights: ['Sunrise view of the facade', 'Rooftop views of Jaipur city', 'Jantar Mantar observatory nearby', 'City Palace complex adjacent', 'Johari Bazaar shopping below'],
            howToReach: { air: 'Jaipur International Airport – 13 km', rail: 'Jaipur Junction – 5 km', road: 'Located in the heart of Jaipur\'s old city' }
        },
        {
            id: 17,
            name: 'Valley of Flowers',
            location: 'Chamoli, Uttarakhand',
            category: 'Nature',
            description: 'A UNESCO World Heritage alpine meadow bursting with over 600 species of wildflowers set against Himalayan peaks.',
            hero: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80',
                'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80',
                'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80',
                'https://images.unsplash.com/photo-1472396961693-142e6e269027?w=800&q=80',
            ],
            history: 'The Valley of Flowers National Park is a stunning high-altitude Himalayan valley known for its meadows of endemic alpine flowers and variety of flora. The valley remained hidden from the world until 1931, when British mountaineers Frank Smythe, Eric Shipton and R.L. Holdsworth stumbled upon it during a return from an expedition to Mount Kamet. Smythe was so enchanted that he returned in 1937 and wrote the book "The Valley of Flowers." The park covers 87.5 sq km at an altitude of 3,250–6,675 metres and is home to over 600 species of flowering plants, including rare orchids, poppies, marigolds, and the endangered Brahma Kamal.',
            facts: { bestTime: 'July – September (peak bloom)', entryFee: '₹150 (Indians) / ₹600 (Foreigners) per 3 days', timings: '7:00 AM – 5:00 PM', unesco: true, builtIn: 'National Park since 1982' },
            highlights: ['Trek through blooming meadows', 'Hemkund Sahib Gurudwara nearby', 'Rare Brahma Kamal flowers', 'Spectacular Himalayan views', 'Rich butterfly & bird diversity'],
            howToReach: { air: 'Jolly Grant Airport, Dehradun – 295 km', rail: 'Rishikesh / Haridwar – 270 km', road: 'Drive to Govindghat, then 17 km trek to the valley' }
        },
        {
            id: 18,
            name: 'Ajanta & Ellora Caves',
            location: 'Aurangabad, Maharashtra',
            category: 'Heritage',
            description: 'Ancient rock-cut cave monasteries with exquisite Buddhist, Hindu and Jain paintings and sculptures spanning 800 years.',
            hero: 'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?w=1200&q=80',
            images: [
                'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?w=800&q=80',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80',
                'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&q=80',
                'https://images.unsplash.com/photo-1600100356729-4b566a02cafa?w=800&q=80',
            ],
            history: 'The Ajanta Caves (2nd century BCE to 6th century CE) are 30 rock-cut Buddhist cave monuments that include paintings and sculptures considered masterpieces of Buddhist religious art. They were carved in a horseshoe-shaped cliff alongside the Waghur River. The caves were abandoned around 480 CE and forgotten until 1819, when a British officer rediscovered them during a tiger hunt. The Ellora Caves (6th-11th century CE), located 100 km away, comprise 34 caves — Buddhist, Hindu, and Jain — representing the artistic zenith of Indian rock-cut architecture. The Kailasa Temple (Cave 16) at Ellora is the largest monolithic rock excavation in the world. Both sites are UNESCO World Heritage Sites.',
            facts: { bestTime: 'October – March', entryFee: '₹40 (Indians) / ₹600 (Foreigners) per site', timings: '9 AM – 5:30 PM (Ajanta closed Mon, Ellora closed Tue)', unesco: true, builtIn: '2nd century BCE – 11th century CE' },
            highlights: ['Ajanta cave paintings (especially Cave 1 & 2)', 'Kailasa Temple at Ellora – carved from a single rock', 'Buddhist viharas and chaityas', 'Bibi Ka Maqbara ("Mini Taj") nearby', 'Daulatabad Fort en route'],
            howToReach: { air: 'Aurangabad Airport – 30 km from Ellora, 100 km from Ajanta', rail: 'Aurangabad Railway Station', road: 'From Mumbai (6 hrs) or Pune (5 hrs) via NH-60' }
        },
    ];

    const CATEGORIES = ['All', 'Heritage', 'Temples', 'Forts & Palaces', 'Beaches', 'Nature', 'Wildlife'];

    // ── State ───────────────────────────────────────────────────────
    let currentView = 'list'; // 'list' or 'detail'
    let selectedPlace = null;
    let activeCategory = 'All';
    let searchQuery = '';
    let galleryIndex = 0;

    // ── DOM ─────────────────────────────────────────────────────────
    const root = document.getElementById('explore-root');

    function setState(updates) {
        if ('currentView' in updates) currentView = updates.currentView;
        if ('selectedPlace' in updates) selectedPlace = updates.selectedPlace;
        if ('activeCategory' in updates) activeCategory = updates.activeCategory;
        if ('searchQuery' in updates) searchQuery = updates.searchQuery;
        if ('galleryIndex' in updates) galleryIndex = updates.galleryIndex;
        render();
    }

    // ── Filtering ───────────────────────────────────────────────────
    function getFilteredPlaces() {
        let places = PLACES;
        if (activeCategory !== 'All') {
            places = places.filter(p => p.category === activeCategory);
        }
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            places = places.filter(p =>
                p.name.toLowerCase().includes(q) ||
                p.location.toLowerCase().includes(q) ||
                p.category.toLowerCase().includes(q) ||
                p.description.toLowerCase().includes(q)
            );
        }
        return places;
    }

    // ── Category badge colors ───────────────────────────────────────
    function badgeClass(cat) {
        const map = {
            'Heritage': 'badge-heritage',
            'Temples': 'badge-temples',
            'Forts & Palaces': 'badge-forts',
            'Beaches': 'badge-beaches',
            'Nature': 'badge-nature',
            'Wildlife': 'badge-wildlife',
        };
        return map[cat] || 'badge-heritage';
    }

    // ── Render ──────────────────────────────────────────────────────
    function render() {
        if (currentView === 'detail' && selectedPlace) {
            renderDetail();
        } else {
            renderList();
        }
        // Re-init lucide icons
        if (window.lucide) lucide.createIcons();
    }

    // ── List View ───────────────────────────────────────────────────
    function renderList() {
        const places = getFilteredPlaces();
        root.innerHTML = `
            <div class="explore-list-view">
                <!-- Hero Banner -->
                <div class="explore-hero">
                    <div class="explore-hero-overlay"></div>
                    <div class="explore-hero-content">
                        <h1 class="explore-hero-title">Discover Incredible India</h1>
                        <p class="explore-hero-sub">From ancient temples to pristine beaches — explore the soul of a timeless land</p>
                    </div>
                </div>

                <div class="explore-container">
                    <!-- Search -->
                    <div class="explore-search-row">
                        <div class="explore-search-box">
                            <i data-lucide="search" class="explore-search-icon"></i>
                            <input type="text" id="explore-search" placeholder="Search places, cities, categories..."
                                   value="${searchQuery}" class="explore-search-input" />
                        </div>
                    </div>

                    <!-- Category Tabs -->
                    <div class="explore-tabs" id="explore-tabs">
                        ${CATEGORIES.map(cat => `
                            <button class="explore-tab ${activeCategory === cat ? 'active' : ''}"
                                    data-cat="${cat}">${cat}</button>
                        `).join('')}
                    </div>

                    <!-- Results Count -->
                    <p class="explore-count">${places.length} destination${places.length !== 1 ? 's' : ''} found</p>

                    <!-- Cards Grid -->
                    <div class="explore-grid">
                        ${places.map((p, i) => `
                            <div class="explore-card" data-id="${p.id}" style="animation-delay:${i * 0.05}s">
                                <div class="explore-card-img-wrap">
                                    <img src="${p.hero}" alt="${p.name}" class="explore-card-img" loading="lazy"
                                         onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&q=80';" />
                                    <span class="explore-card-badge ${badgeClass(p.category)}">${p.category}</span>
                                </div>
                                <div class="explore-card-body">
                                    <h3 class="explore-card-title">${p.name}</h3>
                                    <div class="explore-card-loc">
                                        <i data-lucide="map-pin" class="w-3.5 h-3.5"></i>
                                        <span>${p.location}</span>
                                    </div>
                                    <p class="explore-card-desc">${p.description}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    ${places.length === 0 ? `
                        <div class="explore-empty">
                            <i data-lucide="search-x" class="w-12 h-12 mb-3 opacity-40"></i>
                            <p>No destinations match your search</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Attach events
        document.getElementById('explore-search').addEventListener('input', function(e) {
            setState({ searchQuery: e.target.value });
        });
        document.getElementById('explore-tabs').addEventListener('click', function(e) {
            if (e.target.classList.contains('explore-tab')) {
                setState({ activeCategory: e.target.dataset.cat });
            }
        });
        root.querySelectorAll('.explore-card').forEach(card => {
            card.addEventListener('click', function() {
                const id = parseInt(this.dataset.id);
                const place = PLACES.find(p => p.id === id);
                if (place) {
                    setState({ currentView: 'detail', selectedPlace: place, galleryIndex: 0 });
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        });
    }

    // ── Detail View ─────────────────────────────────────────────────
    function renderDetail() {
        const p = selectedPlace;
        root.innerHTML = `
            <div class="explore-detail-view detail-enter">
                <!-- Hero -->
                <div class="detail-hero">
                    <img src="${p.hero}" alt="${p.name}" class="detail-hero-img"
                         onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200&q=80';" />
                    <div class="detail-hero-overlay"></div>
                    <button class="detail-back-btn" id="detail-back">
                        <i data-lucide="arrow-left" class="w-5 h-5"></i>
                        <span>Back to Explorer</span>
                    </button>
                    <div class="detail-hero-content">
                        <span class="explore-card-badge ${badgeClass(p.category)} mb-3">${p.category}</span>
                        <h1 class="detail-hero-title">${p.name}</h1>
                        <div class="detail-hero-loc">
                            <i data-lucide="map-pin" class="w-4 h-4"></i>
                            <span>${p.location}</span>
                        </div>
                    </div>
                </div>

                <div class="detail-container">
                    <!-- Key Facts -->
                    <div class="detail-facts">
                        <div class="detail-fact">
                            <i data-lucide="calendar" class="detail-fact-icon"></i>
                            <div>
                                <span class="detail-fact-label">Best Time to Visit</span>
                                <span class="detail-fact-value">${p.facts.bestTime}</span>
                            </div>
                        </div>
                        <div class="detail-fact">
                            <i data-lucide="ticket" class="detail-fact-icon"></i>
                            <div>
                                <span class="detail-fact-label">Entry Fee</span>
                                <span class="detail-fact-value">${p.facts.entryFee}</span>
                            </div>
                        </div>
                        <div class="detail-fact">
                            <i data-lucide="clock" class="detail-fact-icon"></i>
                            <div>
                                <span class="detail-fact-label">Timings</span>
                                <span class="detail-fact-value">${p.facts.timings}</span>
                            </div>
                        </div>
                        <div class="detail-fact">
                            <i data-lucide="landmark" class="detail-fact-icon"></i>
                            <div>
                                <span class="detail-fact-label">Built / Established</span>
                                <span class="detail-fact-value">${p.facts.builtIn}</span>
                            </div>
                        </div>
                        ${p.facts.unesco ? `
                        <div class="detail-fact detail-fact-unesco">
                            <i data-lucide="award" class="detail-fact-icon"></i>
                            <div>
                                <span class="detail-fact-label">UNESCO Status</span>
                                <span class="detail-fact-value">World Heritage Site</span>
                            </div>
                        </div>` : ''}
                    </div>

                    <!-- History -->
                    <section class="detail-section">
                        <h2 class="detail-section-title">
                            <i data-lucide="book-open" class="w-5 h-5"></i>
                            History & Background
                        </h2>
                        <p class="detail-section-text">${p.history}</p>
                    </section>

                    <!-- Photo Gallery -->
                    <section class="detail-section">
                        <h2 class="detail-section-title">
                            <i data-lucide="images" class="w-5 h-5"></i>
                            Photo Gallery
                        </h2>
                        <div class="detail-gallery">
                            <div class="detail-gallery-main">
                                <img src="${p.images[galleryIndex]}" alt="${p.name}" id="gallery-main-img"
                                     onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&q=80';" />
                                <button class="gallery-nav gallery-prev" id="gallery-prev">
                                    <i data-lucide="chevron-left" class="w-5 h-5"></i>
                                </button>
                                <button class="gallery-nav gallery-next" id="gallery-next">
                                    <i data-lucide="chevron-right" class="w-5 h-5"></i>
                                </button>
                            </div>
                            <div class="detail-gallery-thumbs">
                                ${p.images.map((img, i) => `
                                    <img src="${img}" alt="Photo ${i+1}" data-idx="${i}"
                                         class="detail-gallery-thumb ${i === galleryIndex ? 'active' : ''}"
                                         onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&q=80';" />
                                `).join('')}
                            </div>
                        </div>
                    </section>

                    <!-- Things to Do -->
                    <section class="detail-section">
                        <h2 class="detail-section-title">
                            <i data-lucide="sparkles" class="w-5 h-5"></i>
                            Things to Do & Highlights
                        </h2>
                        <div class="detail-highlights">
                            ${p.highlights.map(h => `
                                <div class="detail-highlight-item">
                                    <i data-lucide="check-circle-2" class="w-5 h-5 shrink-0"></i>
                                    <span>${h}</span>
                                </div>
                            `).join('')}
                        </div>
                    </section>

                    <!-- How to Reach -->
                    <section class="detail-section">
                        <h2 class="detail-section-title">
                            <i data-lucide="route" class="w-5 h-5"></i>
                            How to Reach
                        </h2>
                        <div class="detail-reach">
                            <div class="detail-reach-item">
                                <div class="detail-reach-icon"><i data-lucide="plane" class="w-5 h-5"></i></div>
                                <div>
                                    <span class="detail-reach-mode">By Air</span>
                                    <span class="detail-reach-desc">${p.howToReach.air}</span>
                                </div>
                            </div>
                            <div class="detail-reach-item">
                                <div class="detail-reach-icon"><i data-lucide="train-front" class="w-5 h-5"></i></div>
                                <div>
                                    <span class="detail-reach-mode">By Rail</span>
                                    <span class="detail-reach-desc">${p.howToReach.rail}</span>
                                </div>
                            </div>
                            <div class="detail-reach-item">
                                <div class="detail-reach-icon"><i data-lucide="car" class="w-5 h-5"></i></div>
                                <div>
                                    <span class="detail-reach-mode">By Road</span>
                                    <span class="detail-reach-desc">${p.howToReach.road}</span>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        `;

        // Attach detail events
        document.getElementById('detail-back').addEventListener('click', function() {
            setState({ currentView: 'list', selectedPlace: null });
        });
        document.getElementById('gallery-prev').addEventListener('click', function() {
            const newIdx = galleryIndex > 0 ? galleryIndex - 1 : p.images.length - 1;
            setState({ galleryIndex: newIdx });
        });
        document.getElementById('gallery-next').addEventListener('click', function() {
            const newIdx = galleryIndex < p.images.length - 1 ? galleryIndex + 1 : 0;
            setState({ galleryIndex: newIdx });
        });
        root.querySelectorAll('.detail-gallery-thumb').forEach(thumb => {
            thumb.addEventListener('click', function() {
                setState({ galleryIndex: parseInt(this.dataset.idx) });
            });
        });
    }

    // ── Init ────────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function() {
        render();
    });
})();
