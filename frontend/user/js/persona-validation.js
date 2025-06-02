// ペルソナの論理的整合性チェック用モジュール

// 年齢をパースする関数
function parseAge(ageStr) {
    if (!ageStr) return null;
    const match = ageStr.match(/(\d+)/);
    return match ? parseInt(match[1]) : null;
}

// フィールド値を取得する関数
function getFieldValue(fieldId) {
    const element = document.getElementById(fieldId);
    return element ? element.value : '';
}

// フィールド値を設定する関数
function setFieldValue(fieldId, value) {
    const element = document.getElementById(fieldId);
    if (element) {
        element.value = value;
    }
}

// ランダムアイテムを取得
function getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

// 学生・子供関連の検証
const StudentChildValidation = {
    studentOccupations: ["小学生", "中学生", "高校生", "大学生", "大学院生", "専門学校生", "浪人生"],
    
    validate: function() {
        const occupation = getFieldValue('occupation');
        const income = getFieldValue('income');
        const lifeEvent = getFieldValue('life_events');
        
        // 学生なのに高収入の矛盾を修正
        if (this.studentOccupations.includes(occupation)) {
            const incomeValue = parseInt(income);
            if (incomeValue > 100) {
                setFieldValue('income', '<100');
            }
            
            // 学生のライフイベント整合性チェック
            const inappropriateEvents = ["昇進", "起業", "定年退職", "子供が生まれた", "結婚記念日"];
            if (inappropriateEvents.some(e => lifeEvent && lifeEvent.includes(e))) {
                const studentEvents = ["進学", "アルバイトを始めた", "サークルに入った", "資格試験合格"];
                setFieldValue('life_events', getRandomItem(studentEvents));
            }
        }
        
        // 未就学児・幼児の設定を修正
        if (["未就学児", "幼稚園児", "保育園児"].includes(occupation)) {
            setFieldValue('income', '<100');
            const childHobbies = ["お絵かき", "ブロック遊び", "絵本", "公園遊び", "おままごと"];
            const hobby = getFieldValue('hobby');
            if (!childHobbies.some(h => hobby.includes(h))) {
                setFieldValue('hobby', getRandomItem(childHobbies));
            }
            setFieldValue('media_sns', "YouTube（子供向けチャンネル）");
        }
    }
};

// 高齢者関連の検証
const ElderlyValidation = {
    validate: function(ageInYears) {
        if (ageInYears >= 70) {
            const mediaSNS = getFieldValue('media_sns');
            const hobby = getFieldValue('hobby');
            
            // TikTokやInstagramは不自然
            if (mediaSNS && (mediaSNS.includes("TikTok") || mediaSNS.includes("Instagram"))) {
                const seniorMedia = ["テレビ", "新聞", "ラジオ", "YouTube", "LINE"];
                setFieldValue('media_sns', getRandomItem(seniorMedia));
            }
            
            // アクティブすぎる趣味を修正
            const activeHobbies = ["登山", "サーフィン", "ランニング", "筋トレ", "ダンス"];
            if (activeHobbies.some(h => hobby.includes(h))) {
                const seniorHobbies = ["散歩", "園芸", "読書", "囲碁・将棋", "カラオケ", "旅行"];
                setFieldValue('hobby', getRandomItem(seniorHobbies));
            }
        }
        
        // 定年退職者の矛盾チェック
        const occupation = getFieldValue('occupation');
        if (occupation === "定年退職者" || occupation === "年金受給者") {
            if (ageInYears < 60) {
                const appropriateOccupations = ["会社員", "自営業", "パート・アルバイト"];
                setFieldValue('occupation', getRandomItem(appropriateOccupations));
            }
            
            const family = getFieldValue('family');
            if (family && (family.includes("子どもが生まれたばかり") || family.includes("幼児の子ども"))) {
                setFieldValue('family', "成人の子どもがいる（18〜26歳）");
            }
        }
    }
};

// 家族・ライフイベント関連の検証
const FamilyLifeEventValidation = {
    validate: function(ageInYears) {
        const family = getFieldValue('family');
        const lifeEvent = getFieldValue('life_events');
        const gender = getFieldValue('gender');
        
        // 離婚・死別なのに幼い子供がいる矛盾を修正
        if ((family === "離婚" || family === "配偶者と死別") && 
            (family.includes("子どもが生まれたばかり") || family.includes("幼児の子ども"))) {
            const realisticFamilies = ["小学校低学年の子どもがいる（6〜8歳）", "中高生の子どもがいる（13〜17歳）", "独身"];
            setFieldValue('family', getRandomItem(realisticFamilies));
        }
        
        // 妊娠・出産関連の整合性チェック
        if (lifeEvent && lifeEvent.includes("妊娠")) {
            if (gender === "男性") {
                setFieldValue('life_events', "配偶者が妊娠中");
            }
            if (ageInYears < 18 || ageInYears > 50) {
                const ageAppropriateEvents = ["引っ越し", "転職", "新しい趣味を始めた"];
                setFieldValue('life_events', getRandomItem(ageAppropriateEvents));
            }
        }
    }
};

