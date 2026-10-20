"""
Qiziqarli va qiyin futbol, mantiq va umumiy bilim savollari to'plami.
Har bir to'g'ri javob uchun foydalanuvchiga Coin (tanga) beriladi.
"""

import random

QUESTIONS = [
    # ═════════════════════════════════════════════════════════════════════
    #  ⚽ FUTBOL SAVOLLARI (Qiyin va qiziqarli)
    # ═════════════════════════════════════════════════════════════════════
    {
        "id": 1,
        "category": "⚽ Futbol",
        "question": "UEFA Chempionlar Ligasida 3 xil klub bilan chempion bo'lgan yagona futbolchi kim?",
        "options": ["Klarens Zeedorf", "Krishtianu Ronaldu", "Zlatan Ibragimovich", "Xabi Alonso"],
        "correct": 0,
        "explanation": "Klarens Zeedorf: Ajax (1995), Real Madrid (1998) va Milan (2003, 2007) bilan Chempionlar Ligasini yutgan!",
        "reward": 15
    },
    {
        "id": 2,
        "category": "⚽ Futbol",
        "question": "Jahon Chempionatlari tarixida eng ko'p gol urgan futbolchi kim?",
        "options": ["Pele", "Miroslav Kloze", "Ronaldo (Fenomen)", "Gerd Myuller"],
        "correct": 1,
        "explanation": "Miroslav Kloze Jahon chempionatlarida jami 16 ta gol urgan (2002-2014).",
        "reward": 10
    },
    {
        "id": 3,
        "category": "⚽ Futbol",
        "question": "Tarixda yagona bo'lib darvozabon sifatida 'Oltin to'p' (Ballon d'Or) yutgan afsonaviy posbon kim?",
        "options": ["Janluiji Buffon", "Iker Kasilyas", "Lev Yashin", "Manuel Noyer"],
        "correct": 2,
        "explanation": "Lev Yashin 1963-yilda 'Oltin to'p'ni yutgan yagona darvozabondir.",
        "reward": 12
    },
    {
        "id": 4,
        "category": "⚽ Futbol",
        "question": "Qaysi futbol klubi o'zining butun mavsumini (38 o'yin) biror marta mag'lubiyatsiz o'tkazib 'Invincibles' (Yengilmaslar) laqabini olgan?",
        "options": ["Arsenal (2003/04)", "Manchester Yunayted (1998/99)", "Chelsi (2004/05)", "Liverpul (2019/20)"],
        "correct": 0,
        "explanation": "Arsen Venger boshchiligidagi 'Arsenal' 2003/04 mavsumda APLda biror marta yutqazmagan (26 g'alaba, 12 durang).",
        "reward": 12
    },
    {
        "id": 5,
        "category": "⚽ Futbol",
        "question": "Futbol bo'yicha Jahon Chempionatini murabbiy sifatida ham, futbolchi sifatida ham yutgan 3 ta inson kimlar?",
        "options": [
            "Zidan, Gvardiola, Klopp",
            "Zagallo, Bekkenbauer, Desham",
            "Kroyf, Anchelotti, Fergyuson",
            "Maradona, Pele, Skaloni"
        ],
        "correct": 1,
        "explanation": "Mario Zagallo (Braziliya), Frans Bekkenbauer (Germaniya) va Didye Desham (Fransiya) ikkala rolda ham JCH chempioni bo'lgan.",
        "reward": 20
    },
    {
        "id": 6,
        "category": "⚽ Futbol",
        "question": "Lionel Messi bir kalendar yilida (2012) rasmiy o'yinlarda nechta gol urib Ginnes rekordini o'rnatgan?",
        "options": ["73 ta", "82 ta", "91 ta", "98 ta"],
        "correct": 2,
        "explanation": "Messi 2012-yilda klub va terma jamoada jami 91 ta rasmiy gol urib, Gerd Myullerning (85) rekordini yangilagan.",
        "reward": 15
    },
    {
        "id": 7,
        "category": "⚽ Futbol",
        "question": "O'zbekiston milliy terma jamoasi tarixida eng ko'p gol urgan to'purar kim?",
        "options": ["Mirjalol Qosimov", "Maksim Shatskix", "Eldor Shomurodov", "Server Jeparov"],
        "correct": 2,
        "explanation": "Eldor Shomurodov terma jamoa tarixida eng ko'p gol urgan to'purardir!",
        "reward": 12
    },
    {
        "id": 8,
        "category": "⚽ Futbol",
        "question": "Klassiko (Real Madrid va Barcelona) tarixida ikkala klub safida ham o'ynagan va 'Barsa'dan 'Real'ga o'tgani uchun unga cho'chqa boshi uloqtirilgan afsona kim?",
        "options": ["Luis Figo", "Ronaldo Nazario", "Maykl Ouen", "Samuyel Eto'o"],
        "correct": 0,
        "explanation": "Luis Figo 2000-yilda Barselonadan Realga o'tganida 'Kamp Nou'da unga cho'chqa boshi uloqtirilgan.",
        "reward": 12
    },
    {
        "id": 9,
        "category": "⚽ Futbol",
        "question": "Qaysi davlat terma jamoasi Jahon Chempionati finallarida 3 marta o'ynab, biror marta chempion bo'la olmagan (abadiy ikkinchilar)?",
        "options": ["Angliya", "Niderlandiya (Gollandiya)", "Portugaliya", "Xorvatiya"],
        "correct": 1,
        "explanation": "Niderlandiya 1974, 1978 va 2010 yillarda JCH finaliga chiqib, uchtasida ham mag'lub bo'lgan.",
        "reward": 15
    },
    {
        "id": 10,
        "category": "⚽ Futbol",
        "question": "Krishtianu Ronaldu Yevropa Chempionatlari (EURO) tarixida eng ko'p gol urgan futbolchi. U nechta gol urgan?",
        "options": ["9 ta", "11 ta", "14 ta", "18 ta"],
        "correct": 2,
        "explanation": "Krishtianu Ronaldu EURO finallarida 14 ta gol urib mutlaq rekordchi hisoblanadi (Mishel Platini - 9 ta).",
        "reward": 15
    },
    {
        "id": 11,
        "category": "⚽ Futbol",
        "question": "2005-yilgi Chempionlar Ligasi 'Istanbul mo''jizasi' finalida Milan birinchi bo'limda 3:0 hisobida yutayotganida, Liverpul qancha daqiqada hisobni 3:3 qilgan?",
        "options": ["6 daqiqada", "12 daqiqada", "20 daqiqada", "30 daqiqada"],
        "correct": 0,
        "explanation": "Liverpul 54, 56 va 60-daqiqalarda — bor-yo'g'i 6 daqiqa ichida 3 ta gol urib 3:3 qilgan va penaltilarda g'alaba qozongan!",
        "reward": 18
    },
    {
        "id": 12,
        "category": "⚽ Futbol",
        "question": "Birinchi Jahon Chempionati (1930) qaysi mamlakatda o'tkazilgan va kim chempion bo'lgan?",
        "options": ["Braziliya (Braziliya)", "Urugvay (Urugvay)", "Italiya (Italiya)", "Argentina (Urugvay)"],
        "correct": 1,
        "explanation": "1930-yilgi ilk mundial Urugvayda bo'lib o'tgan va finalda Argentina ustidan 4:2 hisobida Urugvay g'alaba qozongan.",
        "reward": 15
    },
    {
        "id": 13,
        "category": "⚽ Futbol",
        "question": "APL (Premyer Liga) tarixida eng tezkor xet-trik muallifi kim (2 daqiqa 56 soniya)?",
        "options": ["Sadio Mane", "Serxio Aguero", "Erling Xoland", "Tyerri Anri"],
        "correct": 0,
        "explanation": "Sadio Mane 'Sautgempton' safida 'Aston Villa'ga qarshi 2 daqiqa 56 soniyada 3 ta gol urgan!",
        "reward": 18
    },
    {
        "id": 14,
        "category": "⚽ Futbol",
        "question": "Top-5 Yevropa ligalari ichida 'Bayer Leverkuzen' 2023/24 mavsumida ketma-ket nechta rasmiy o'yinda mag'lub bo'lmay rekord o'rnatdi?",
        "options": ["43 ta", "48 ta", "51 ta", "55 ta"],
        "correct": 2,
        "explanation": "Xabi Alonso boshchiligidagi Leverkuzen barcha musobaqalarda ketma-ket 51 ta o'yin mag'lubiyatsiz o'ynadi!",
        "reward": 15
    },
    {
        "id": 15,
        "category": "⚽ Futbol",
        "question": "Qaysi futbolchi ketma-ket 5 ta Jahon Chempionatida (2006, 2010, 2014, 2018, 2022) gol urgan yagona inson?",
        "options": ["Lionel Messi", "Krishtianu Ronaldu", "Pele", "Miroslav Kloze"],
        "correct": 1,
        "explanation": "Krishtianu Ronaldu 5 ta turli mundialda gol urgan tarixdagi yagona futbolchidir.",
        "reward": 12
    },

    # ═════════════════════════════════════════════════════════════════════
    #  🧠 MANTIQIY VA QIYIN SAVOLLAR (Miya charxlash)
    # ═════════════════════════════════════════════════════════════════════
    {
        "id": 16,
        "category": "🧠 Mantiq",
        "question": "Qaysi narsa yoshligida uzun, qariganida esa qisqa bo'ladi?",
        "options": ["Daraxt", "Sham (yoki qalam)", "Soyabon", "Inson bo'yi"],
        "correct": 1,
        "explanation": "Sham yongani sari qisqaradi, qalam ham yo'nilgani sari kalta bo'lib boradi!",
        "reward": 12
    },
    {
        "id": 17,
        "category": "🧠 Mantiq",
        "question": "Uni suvga solsangiz ham, olovga tashlasangiz ham, pichoq bilan kessangiz ham hech narsa qilmaydi. Bu nima?",
        "options": ["Havo", "Soya", "Oyna", "Tosh"],
        "correct": 1,
        "explanation": "Soya! Uni kuydirib, cho'ktirib yoki kesib bo'lmaydi.",
        "reward": 12
    },
    {
        "id": 18,
        "category": "🧠 Mantiq",
        "question": "Bir poygada siz 2-o'rindagi yuguruvchini quvib o'tdingiz. Hozir siz nechanchi o'rindasiz?",
        "options": ["1-o'rinda", "2-o'rinda", "3-o'rinda", "Poyga yakunlandi"],
        "correct": 1,
        "explanation": "Siz 2-o'rindagi odamning o'rniga o'tdingiz, demak endi siz 2-o'rindasiz (1-o'rindagi odam hali ham oldinda)!",
        "reward": 12
    },
    {
        "id": 19,
        "category": "🧠 Mantiq",
        "question": "Qancha ko'p olsangiz, u shunchalik kattalashib boradi. Bu nima?",
        "options": ["Qarz", "Chuqur (o'ra)", "Bilik", "Yosh"],
        "correct": 1,
        "explanation": "Chuqurdan tuproqni qancha ko'p olsangiz, chuqur shuncha kattalashadi!",
        "reward": 12
    },
    {
        "id": 20,
        "category": "🧠 Mantiq",
        "question": "Bir oilada 5 ta aka-uka bor. Har bir aka-ukaning 1 tadan singlisi bor. Bu oilada jami nechta farzand bor?",
        "options": ["10 ta", "6 ta", "9 ta", "5 ta"],
        "correct": 1,
        "explanation": "6 ta! Chunki o'sha 1 ta singil barcha 5 ta aka-ukaning umumiy singlisi hisoblanadi.",
        "reward": 15
    },
    {
        "id": 21,
        "category": "🧠 Mantiq",
        "question": "Barcha odamlarda bor, lekin boshqalar undan egasiga qaraganda ancha ko'p foydalanishadi. Bu nima?",
        "options": ["Telefon", "Ism", "Ko'zgu", "Pul"],
        "correct": 1,
        "explanation": "Ism! Siz o'z ismingizni kam aytasiz, boshqalar esa sizni chaqirish uchun doim aytishadi.",
        "reward": 10
    },
    {
        "id": 22,
        "category": "🧠 Mantiq",
        "question": "Dunyodagi eng katta okean qaysi?",
        "options": ["Atlantika okeani", "Tinch okeani", "Hind okeani", "Shimoliy Muz okeani"],
        "correct": 1,
        "explanation": "Tinch okeani Yer yuzasining deyarli uchdan bir qismini egallagan eng katta okeandir.",
        "reward": 10
    },
    {
        "id": 23,
        "category": "🧠 Mantiq",
        "question": "Og'zi yo'q — gapiradi, qulog'i yo'q — eshitadi, tanasi yo'q — shamolda uchadi. Bu nima?",
        "options": ["Aks-sado (Exo)", "Radio", "Bulut", "Telefon"],
        "correct": 0,
        "explanation": "Aks-sado (exo) — tovushingizni qaytaradi, lekin tanasi yo'q!",
        "reward": 12
    },
    {
        "id": 24,
        "category": "🧠 Mantiq",
        "question": "Qaysi oyda odamlar eng kam uxlashadi?",
        "options": ["Yanvar", "Fevral", "Iyun", "Dekabr"],
        "correct": 1,
        "explanation": "Fevral oyida! Chunki fevralda atigi 28 (yoki 29) kun bor — boshqa oylarga nisbatan kunlar soni eng kam.",
        "reward": 12
    },
    {
        "id": 25,
        "category": "⚽ Futbol",
        "question": "Chempionlar Ligasi finalida eng ko'p o'ynagan va 6 marta kubokni yutgan futbolchilar kimlar?",
        "options": ["Krishtianu Ronaldu va Messi", "Pako Xento, Modrich, Kroos, Karvaxal, Nacho", "Maldini va Zeedorf", "Ramos va Benzema"],
        "correct": 1,
        "explanation": "Real Madrid afsonalari (Pako Xento va 2024-yilda Modrich, Kroos, Karvaxal, Nacho) 6 tadan Chempionlar Ligasini yutgan!",
        "reward": 20
    },
    {
        "id": 26,
        "category": "⚽ Futbol",
        "question": "Futbol to'riga gol urilganda to'p to'rga tegmasdan orqaga qaytishi uchun to'rni kim ixtiro qilgan?",
        "options": ["Jon Aleksandr Brodi (1891)", "Jyul Rime (1920)", "Ebenezer Kobb Morli (1863)", "Zep Blatter (1975)"],
        "correct": 0,
        "explanation": "1891-yilda ingliz muhandisi Jon Aleksandr Brodi futbol darvozasi uchun to'rni ixtiro qilgan va patentlagan.",
        "reward": 25
    },
    {
        "id": 27,
        "category": "🧠 Mantiq",
        "question": "Qaysi idishdan hech qachon ovqat yeb bo'lmaydi?",
        "options": ["Oltin idishdan", "Bo'sh idishdan", "Singan idishdan", "Katta qozondan"],
        "correct": 1,
        "explanation": "Bo'sh idishdan ovqat yeb bo'lmaydi, chunki unda ovqatning o'zi yo'q!",
        "reward": 10
    },
    {
        "id": 28,
        "category": "⚽ Futbol",
        "question": "Qaysi futbolchi 'El Matador' laqabi bilan tanilgan?",
        "options": ["Luis Suares", "Edinson Kavani", "Radamel Falkao", "Diyego Forlan"],
        "correct": 1,
        "explanation": "Edinson Kavani 'El Matador' laqabi bilan mashhur bo'lgan urugvaylik mashhur hujumchi.",
        "reward": 12
    },
    {
        "id": 29,
        "category": "🧠 Mantiq",
        "question": "Agar 3 ta mushuk 3 ta sichqonni 3 daqiqada tutsa, 100 ta mushuk 100 ta sichqonni necha daqiqada tutadi?",
        "options": ["100 daqiqada", "3 daqiqada", "30 daqiqada", "1 daqiqada"],
        "correct": 1,
        "explanation": "3 daqiqada! Chunki 1 ta mushuk 1 ta sichqonni tutishi uchun 3 daqiqa kerak, 100 ta mushuk bir vaqtda 100 ta sichqonni 3 daqiqada tutadi.",
        "reward": 18
    },
    {
        "id": 30,
        "category": "⚽ Futbol",
        "question": "Dunyodagi eng qimmat transfer rekordi qaysi futbolchiga tegishli (222 million yevro)?",
        "options": ["Kilian Mbappe", "Neymar Jr", "Filippe Koutinyo", "Jude Bellingem"],
        "correct": 1,
        "explanation": "2017-yilda Neymar 'Barselona'dan PSJga 222 million yevro evaziga o'tib mutlaq rekord o'rnatgan.",
        "reward": 10
    }
]


def get_random_question(exclude_ids: set | None = None) -> dict:
    """Tasodifiy savolni tanlaydi."""
    if exclude_ids:
        available = [q for q in QUESTIONS if q["id"] not in exclude_ids]
        if available:
            return random.choice(available)
    return random.choice(QUESTIONS)
