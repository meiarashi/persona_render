// ペルソナのランダムデータ生成モジュール

// 患者タイプの詳細情報
const patientTypeDetailsMap = {
    '利便性重視型': { 
        description: 'アクセスの良さ、待ち時間の短さ、診療時間の柔軟性など、便利さを最優先', 
        example: '忙しいビジネスパーソン、オンライン診療を好む患者' 
    },
    '専門医療追求型': { 
        description: '専門医や高度専門医療機関での治療を希望し、医師の経歴や実績を重視', 
        example: '難病患者、複雑な症状を持つ患者' 
    },
    '予防健康管理型': { 
        description: '病気になる前の予防や早期発見、健康維持に関心が高い', 
        example: '定期健診を欠かさない人、予防接種に積極的な人' 
    },
    '代替医療志向型': { 
        description: '漢方、鍼灸、ホメオパシーなど、西洋医学以外の選択肢を積極的に取り入れる', 
        example: '自然療法愛好者、慢性疾患の患者' 
    },
    '経済合理型': { 
        description: '自己負担額、保険適用の有無、費用対効果を重視', 
        example: '経済的制約のある患者、医療費控除を意識する人' 
    },
    '情報探求型': { 
        description: '徹底的な情報収集、セカンドオピニオン取得、比較検討を行う', 
        example: '高学歴層、慎重な意思決定を好む患者' 
    },
    '革新技術指向型': { 
        description: '最先端の医療技術、新薬、臨床試験などに積極的に関心を持つ', 
        example: '既存治療で効果が出なかった患者、医療イノベーションに関心がある人' 
    },
    '対話重視型': { 
        description: '医師からの丁寧な説明や対話を求め、質問が多い', 
        example: '不安を感じやすい患者、医療従事者' 
    },
    '信頼基盤型': { 
        description: 'かかりつけ医との長期的な関係や医療機関の評判を重視', 
        example: '地域密着型の患者、同じ医師に長期通院する患者' 
    },
    '緊急解決型': { 
        description: '症状の即時改善を求め、緊急性を重視', 
        example: '急性疾患患者、痛みに耐性が低い患者' 
    },
    '受動依存型': { 
        description: '医師の判断に全面的に依存し、自らの決定より医師の指示を優先', 
        example: '高齢者、医療知識が少ない患者' 
    },
    '自律決定型': { 
        description: '自分の治療に主体的に関わり、最終決定権を持ちたいと考える', 
        example: '医療リテラシーが高い患者、自己管理を好む慢性疾患患者' 
    }
};

// ランダムアイテム取得
function getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

// 性別に基づくランダム名前生成
function getRandomName(gender, personaRandomValues) {
    const maleGenders = ["male", "男性"];
    const femaleGenders = ["female", "女性"];
    
    if (maleGenders.includes(gender) && personaRandomValues.names.male && personaRandomValues.names.male.length > 0) {
        return getRandomItem(personaRandomValues.names.male);
    } else if (femaleGenders.includes(gender) && personaRandomValues.names.female && personaRandomValues.names.female.length > 0) {
        return getRandomItem(personaRandomValues.names.female);
    } else if (personaRandomValues.names.unisex && personaRandomValues.names.unisex.length > 0) {
        return getRandomItem(personaRandomValues.names.unisex);
    }
    
    // フォールバック
    const allNames = [];
    if (personaRandomValues.names.male) allNames.push(...personaRandomValues.names.male);
    if (personaRandomValues.names.female) allNames.push(...personaRandomValues.names.female);
    if (personaRandomValues.names.unisex) allNames.push(...personaRandomValues.names.unisex);
    
    return allNames.length > 0 ? getRandomItem(allNames) : "名無し";
}

// ランダム年齢生成
function getRandomAge(personaRandomValues) {
    const ageRanges = personaRandomValues.ageRanges;
    if (!ageRanges || ageRanges.length === 0) {
        return "30歳"; // デフォルト
    }
    
    const randomRange = getRandomItem(ageRanges);
    
    if (randomRange.endsWith("代")) {
        const decade = parseInt(randomRange);
        const randomYear = Math.floor(Math.random() * 10);
        return `${decade + randomYear}歳`;
    } else if (randomRange.includes("〜")) {
        const [min, max] = randomRange.split("〜").map(s => parseInt(s.replace("歳", "")));
        const randomYear = min + Math.floor(Math.random() * (max - min + 1));
        return `${randomYear}歳`;
    } else {
        return randomRange;
    }
}

// ランダム都道府県と市区町村生成
function getRandomPrefectureAndMunicipality(personaRandomValues) {
    const prefectures = personaRandomValues.prefectures;
    const municipalities = personaRandomValues.municipalities;
    
    if (!prefectures || prefectures.length === 0) {
        return { prefecture: "", municipality: "" };
    }
    
    const randomPrefecture = getRandomItem(prefectures);
    const prefectureMunicipalities = municipalities.filter(m => m.startsWith(randomPrefecture));
    
    let randomMunicipality = "";
    if (prefectureMunicipalities.length > 0) {
        const fullMunicipality = getRandomItem(prefectureMunicipalities);
        randomMunicipality = fullMunicipality.replace(randomPrefecture, "");
    } else {
        const cityTypes = ["市", "町", "村", "区"];
        const defaultCityType = getRandomItem(cityTypes);
        randomMunicipality = `中央${defaultCityType}`;
    }
    
    return { prefecture: randomPrefecture, municipality: randomMunicipality };
}

// ランダム性格キーワード生成
function getRandomPersonalityKeywords(personaRandomValues) {
    const personalityKeywords = personaRandomValues.personality_keywords || [];
    if (personalityKeywords.length === 0) return "";
    
    const selectedKeywords = [];
    const keywordCount = Math.floor(Math.random() * 3) + 2; // 2-4個
    
    for (let i = 0; i < keywordCount && i < personalityKeywords.length; i++) {
        let keyword;
        do {
            keyword = getRandomItem(personalityKeywords);
        } while (selectedKeywords.includes(keyword));
        selectedKeywords.push(keyword);
    }
    
    return selectedKeywords.join("、");
}

// エクスポート
window.PersonaRandomData = {
    patientTypeDetailsMap,
    getRandomItem,
    getRandomName,
    getRandomAge,
    getRandomPrefectureAndMunicipality,
    getRandomPersonalityKeywords
};