// 収入・職業関連の検証
const IncomeOccupationValidation = {
    validate: function() {
        const occupation = getFieldValue('occupation');
        const income = getFieldValue('income');
        
        // 年収と職業の不整合を追加チェック
        const lowIncomeOccupations = ["パート・アルバイト", "フリーター", "求職中", "年金受給者"];
        if (lowIncomeOccupations.includes(occupation)) {
            const incomeValue = parseInt(income.split('-')[0]);
            if (incomeValue > 400) {
                setFieldValue('income', getRandomItem(["<100", "100-200", "200-300", "300-400"]));
            }
        }
        
        // 性別と職業の現実的な分布
        const gender = getFieldValue('gender');
        if (gender === "男性" && occupation === "助産師") {
            const alternativeOccupations = ["看護師", "医療事務", "理学療法士"];
            setFieldValue('occupation', getRandomItem(alternativeOccupations));
        }
    }
};

// 趣味・ライフスタイル関連の検証
const HobbyLifestyleValidation = {
    validate: function(ageInYears) {
        const hobby = getFieldValue('hobby');
        const occupation = getFieldValue('occupation');
        const income = getFieldValue('income');
        const prefecture = getFieldValue('prefecture');
        
        // 職業と趣味の時間的整合性チェック
        const timeIntensiveOccupations = ["医師", "看護師", "経営者", "弁護士", "コンサルタント", "投資銀行"];
        const timeIntensiveHobbies = ["毎日ジム通い", "世界旅行", "複数の習い事", "ボランティア活動"];
        
        if (timeIntensiveOccupations.some(o => occupation.includes(o)) && 
            timeIntensiveHobbies.some(h => hobby.includes(h))) {
            const lightHobbies = ["読書", "映画鑑賞", "音楽鑑賞", "散歩", "料理"];
            setFieldValue('hobby', getRandomItem(lightHobbies));
        }
        
        // 収入と趣味のコスト整合性チェック
        const expensiveHobbies = ["ゴルフ", "ヨット", "乗馬", "海外旅行", "高級車", "ワインコレクション"];
        const incomeNum = parseInt(income.split('-')[0] || income.replace(/[^\d]/g, ''));
        
        if (incomeNum < 500 && expensiveHobbies.some(h => hobby.includes(h))) {
            const affordableHobbies = ["読書", "ジョギング", "料理", "映画鑑賞", "カフェ巡り"];
            setFieldValue('hobby', getRandomItem(affordableHobbies));
        }
        
        // 趣味と年齢・体力の整合性
        const physicallyDemandingHobbies = ["格闘技", "トライアスロン", "ロッククライミング", "パルクール"];
        if (physicallyDemandingHobbies.some(h => hobby.includes(h))) {
            if (ageInYears < 15 || ageInYears > 60) {
                const ageAppropriateHobbies = ageInYears < 15 ? 
                    ["読書", "ゲーム", "音楽鑑賞", "絵を描く"] : 
                    ["ウォーキング", "ガーデニング", "料理", "写真撮影"];
                setFieldValue('hobby', getRandomItem(ageAppropriateHobbies));
            }
        }
        
        // 地域と趣味の整合性チェック
        const urbanPrefectures = ["東京都", "大阪府", "神奈川県", "愛知県"];
        const urbanHobbies = ["美術館巡り", "ライブ参加", "カフェ巡り", "ショッピング"];
        
        if (!urbanPrefectures.includes(prefecture) && urbanHobbies.some(h => hobby.includes(h))) {
            const universalHobbies = ["読書", "料理", "ガーデニング", "ドライブ", "写真撮影"];
            setFieldValue('hobby', getRandomItem(universalHobbies));
        }
    }
};

// 健康・医療関連の検証
const HealthMedicalValidation = {
    validate: function(ageInYears) {
        const healthActions = getFieldValue('health_actions');
        const department = getFieldValue('department');
        const concerns = getFieldValue('concerns');
        const patientType = getFieldValue('patient_type');
        const holidayActivities = getFieldValue('holiday_activities');
        
        // 健康行動の年齢整合性チェック
        if (ageInYears < 30) {
            const seniorHealthActions = ["老眼鏡を作った", "補聴器を検討", "介護予防体操"];
            if (seniorHealthActions.some(action => healthActions.includes(action))) {
                const youngHealthActions = ["ジムに通い始めた", "食生活を見直した", "睡眠時間を確保するようにした"];
                setFieldValue('health_actions', getRandomItem(youngHealthActions));
            }
        }
        
        // 診療科と関心事の整合性チェック
        if (department && concerns) {
            const departmentConcernsMap = {
                "内科": ["胃痛", "頭痛", "疲労感", "風邪を引きやすい"],
                "整形外科": ["腰痛", "関節の痛み", "姿勢の悪さ", "運動不足"],
                "皮膚科": ["肌荒れ", "アトピー", "シミ・シワ", "日焼け"],
                "精神科": ["ストレス", "不眠", "気分の落ち込み", "不安感"],
                "眼科": ["視力低下", "目の疲れ", "ドライアイ", "老眼"],
                "歯科": ["虫歯", "歯周病", "歯並び", "口臭"]
            };
            
            if (departmentConcernsMap[department]) {
                const otherDepartmentConcerns = Object.entries(departmentConcernsMap)
                    .filter(([dept, _]) => dept !== department)
                    .flatMap(([_, concerns]) => concerns);
                
                if (otherDepartmentConcerns.some(c => concerns.includes(c))) {
                    setFieldValue('concerns', getRandomItem(departmentConcernsMap[department]));
                }
            }
        }
        
        // 患者タイプと行動の整合性チェック
        if (patientType && holidayActivities) {
            if (patientType === "利便性重視型" && 
                ["長時間の料理", "一日中読書", "終日ゴルフ"].some(a => holidayActivities.includes(a))) {
                const quickActivities = ["ネットサーフィン", "近所の散歩", "コンビニ巡り", "動画視聴"];
                setFieldValue('holiday_activities', getRandomItem(quickActivities));
            }
            
            if (patientType === "予防健康管理型" && 
                ["飲み歩き", "夜更かし", "ゲーム三昧", "暴飲暴食"].some(a => holidayActivities.includes(a))) {
                const healthyActivities = ["ジョギング", "ヨガ", "健康的な料理作り", "早朝散歩"];
                setFieldValue('holiday_activities', getRandomItem(healthyActivities));
            }
        }
    }
};

// 性格・価値観関連の検証
const PersonalityValidation = {
    validate: function(ageInYears) {
        const personality = getFieldValue('personality_keywords');
        const catchphrase = getFieldValue('catchphrase');
        const motto = getFieldValue('motto');
        const concerns = getFieldValue('concerns');
        
        // キャッチコピーと性格の整合性チェック
        if (personality && catchphrase) {
            const negativeTraits = ["心配性", "慎重", "内向的", "悲観的"];
            const positivePhases = ["いつも前向き", "超ポジティブ", "楽天家"];
            
            if (negativeTraits.some(t => personality.includes(t)) && 
                positivePhases.some(p => catchphrase.includes(p))) {
                const neutralPhrases = ["一歩一歩着実に", "慎重に判断", "じっくり考える"];
                setFieldValue('catchphrase', getRandomItem(neutralPhrases));
            }
        }
        
        // 座右の銘と性格の整合性
        if (personality && motto) {
            if (personality.includes("慎重") && motto && 
                ["一か八か", "やるかやられるか", "リスクを恐れるな"].some(m => motto.includes(m))) {
                const carefulMottos = ["石橋を叩いて渡る", "備えあれば憂いなし", "慎重第一"];
                setFieldValue('motto', getRandomItem(carefulMottos));
            }
        }
        
        // 悩み・関心事の年齢整合性チェック
        if (concerns) {
            if (ageInYears < 18) {
                const adultConcerns = ["老後の不安", "介護", "更年期", "資産運用", "相続"];
                if (adultConcerns.some(c => concerns.includes(c))) {
                    const childConcerns = ["進路", "友人関係", "勉強", "部活動", "将来の夢"];
                    setFieldValue('concerns', getRandomItem(childConcerns));
                }
            }
            
            if (ageInYears >= 65) {
                const youngConcerns = ["就活", "婚活", "キャリアアップ", "転職"];
                if (youngConcerns.some(c => concerns.includes(c))) {
                    const seniorConcerns = ["健康維持", "老後の生活", "孫の成長", "趣味の充実", "社会貢献"];
                    setFieldValue('concerns', getRandomItem(seniorConcerns));
                }
            }
        }
    }
};

// 地域関連の検証
const GeographicValidation = {
    validate: function() {
        const municipality = getFieldValue('municipality');
        const prefecture = getFieldValue('prefecture');
        const family = getFieldValue('family');
        
        // 都道府県と市区町村の整合性
        if (municipality && prefecture) {
            const tokyoWards = ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", 
                              "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", 
                              "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"];
            if (tokyoWards.includes(municipality) && prefecture !== "東京都") {
                setFieldValue('prefecture', "東京都");
            }
        }
        
        // 家族構成と住居の整合性
        if (family && municipality) {
            const downtownAreas = ["千代田区", "中央区", "港区", "渋谷区"];
            const largeFamilies = ["三世代同居", "子供3人以上", "大家族"];
            
            if (downtownAreas.includes(municipality) && 
                largeFamilies.some(f => family.includes(f))) {
                const smallFamilies = ["夫婦のみ", "子ども1人", "独身"];
                setFieldValue('family', getRandomItem(smallFamilies));
            }
        }
    }
};

// メインの検証関数
function validatePersonaConsistency() {
    const age = getFieldValue('age');
    const ageInYears = parseAge(age);
    
    // 各カテゴリの検証を実行
    StudentChildValidation.validate();
    ElderlyValidation.validate(ageInYears);
    FamilyLifeEventValidation.validate(ageInYears);
    IncomeOccupationValidation.validate();
    HobbyLifestyleValidation.validate(ageInYears);
    HealthMedicalValidation.validate(ageInYears);
    PersonalityValidation.validate(ageInYears);
    GeographicValidation.validate();
}

// エクスポート
window.PersonaValidation = {
    validatePersonaConsistency: validatePersonaConsistency
};