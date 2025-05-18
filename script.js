// --- Patient Type Descriptions (Store features and examples) ---
const patientTypeDetails = {
    '利便性重視型': { description: 'アクセスの良さ、待ち時間の短さ、診療時間の柔軟性など、便利さを最優先', example: '忙しいビジネスパーソン、オンライン診療を好む患者' },
    '専門医療追求型': { description: '専門医や高度専門医療機関での治療を希望し、医師の経歴や実績を重視', example: '難病患者、複雑な症状を持つ患者' },
    '予防健康管理型': { description: '病気になる前の予防や早期発見、健康維持に関心が高い', example: '定期健診を欠かさない人、予防接種に積極的な人' },
    '代替医療志向型': { description: '漢方、鍼灸、ホメオパシーなど、西洋医学以外の選択肢を積極的に取り入れる', example: '自然療法愛好者、慢性疾患の患者' },
    '経済合理型': { description: '自己負担額、保険適用の有無、費用対効果を重視', example: '経済的制約のある患者、医療費控除を意識する人' },
    '情報探求型': { description: '徹底的な情報収集、セカンドオピニオン取得、比較検討を行う', example: '高学歴層、慎重な意思決定を好む患者' },
    '革新技術指向型': { description: '最先端の医療技術、新薬、臨床試験などに積極的に関心を持つ', example: '既存治療で効果が出なかった患者、医療イノベーションに関心がある人' },
    '対話重視型': { description: '医師からの丁寧な説明や対話を求め、質問が多い', example: '不安を感じやすい患者、医療従事者' },
    '信頼基盤型': { description: 'かかりつけ医との長期的な関係や医療機関の評判を重視', example: '地域密着型の患者、同じ医師に長期通院する患者' },
    '緊急解決型': { description: '症状の即時改善を求め、緊急性を重視', example: '急性疾患患者、痛みに耐性が低い患者' },
    '受動依存型': { description: '医師の判断に全面的に依存し、自らの決定より医師の指示を優先', example: '高齢者、医療知識が少ない患者' },
    '自律決定型': { description: '自分の治療に主体的に関わり、最終決定権を持ちたいと考える', example: '医療リテラシーが高い患者、自己管理を好む慢性疾患患者' }
};

// --- Persona Fields Random Value Settings ---
// 候補値のリスト
const personaRandomValues = {
    names: {
        male: [
            "三浦 健吾", "大西 直樹", "石井 慎太", "木下 涼太", "長谷川 誠", "前田 洋介", "工藤 隼", "藤原 淳一", "今井 晃", "柴田 拓真", "竹内 優太", "安藤 陽介", 
            "上原 聡", "桑原 蓮", "橋本 悠真", "大島 亮", "樋口 大翔", "和田 晴人", "稲葉 海斗", "小池 晴翔", "関根 遼", "高田 隼人", "西村 陸", "田辺 駿佑", 
            "大塚 海人", "川島 裕翔", "宮崎 光", "新井 智也", "金子 啓太", "松永 翼", "浅野 俊輔", "水野 崇", "村田 快", "高山 篤", "佐川 蒼真", "藤本 怜", 
            "目黒 空", "青木 壮真", "堀内 蒼汰", "岡田 拓人", "山下 慎", "内田 直樹", "服部 陽斗", "河村 慧", "坂口 颯太", "小泉 元気", "横山 統也", "中原 洋", 
            "中田 真一", "庄司 光太", "吉川 湊多", "伊藤 奨", "野田 晴登", "福島 颯真", "星野 雅", "宮原 昂大", "高倉 渓太", "岡部 潤", "小嶋 蒼", "谷川 大樹"
        ],
        female: [
            "高橋 美優", "中村 千夏", "野口 陽菜", "河合 結月", "宮本 梨花", "松岡 彩音", "島田 真帆", "永井 咲良", "吉田 柚希", "井上 芽依", "原田 美月", "谷口 結衣", 
            "森 優菜", "村上 美桜", "小田 真央", "岡本 花恋", "白石 ひなた", "北川 澪", "黒田 結芽", "本田 瑞季", "藤川 桃子", "大谷 若菜", "岩田 心愛", "佐野 莉緒", 
            "広瀬 莉子", "小山 芽衣", "田島 望", "山川 栞", "中本 美空", "大森 佳奈", "古川 由奈", "浜田 千尋", "川口 美紅", "石田 詩織", "坂本 あかり", "長井 さくら", 
            "松本 愛莉", "赤坂 澪音", "藤沢 凛", "金井 碧", "土屋 陽", "今村 あい", "花田 小春", "関 彩華", "日高 心結", "和泉 瑞葉", "大庭 梨紗", "矢野 千聖", 
            "小林 瑠那", "富田 優香", "田所 美緒", "志村 日菜", "松井 愛子", "井口 沙羅", "西山 友里", "安達 柚葉", "河原 芽依", "八木 美琴", "山岡 千聖"
        ]
    },
    genders: ["male", "female"], // Added: Verify these values against your HTML's gender select options
    ages: [ // This list is now primarily for 0-year-old month variations
        "0y0m", "0y1m", "0y2m", "0y3m", "0y4m", "0y5m", "0y6m", "0y7m", "0y8m", "0y9m", "0y10m", "0y11m",
        // Full year entries from 1y to 100y are still useful as fallbacks or if needed elsewhere,
        // but getRandomAge will prioritize the new distribution.
        "1y", "2y", "3y", "4y", "5y", "6y", "7y", "8y", "9y", "10y", "11y", "12y", "13y", "14y", "15y",
        "16y", "17y", "18y", "19y", "20y", "21y", "22y", "23y", "24y", "25y", "26y", "27y", "28y", "29y",
        "30y", "31y", "32y", "33y", "34y", "35y", "36y", "37y", "38y", "39y", "40y", "41y", "42y", "43y",
        "44y", "45y", "46y", "47y", "48y", "49y", "50y", "51y", "52y", "53y", "54y", "55y", "56y", "57y",
        "58y", "59y", "60y", "61y", "62y", "63y", "64y", "65y", "66y", "67y", "68y", "69y", "70y", "71y",
        "72y", "73y", "74y", "75y", "76y", "77y", "78y", "79y", "80y", "81y", "82y", "83y", "84y", "85y",
        "86y", "87y", "88y", "89y", "90y", "91y", "92y", "93y", "94y", "95y", "96y", "97y", "98y", "99y", "100y"
    ],
    // Based on 令和５年（2023年）10月1日現在人口推計（総務省統計局）
    // 人口（千人）をそのままウェイトとして使用。合計約124,352千人。
    // 未成年者の選出確率を意図的に下げるため、19歳以下のweightを調整 (元の値の約7.5%に)
    ageDistributionWeights: [
        // 0歳児の月齢表現のため、0歳は特別扱い
        { ageGroup: "0y_months", weight: 54 },   // 元: 720 -> 216 -> 54
        { ageRange: "1-4y", weight: 224 },    // 元: 2989 -> 897 -> 224
        { ageRange: "5-9y", weight: 303 },    // 元: 4039 -> 1212 -> 303
        { ageRange: "10-14y", weight: 336 },   // 元: 4477 -> 1343 -> 336
        { ageRange: "15-19y", weight: 385 },   // 元: 5128 -> 1538 -> 385
        // 成人層のweightは未成年からの削減分を比例配分して増加
        { ageRange: "20-24y", weight: 6142 },  // 元: 5891
        { ageRange: "25-29y", weight: 6472 },  // 元: 6207
        { ageRange: "30-34y", weight: 6564 },  // 元: 6295
        { ageRange: "35-39y", weight: 6850 },  // 元: 6570
        { ageRange: "40-44y", weight: 7503 },  // 元: 7196
        { ageRange: "45-49y", weight: 8528 },  // 元: 8179
        { ageRange: "50-54y", weight: 10132 }, // 元: 9718
        { ageRange: "55-59y", weight: 7847 },  // 元: 7526
        { ageRange: "60-64y", weight: 7017 },  // 元: 6730
        { ageRange: "65-69y", weight: 7521 },  // 元: 7214
        { ageRange: "70-74y", weight: 8964 },  // 元: 8597
        { ageRange: "75-79y", weight: 7470 },  // 元: 7165
        { ageRange: "80-84y", weight: 5706 },  // 元: 5473
        { ageRange: "85-89y", weight: 4006 },  // 元: 3842
        { ageRange: "90-94y", weight: 2165 },  // 元: 2076
        { ageRange: "95-99y", weight: 797 },   // 元: 764
        { ageValue: "100y", weight: 163 }      // 元: 156
    ],
    prefectureCityPairs: [
        "北海道札幌市", "北海道函館市", "北海道旭川市", "北海道釧路市", "北海道帯広市",
        "青森県青森市", "青森県八戸市", "青森県弘前市",
        "岩手県盛岡市", "岩手県一関市", "岩手県花巻市",
        "宮城県仙台市", "宮城県石巻市", "宮城県大崎市",
        "秋田県秋田市", "秋田県横手市", "秋田県大仙市",
        "山形県山形市", "山形県鶴岡市", "山形県酒田市",
        "福島県福島市", "福島県郡山市", "福島県いわき市",
        "茨城県水戸市", "茨城県つくば市", "茨城県日立市",
        "栃木県宇都宮市", "栃木県小山市", "栃木県足利市",
        "群馬県前橋市", "群馬県高崎市", "群馬県太田市",
        "埼玉県さいたま市", "埼玉県川口市", "埼玉県川越市", "埼玉県所沢市",
        "千葉県千葉市", "千葉県船橋市", "千葉県柏市", "千葉県市川市",
        "東京都新宿区", "東京都渋谷区", "東京都世田谷区", "東京都練馬区", "東京都大田区", "東京都八王子市", "東京都町田市",
        "神奈川県横浜市", "神奈川県川崎市", "神奈川県相模原市", "神奈川県藤沢市", "神奈川県横須賀市",
        "新潟県新潟市", "新潟県長岡市", "新潟県上越市",
        "富山県富山市", "富山県高岡市",
        "石川県金沢市", "石川県白山市",
        "福井県福井市", "福井県坂井市",
        "山梨県甲府市", "山梨県富士吉田市",
        "長野県長野市", "長野県松本市", "長野県上田市",
        "岐阜県岐阜市", "岐阜県大垣市", "岐阜県各務原市",
        "静岡県静岡市", "静岡県浜松市", "静岡県富士市", "静岡県沼津市",
        "愛知県名古屋市", "愛知県豊田市", "愛知県岡崎市", "愛知県一宮市", "愛知県豊橋市",
        "三重県津市", "三重県四日市市", "三重県鈴鹿市",
        "滋賀県大津市", "滋賀県草津市", "滋賀県彦根市",
        "京都府京都市", "京都府宇治市", "京都府亀岡市",
        "大阪府大阪市", "大阪府堺市", "大阪府東大阪市", "大阪府吹田市", "大阪府高槻市",
        "兵庫県神戸市", "兵庫県姫路市", "兵庫県尼崎市", "兵庫県西宮市",
        "奈良県奈良市", "奈良県橿原市", "奈良県生駒市",
        "和歌山県和歌山市", "和歌山県田辺市",
        "鳥取県鳥取市", "鳥取県米子市",
        "島根県松江市", "島根県出雲市",
        "岡山県岡山市", "岡山県倉敷市", "岡山県津山市",
        "広島県広島市", "広島県福山市", "広島県呉市",
        "山口県山口市", "山口県下関市", "山口県宇部市",
        "徳島県徳島市", "徳島県阿南市",
        "香川県高松市", "香川県丸亀市",
        "愛媛県松山市", "愛媛県新居浜市", "愛媛県今治市",
        "高知県高知市", "高知県南国市",
        "福岡県福岡市", "福岡県北九州市", "福岡県久留米市", "福岡県飯塚市",
        "佐賀県佐賀市", "佐賀県唐津市",
        "長崎県長崎市", "長崎県佐世保市", "長崎県諫早市",
        "熊本県熊本市", "熊本県八代市",
        "大分県大分市", "大分県別府市",
        "宮崎県宮崎市", "宮崎県都城市",
        "鹿児島県鹿児島市", "鹿児島県霧島市", "鹿児島県鹿屋市",
        "沖縄県那覇市", "沖縄県沖縄市", "沖縄県うるま市"
    ],
    families: [
        "独身", "婚約中", "既婚", "新婚（3ヶ月未満）", "新婚（6ヶ月未満）", "新婚（1年未満）", 
        "子どもが生まれたばかり（0〜12ヶ月）", "幼児の子どもがいる（1〜2歳）", "子どもがいる（3〜5歳）", 
        "小学校低学年の子どもがいる（6〜8歳）", "小学校高学年の子どもがいる（9〜12歳）", 
        "中高生の子どもがいる（13〜17歳）", "成人の子どもがいる（18〜26歳）", 
        "配偶者と死別", "離婚", "別居中", "遠距離恋愛", "ドメスティックパートナー（事実婚）", 
        "オープンな関係", "シビルユニオン（法的パートナーシップ）", "複雑な関係", 
        "両親がいる", "母子家庭", "父子家庭"
    ],
    occupations: [
        "未就学児", "幼稚園児", "保育園児", "小学生", "中学生", "高校生", "大学生", "大学院生", "専門学校生", "浪人生", 
        "求職中", "就職活動中", "インターンシップ中", "契約社員", "派遣社員", "パートタイム勤務", "アルバイト", 
        "フリーランス", "自営業主", "個人事業主", "会社経営者", "会社役員", "会社員（総合職）", "会社員（一般職）", 
        "会社員（専門職）", "会社員（技術職）", "会社員（研究職）", "会社員（企画・マーケティング職）", 
        "会社員（営業職）", "会社員（事務職）", "会社員（クリエイティブ職）", "公務員（国家）", "公務員（地方）", 
        "教員・教師（小学校）", "教員・教師（中学校）", "教員・教師（高校）", "教員・教師（大学）", "教員・教師（専門学校）", 
        "保育士", "医師", "歯科医師", "薬剤師", "看護師", "保健師", "助産師", "理学療法士", "作業療法士", "言語聴覚士", 
        "介護福祉士", "社会福祉士", "精神保健福祉士", "栄養士・管理栄養士", "調理師", "美容師", "理容師", "エステティシャン", 
        "ネイリスト", "アイリスト", "整体師・セラピスト", "スポーツインストラクター", "アスリート", "芸術家・アーティスト", 
        "音楽家・ミュージシャン", "俳優・タレント", "声優", "モデル", "デザイナー（グラフィック）", "デザイナー（ウェブ）", 
        "デザイナー（ファッション）", "デザイナー（プロダクト）", "建築家・設計士", "インテリアコーディネーター", "イラストレーター", 
        "漫画家", "アニメーター", "ゲームクリエイター", "プログラマー", "システムエンジニア", "ITコンサルタント", 
        "データサイエンティスト", "ウェブマーケター", "編集者・ライター", "ジャーナリスト", "カメラマン", "翻訳家・通訳者", 
        "弁護士", "弁理士", "司法書士", "行政書士", "税理士", "公認会計士", "不動産鑑定士", "コンサルタント（経営）", 
        "コンサルタント（IT）", "コンサルタント（その他専門）", "金融関連専門職", "不動産関連専門職", "MR（医薬情報担当者）", 
        "臨床開発モニター", "農業従事者", "林業従事者", "漁業従事者", "酪農家", "伝統工芸士", "職人（建設・建築系）", 
        "職人（製造・機械系）", "職人（その他）", "パイロット", "客室乗務員", "鉄道運転士", "バス運転手", "タクシー運転手", 
        "トラック運転手", "船舶乗組員", "警備員", "消防士", "警察官", "自衛官", "宗教家", "政治家", "学者・研究者", 
        "図書館司書", "学芸員", "カウンセラー", "キャリアコンサルタント", "ファイナンシャルプランナー", "秘書", 
        "受付", "コールセンター勤務", "工場勤務", "建設作業員", "清掃員", "配達員", "警備員", "店舗スタッフ（販売）", 
        "店舗スタッフ（飲食）", "ホテルスタッフ", "旅行代理店スタッフ", "アミューズメント施設スタッフ", "専業主婦・主夫", 
        "家事手伝い", "定年退職者", "年金受給者", "不労所得者", "投資家", "その他"
    ],
    hobbies: [
        // エンターテイメント
        "音楽", "映画", "読書", "テレビ", "ラジオ", "ポッドキャスト", "アニメ", "漫画", "ゲーム", "舞台鑑賞（演劇、ミュージカル、オペラ、バレエ）", "コンサート・ライブ", "美術鑑賞（美術館、ギャラリー）", "博物館", "プラネタリウム", "動物園", "水族館", "テーマパーク", "遊園地", "花火", "祭り・イベント参加", "謎解きゲーム・脱出ゲーム",
        // スポーツ・アウトドア
        "スポーツ観戦", "ウォーキング", "ジョギング・ランニング", "サイクリング", "ハイキング・登山", "キャンプ", "釣り", "サーフィン", "ダイビング・シュノーケリング", "スキー・スノーボード", "スケート", "水泳", "ヨガ・ピラティス", "ダンス", "ゴルフ", "テニス", "バドミントン", "卓球", "野球", "サッカー・フットサル", "バスケットボール", "バレーボール", "武道（剣道、柔道、空手、合気道など）", "ボルダリング・クライミング", "フィットネス・筋トレ", "モータースポーツ", "ラフティング", "カヌー・カヤック", "バードウォッチング",
        // 旅行・乗り物
        "国内旅行", "海外旅行", "温泉巡り", "神社仏閣巡り", "城巡り", "聖地巡礼", "ドライブ", "ツーリング（バイク）", "鉄道旅行・撮り鉄", "飛行機・空港好き", "船旅",
        // ものづくり・創作
        "料理", "お菓子作り", "パン作り", "手芸（編み物、刺繍、裁縫など）", "DIY・日曜大工", "ガーデニング・家庭菜園", "盆栽", "華道", "書道", "茶道", "陶芸", "絵画", "イラスト", "写真撮影", "ビデオ編集・動画制作", "プログラミング", "電子工作", "プラモデル・模型作り", "アクセサリー作り", "レザークラフト", "キャンドル作り", "石鹸作り", "書道", "俳句・短歌", "小説執筆", "ブログ・SNS投稿", "作詞・作曲", "楽器演奏",
        // 収集・コレクション
        "切手収集", "コイン収集", "アンティーク収集", "フィギュア収集", "トレーディングカード収集", "スニーカー収集", "時計収集", "レコード収集", "古書収集", "美術品収集", "ワイン収集", "日本酒・焼酎収集", "香水収集",
        // 学習・自己啓発
        "語学学習", "資格取得", "セミナー・講演会参加", "オンライン学習", "プログラミング学習", "投資・資産運用", "歴史研究", "哲学・思想", "科学・宇宙", "自己啓発本の読書",
        // グルメ
        "食べ歩き", "カフェ巡り", "ラーメン巡り", "パン屋巡り", "スイーツ巡り", "お酒（日本酒、ワイン、ビール、ウイスキーなど）", "コーヒー・紅茶", "料理教室通い",
        // ファッション・美容
        "ファッション", "ショッピング", "コスメ・美容", "ネイルアート", "ヘアアレンジ", "エステ",
        // ゲーム（詳細）
        "テレビゲーム・コンシューマーゲーム", "PCゲーム", "スマートフォンゲーム", "ボードゲーム", "カードゲーム", "テーブルトークRPG", "オンラインゲーム", "eスポーツ観戦",
        // その他
        "ボランティア活動", "地域活動", "占い・スピリチュアル", "瞑想・マインドフルネス", "アロマテラピー", "ペット（犬、猫など）の世話", "熱帯魚・アクアリウム", "天体観測", "カラオケ", "ダーツ", "ビリヤード", "パチンコ・パチスロ", "競馬・競輪・競艇", "麻雀", "献血", "フリーマーケット出店・参加", "ネットサーフィン", "SNSチェック", "ポイント活動・ポイ活", "懸賞応募", "昼寝", "人間観察"
    ],
    life_events: [
        "婚約中（1年未満）", "婚約中（6ヶ月未満）", "婚約中（3ヶ月未満）",
        "新しい交際関係", "最近転居した", "最近引っ越しした人の友達",
        "出身地から離れた所に住んでいる", "家族から離れた所に住んでいる",
        "就職・転職", "近日中に誕生日を迎える",
        "1ヶ月以内に誕生日を迎える人の友達", "1週間以内に誕生日を迎える人の友達",
        "7日以内に誕生日を迎える女性の友達", "7日以内に誕生日を迎える男性の友達",
        "7〜30日後に誕生日を迎える女性の友達", "7〜30日後に誕生日を迎える男性の友達",
        "30日以内に記念日がある人", "31〜60日以内に記念日がある人"
    ],
    incomeRanges: [ // HTMLのselect#incomeのvalue値を設定
        "<100", "100-200", "200-300", "300-400", "400-500", "500-600", "600-700", "700-800", "800-900", "900-1000",
        "1000-1100", "1100-1200", "1200-1300", "1300-1400", "1400-1500", "1500-1600", "1600-1700", "1700-1800", "1800-1900", "1900-2000",
        "2000-2100", "2100-2200", "2200-2300", "2300-2400", "2400-2500", "2500-2600", "2600-2700", "2700-2800", "2800-2900", "2900-3000",
        "3000-3100", "3100-3200", "3200-3300", "3300-3400", "3400-3500", "3500-3600", "3600-3700", "3700-3800", "3800-3900", "3900-4000",
        "4000-4100", "4100-4200", "4200-4300", "4300-4400", "4400-4500", "4500-4600", "4600-4700", "4700-4800", "4800-4900", "4900-5000",
        "5000-5100", "5100-5200", "5200-5300", "5300-5400", "5400-5500", "5500-5600", "5600-5700", "5700-5800", "5800-5900", "5900-6000",
        "6000-6100", "6100-6200", "6200-6300", "6300-6400", "6400-6500", "6500-6600", "6600-6700", "6700-6800", "6800-6900", "6900-7000",
        "7000-7100", "7100-7200", "7200-7300", "7300-7400", "7400-7500", "7500-7600", "7600-7700", "7700-7800", "7800-7900", "7900-8000",
        "8000-8100", "8100-8200", "8200-8300", "8300-8400", "8400-8500", "8500-8600", "8600-8700", "8700-8800", "8800-8900", "8900-9000",
        "9000-9100", "9100-9200", "9200-9300", "9300-9400", "9400-9500", "9500-9600", "9600-9700", "9700-9800", "9800-9900", "9900-10000",
        ">=10000"
    ],
    motto: ["一期一会", "継続は力なり", "笑う門には福来る", "人生一度きり", "石の上にも三年", "初心忘るべからず", "良薬は口に苦し", "急がば回れ", "歓びを分かち合えば二倍に、悲しみを分かち合えば半分に", "七転び八起き", "明日は明日の風が吹く", "時は金なり", "備えあれば憂いなし", "為せば成る、為さねば成らぬ",
        // 子供向けの座右の銘を追加
        "笑顔が一番", "友達大事", "楽しく遊ぶ", "元気が一番", "一生懸命", "あきらめない", "ありがとう", "順番を守る", "助け合い", "約束を守る", "正直に話す", "チャレンジする", "何でも挑戦", "明るく元気に",
        // 若者向けの座右の銘を追加
        "挑戦なくして成長なし", "今を生きる", "自分らしさを大切に", "失敗は成功のもと", "今日できることは今日する", "可能性は無限大", "苦労は買ってでもしろ", "若いうちの苦労は買ってでもしろ", "正解よりも納得", "夢見る力は無限大", "青春に悔いなし", "やると決めたらやりきる", "努力は裏切らない", "一意専心", "他人と比べず自分と向き合う",
        // 大人向けの座右の銘を追加
        "一期一会", "塞翁が馬", "初心忘るべからず", "己を知る者は強し", "千里の道も一歩から", "思い立ったが吉日", "好機逸すべからず", "臥薪嘗胆", "精神一到何事か成らざらん", "小事を積み重ね大事とす", "謙虚なれど卑屈ならず", "機を見るに敏", "過ぎたるは猶及ばざるが如し", "賢者は歴史に学ぶ", "和を以て貴しとなす",
        // 高齢者向けの座右の銘を追加
        "老いてなお学べば死して朽ちず", "温故知新", "楽あれば苦あり、苦あれば楽あり", "堪忍は一生の宝", "日日是好日", "今日一日", "往生際の良さ", "歳月人を待たず", "老いは客人のごとく", "過ぎ去りし日々に感謝", "諦観", "心淡くして味厚し", "身軽に生きる", "山高ければ谷深し", "無心", "枯れて花あり"
    ],
    concerns: ["健康維持", "体重管理", "ストレス対策", "睡眠の質向上", "健康診断の結果", "歯の治療", "視力低下", "老眼", "肩こり腰痛", "アレルギー症状", "花粉症対策", "疲れやすさ", "免疫力向上", "生活習慣病予防", "メンタルケア", "認知症予防", "家族の健康",
        // 子供向けの悩み・関心を追加
        "お友達との関係", "勉強", "好きな遊び", "好きな食べ物", "テレビアニメ", "習い事", "新しいおもちゃ", "幼稚園・保育園での活動", "折り紙が上手くできない", "お絵かき", "絵本", "ヒーローに憧れる", "楽器の練習", "水泳教室", "運動会の練習", "先生とのコミュニケーション", "身長が伸びるか",
        // 若者向けの悩み・関心を追加
        "学校生活", "勉強の成績", "将来の進路", "友人関係", "恋愛", "ファッション", "SNSの使い方", "スマホ依存", "受験勉強", "部活動の成績", "ダイエット", "身長", "コンプレックス", "人気者になりたい", "ゲームの上達", "アイドル追っかけ", "大学受験", "推しの活動", "親との関係", "塾・予備校", "おこづかい", "アルバイト", 
        // 大人向けの悩み・関心を追加
        "キャリアアップ", "副業", "住宅ローン", "資産運用", "子育て", "パートナーとの関係", "ワークライフバランス", "転職", "残業", "上司との関係", "出世", "保険の見直し", "貯金", "マイホーム購入", "車の維持費", "教育費", "老後資金", "職場のハラスメント", "株式投資", "仮想通貨", "趣味の時間確保", "睡眠不足", "飲み会の付き合い", "親の介護", "夫婦生活", "育児ストレス",
        // 高齢者向けの悩み・関心を追加
        "老後の生活", "年金", "健康維持", "介護問題", "終活", "趣味の時間", "子や孫との関係", "遺産相続", "後見人制度", "認知症の不安", "病院通い", "一人暮らしの不安", "老人ホーム入居", "友人との別れ", "足腰の衰え", "物忘れ", "生きがい探し", "地域活動への参加", "高齢者詐欺への不安", "デジタル機器の使い方", "運転免許返納の悩み", "医療費"
    ],
    favorite_person: ["松任谷由実", "安室奈美恵", "木村拓哉", "北野武", "山崎賢人", "綾瀬はるか", "本田圭佑", "石原さとみ", "西島秀俊", "天海祐希", "松本人志", "草彅剛", "星野源", "米津玄師", "浜崎あゆみ", "宮沢りえ", "新垣結衣", "福山雅治", "イチロー", "桑田佳祐", "吉岡里帆", "矢沢永吉", "YOASOBI",
        // 子供向けの人物・キャラクターを追加
        "アンパンマン", "ドラえもん", "クレヨンしんちゃん", "ポケモンのキャラクター", "プリキュア", "鬼滅の刃のキャラクター", "すみっコぐらし", "ミッキーマウス", "しまじろう", "いないいないばあっ！のワンワン", "おかあさんといっしょの体操のお兄さん", "戦隊ヒーロー", "仮面ライダー", "ウルトラマン", "となりのトトロ", "魔女の宅急便のキキ", "ピカチュウ", "トーマス", "おじゃる丸", "子供向けYouTuber",
        // 若者向けの人物を追加
        "King Gnu", "あいみょん", "Official髭男dism", "キングヌー", "ユーチューバー", "若手アイドル", "アニメキャラクター", "藤井聡太", "NiziU", "BTS", "SnowMan", "櫻坂46", "乃木坂46", "バスケ選手", "サッカー選手", "Vtuber", "TikToker", "竹内涼真", "浜辺美波", "Ado", "平手友梨奈", "佐藤健", "森七菜", "中村倫也", "小松菜奈", "菅田将暉", "伊藤沙莉",
        // 大人向けの人物を追加
        "阿部寛", "長澤まさみ", "深津絵里", "ビートたけし", "明石家さんま", "タモリ", "松本人志", "小泉今日子", "綾野剛", "松たか子", "草刈正雄", "柴咲コウ", "松嶋菜々子", "堺雅人", "高嶋政宏", "斎藤工", "妻夫木聡", "宮沢りえ", "松坂桃李", "戸田恵梨香", "クリント・イーストウッド", "山本耕史", "向井理", "吉永小百合", "スティーブン・スピルバーグ", "トム・クルーズ", "メリル・ストリープ",
        // 高齢者向けの人物を追加
        "美空ひばり", "加山雄三", "石原裕次郎", "中村勘三郎", "淡島千景", "渥美清", "山田洋次", "黒柳徹子", "森繁久彌", "藤山寛美", "植木等", "浜村淳", "中村玉緒", "司葉子", "伊東四朗", "大滝秀治", "宮本信子", "倍賞千恵子", "菅原文太", "三船敏郎", "高倉健", "山口百恵", "森光子", "渡哲也", "西田敏行", "加藤剛", "伊丹十三", "井上ひさし", "沢村貞子", "水前寺清子"
    ],
    media_sns: ["YouTube", "Twitter", "Instagram", "Facebook", "TikTok", "LINE", "テレビ", "新聞", "雑誌", "ラジオ", "Podcast", "ABEMA", "Netflix", "Hulu", "Amazon Prime", "ニュースアプリ", "Yahoo!ニュース", "SmartNews", "NHK", "地上波テレビ",
        // 子供向けのメディアを追加
        "子供向けアプリ", "子供向けYouTubeチャンネル", "教育番組", "子供向けテレビ番組", "絵本", "幼児向けタブレット", "Eテレ", "キッズチューブ", "子供向け漫画雑誌", "キッズ向けサブスク", "どうぶつの森", "マインクラフト", "子供向けDVD", "子供向け映画", "キッズウィークリー",
        // 若者向けのメディアを追加
        "Discord", "Twitch", "TikTok", "Spotify", "音楽配信サービス", "オンラインゲーム", "アニメ配信サービス", "X（旧Twitter）", "YouTube Premium", "Threads", "BeReal", "Pococha", "ニコニコ動画", "pixiv", "note", "Pinterest", "Reddit", "Tinder", "マッチングアプリ", "ゲーム攻略サイト", "二次元キャラSNS", "漫画アプリ", "WebToon", "17Live",
        // 大人向けのメディアを追加
        "ビジネス雑誌", "経済ニュース", "専門誌", "Kindle", "オーディオブック", "ポッドキャスト", "日経新聞", "東洋経済", "プレジデント", "Clubhouse", "ビジネスSNS", "LinkedIn", "ブルームバーグ", "The Wall Street Journal", "Forbes JAPAN", "Diamond Online", "大人向けYouTubeチャンネル", "教養番組", "グルメ情報サイト", "Audible", "楽天マガジン", "d マガジン", "dポイントクラブ", "PayPayポイント", "楽天ポイント", "株価アプリ",
        // 高齢者向けのメディアを追加
        "地域新聞", "シニア向け雑誌", "ラジオ講座", "趣味の専門誌", "朝の情報番組", "NHK連続テレビ小説", "大河ドラマ", "シニア向け情報サイト", "健康情報誌", "郷土史雑誌", "旅番組", "美術展情報", "地方自治体の広報誌", "シルバー人材センター情報誌", "文化センター会報", "老人クラブ会報", "生涯学習情報", "終活セミナー情報", "ラジオ深夜便", "高齢者向けタブレット教室"
    ],
    personality: ["明るい", "穏やか", "几帳面", "社交的", "慎重", "好奇心旺盛", "忍耐強い", "論理的", "感情的", "気配り上手", "思いやりがある", "決断力がある", "協調性がある", "独立心がある", "冒険好き", "保守的", "内向的", "外交的", "直感的", "計画的", "柔軟", "頑固", "真面目", "楽観的", "悲観的", "慎み深い", "大胆", "繊細", "丁寧", "雑", "勤勉", "温厚", "情熱的", "落ち着いている",
        // 追加のパーソナリティー特性
        "創造的", "分析的", "熱心", "謙虚", "負けず嫌い", "粘り強い", "自己主張が強い", "寛容", "慎重", "細部にこだわる", "ユーモアがある", "リーダーシップがある", "感受性が強い", "責任感がある", "誠実", "大胆不敵", "控えめ", "表現力がある", "自制心がある", "冷静沈着", "行動力がある", "聞き上手", "配慮が細やか", "臨機応変", "勇気がある", "実直", "世話好き", "理想主義", "現実主義", "感謝の気持ちを持つ", "気前がいい", "親しみやすい", "几帳面", "物事を深く考える", "決めたことはやり遂げる", "平和主義", "ポジティブ思考", "クリエイティブ", "堅実", "野心的", "効率重視", "規律正しい", "完璧主義"
    ],
    health_actions: ["健康診断を受けた", "歯医者で検診を受けた", "ウォーキングを始めた", "ジムに通い始めた", "食生活を見直した", "サプリメントを飲み始めた", "禁煙した", "節酒した", "睡眠時間を増やした", "体重計に毎日乗るようにした", "血圧を測るようにした", "オンライン診療を利用した", "定期的に薬を飲み始めた", "マスクを常時着用している", "アルコール消毒を徹底している", "ストレッチを日課にした", "瞑想を始めた", "新しい運動を始めた",
        // 子供向けの健康行動を追加
        "手洗いうがいを心がけている", "早寝早起きを心がけている", "栄養バランスの良い食事を食べている", "外で遊ぶようにしている", "正しい姿勢で座る練習をしている", "歯磨きを丁寧にしている", "好き嫌いなく食べる練習をしている", "虫歯予防のフッ素塗布をした", "スポーツ少年団に入った", "水泳教室に通い始めた", "目の健康のためスクリーンタイムを減らした", "定期的に身長体重を測っている", "朝食をしっかり食べるようにしている", "アレルギー検査を受けた", "姿勢を正しくする練習をしている", "家族と一緒に体操している",
        // 若者向けの健康行動を追加
        "スポーツを定期的に行っている", "ダイエットを始めた", "SNS利用時間を制限した", "スクリーンタイムを減らした", "姿勢改善のためのストレッチをしている", "プロテインを飲み始めた", "筋トレを始めた", "ヨガを始めた", "ランニングを始めた", "断食に挑戦した", "腸活を始めた", "ヘルシーな外食を選ぶようになった", "ファスティングに挑戦した", "半身浴を習慣にした", "姿勢矯正グッズを使い始めた", "青汁を飲み始めた", "ピラティスを始めた", "部活動を頑張っている", "目の疲れ対策をしている", "視力検査を受けた",
        // 大人向けの健康行動を追加
        "完全禁煙した", "アルコール摂取量を減らした", "定期的な筋トレを始めた", "腸活を意識した食事をしている", "休息時間を意識的に取っている", "フィットネスバンドで活動量を計測し始めた", "有酸素運動を週3回行うようになった", "ローカーボダイエットを始めた", "プチ断食に挑戦した", "テレワークでの姿勢改善に取り組んでいる", "立ち仕事の割合を増やした", "通勤を自転車に変えた", "糖質制限を始めた", "オーガニック食品を取り入れた", "ビタミンDのサプリを摂り始めた", "職場の健康プログラムに参加した", "メンタルヘルスケアを始めた", "人間ドックを受けた", "ストレス管理のためのアプリを使い始めた", "食事の写真を撮って栄養管理している", "睡眠の質を測定するアプリを使い始めた",
        // 高齢者向けの健康行動を追加
        "定期的な病院の通院", "介護予防体操", "血圧測定", "バランスの良い食事", "水分摂取を心がけている", "老眼鏡を作った", "シルバー体操教室に参加", "認知症予防のパズルを解いている", "転倒防止のための家の改修", "杖を使い始めた", "聴力検査を受けた", "補聴器を使い始めた", "フレイル予防に取り組んでいる", "口腔ケアを徹底している", "歩行補助具を使い始めた", "健康体操のDVDを見ながら運動している", "骨密度検査を受けた", "カルシウムのサプリを飲み始めた", "緑内障検査を受けた", "高齢者サロンに参加し始めた", "温泉療法を取り入れた", "通所リハビリに通い始めた", "服薬管理アプリを使い始めた", "お薬手帳を活用している"
    ],
    holiday_activities: ["家でゆっくり過ごす", "映画を見る", "買い物に行く", "友人と会う", "家族で出かける", "趣味に没頭する", "掃除や整理整頓", "料理をする", "スポーツをする", "自然の中で過ごす", "カフェでくつろぐ", "温泉に行く", "ドライブに行く", "読書をする", "寝だめをする", "テレビを見る", "SNSをチェックする", "ゲームをする", "公園を散歩する", "博物館や美術館に行く",
        // 子供向けの休日の過ごし方を追加
        "公園で遊ぶ", "おもちゃで遊ぶ", "友達と遊ぶ", "プラモデルを作る", "ゲームセンターに行く", "映画館で子供向け映画を見る", "キャラクターショーに行く", "遊園地に行く", "水族館に行く", "動物園に行く", "プールに行く", "アスレチックで遊ぶ", "お絵かきをする", "折り紙をする", "粘土遊びをする", "ブロック遊び", "カードゲームで遊ぶ", "科学館に行く", "キッズスペースで遊ぶ", "ピクニックに行く", "昆虫採集", "お菓子作り体験", "キッズダンス教室",
        // 若者向けの休日の過ごし方を追加
        "カラオケに行く", "ショッピングモールで買い物", "ゲームをする", "動画配信を見る", "友達とカフェでおしゃべり", "部活動", "ダンス練習", "バンド練習", "ライブに行く", "推しのイベントに参加", "アニメイベントに参加", "コミケに行く", "ゲームセンター", "ネットカフェ", "コスプレをする", "写真撮影", "メイク研究", "SNSの投稿を作る", "ネットショッピング", "アイドルのライブ配信を見る", "フェスに行く", "スケボーをする", "パルクール", "BMX", "サーフィン", "スノーボード", "スケート", "ダンスゲーム",
        // 大人向けの休日の過ごし方を追加
        "ワイン選び", "ガーデニング", "DIY", "資格勉強", "投資の勉強", "ホームパーティー", "副業", "家計管理", "株取引", "クレジットカードの整理", "保険の見直し", "不動産投資の勉強", "転職活動", "飲み会", "合コン", "相席居酒屋", "婚活パーティー", "高級レストラン", "子供の習い事の送迎", "フリーマーケット出店", "メルカリ出品", "ボランティア活動", "地域のイベント参加", "PTA活動", "子供の運動会", "職場の飲み会", "同窓会", "ゴルフ", "ランニング", "サイクリング", "海外旅行計画", "ビジネス書を読む", "キャンプ", "釣り", "アウトドア",
        // 高齢者向けの休日の過ごし方を追加
        "近所の散歩", "孫と過ごす", "地域の集まりに参加", "囲碁・将棋", "園芸", "昔のアルバムを見る", "俳句の会", "老人クラブ活動", "温泉旅行", "デイサービス", "生涯学習講座", "書道教室", "陶芸教室", "民謡教室", "グラウンドゴルフ", "太極拳", "ラジオ体操", "健康マージャン", "ゲートボール", "ウォーキング仲間との交流", "昔の友人と会う", "医療講演会に参加", "健康相談会", "お墓参り", "寺社参拝", "日帰りバスツアー", "同窓会", "カラオケ喫茶", "地域の清掃活動", "花壇の手入れ", "近所の子供たちとの交流", "伝統工芸教室", "昔話の語り部"
    ],
    catchphrase: ["健康第一、笑顔で毎日", "丁寧な暮らしで心も体も健やかに", "自分らしく健やかに生きる", "家族の笑顔が私の元気の源", "一歩一歩、着実に前へ", "穏やかな日常に感謝して", "毎日を大切に生きる", "夢を追い求める情熱が私を動かす", "心と体のバランスが一番", "今日より明日はもっと良くなる", "小さな幸せを見つける目を持つ", "転んでも前を向いて歩き続ける", "チャレンジする勇気を忘れない", "いつも前向きに考える", "細く長く、自分のペースで",
        // 子供向けのキャッチフレーズを追加
        "笑顔いっぱい元気いっぱい", "友達と仲良く", "元気が一番", "いつも楽しく", "好奇心いっぱい", "すくすく成長中", "おともだちと楽しく遊ぶ", "いつも笑顔でキラキラ", "元気いっぱい冒険中", "のびのび育つよ", "わくわくドキドキ大好き", "すくすく伸びる若葉のように", "みんなで一緒に楽しいね", "おしゃべり大好き冒険隊", "好奇心いっぱいワクワク毎日", "お友達大好き", "いつも挑戦！恐れない！", "今日も元気！明日も元気！", "遊びが大好き！",
        // 若者向けのキャッチフレーズを追加
        "自分のスタイルを貫く", "常に新しいことにチャレンジ", "限界を決めるのは自分", "今日も自分らしく", "夢を諦めない", "常に上を目指す", "今を全力で生きる", "自分の道は自分で切り開く", "失敗を恐れず前へ進む", "トレンドの最先端", "SNSでバズる生き方", "チャンスを掴む力", "可能性は無限大", "今が青春", "いつだって主役は自分", "個性輝く瞬間", "最高の自分になる", "いつも自分らしく輝く", "何にでもチャレンジ", "自分磨きを怠らない", "自由に生きる自由な魂", "青春を全力で駆け抜ける",
        // 大人向けのキャッチフレーズを追加
        "バランスのとれた生活が健康の秘訣", "人生は学びの連続", "今日という日を大切に", "仕事も家庭も充実した毎日", "自分の時間も大切に", "小さな幸せの積み重ね", "明日の自分に投資する", "健康でいることが一番の贅沢", "ストレスとうまく付き合う", "責任ある選択", "未来を見据えた行動", "家族との時間が宝物", "経験が自分を作る", "日々の努力こそが成功の鍵", "心にゆとりを持つ毎日", "丁寧に生きる", "感謝の気持ちを忘れない", "日々の小さな選択が人生を作る", "物事の優先順位を大切に", "ワークライフバランスを意識",
        // 高齢者向けのキャッチフレーズを追加
        "健康寿命を延ばす毎日の工夫", "年齢は数字に過ぎない", "できることを少しずつ", "日々感謝", "人生の知恵を次世代へ", "穏やかな日々に感謝", "老いることは学ぶこと", "培った知恵を活かす", "静かな喜びを味わう日々", "いつまでも好奇心を持ち続ける", "人生経験が私の宝物", "ゆっくりと確実に", "昔を懐かしみ今を生きる", "笑顔で過ごす穏やかな日々", "一期一会の精神で", "新しいことに挑戦し続ける", "日々の小さな幸せを大切に", "家族の健康が一番の願い", "自分のペースを大切に", "できることから無理なく", "心穏やかに日々過ごす", "人生の実りの季節を楽しむ", "培った知恵を次の世代へ"
    ]
};

// --- Helper Functions for Random Values ---
function getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

// Function to get a random name based on gender
function getRandomName(gender) {
    console.log("getRandomName called with gender:", gender);
    // Ensure personaRandomValues.genders is defined and has entries before using it in comparisons
    const maleGenders = ["male"]; // Default to "male"
    const femaleGenders = ["female"]; // Default to "female"
    if (personaRandomValues.genders && personaRandomValues.genders.length > 0) {
        maleGenders.push(personaRandomValues.genders[0]);
        if (personaRandomValues.genders.length > 1) {
            femaleGenders.push(personaRandomValues.genders[1]);
        }
    }

    if (maleGenders.includes(gender) && personaRandomValues.names.male && personaRandomValues.names.male.length > 0) {
        return getRandomItem(personaRandomValues.names.male);
    } else if (femaleGenders.includes(gender) && personaRandomValues.names.female && personaRandomValues.names.female.length > 0) {
        return getRandomItem(personaRandomValues.names.female);
    } else {
        // Fallback: pick from either male or female if gender is unknown, not explicitly "male"/"female", or lists are empty
        console.log("getRandomName: Gender not matched or name list empty, using fallback.");
        const allNames = [...(personaRandomValues.names.male || []), ...(personaRandomValues.names.female || [])];
        if (allNames.length > 0) {
            return getRandomItem(allNames);
        }
        return "名無し"; // Absolute fallback
    }
}

// ランダム年齢取得関数を修正し、固定リストを使うように変更
// function getRandomAge() {
//     // 固定リストから年齢をランダムに選択
//     return getRandomItem(personaRandomValues.ages);
// }
// New getRandomAge function using weighted distribution
function getRandomAge() {
    const weights = personaRandomValues.ageDistributionWeights;
    const totalWeight = weights.reduce((sum, item) => sum + item.weight, 0);
    let randomNum = Math.random() * totalWeight;

    for (const item of weights) {
        if (randomNum < item.weight) {
            if (item.ageGroup === "0y_months") {
                // Select a random month for 0-year-olds
                const zeroYearMonthAges = personaRandomValues.ages.filter(age => age.startsWith("0y") && age.includes("m"));
                return getRandomItem(zeroYearMonthAges);
            } else if (item.ageRange) {
                const [startStr, endStrFull] = item.ageRange.split('-');
                const start = parseInt(startStr);
                const end = parseInt(endStrFull.replace('y', ''));
                const randomYear = Math.floor(Math.random() * (end - start + 1)) + start;
                return `${randomYear}y`;
            } else if (item.ageValue) { // For single age values like "100y"
                return item.ageValue;
            }
        }
        randomNum -= item.weight;
    }
    // Fallback (should ideally not be reached if weights are comprehensive)
    console.warn("getRandomAge fallback: Could not select age from weighted distribution. Defaulting to old method.");
    return getRandomItem(personaRandomValues.ages.filter(age => !age.includes("m") || age.startsWith("0y"))); // Prefer full years or 0yXm
}

function getRandomPrefectureAndMunicipality() {
    const pairString = getRandomItem(personaRandomValues.prefectureCityPairs);
    const match = pairString.match(/^(.+?[都道府県])(.+)$/); // Regex to split prefecture and city

    if (match && match[1] && match[2]) {
        return { prefecture: match[1], municipality: match[2] };
    } else {
        // Fallback if regex fails (should not happen with well-formatted list)
        console.warn("Could not parse prefecture/city pair:", pairString);
        // Attempt a simple split for known special prefectures if regex fails
        let prefecture = "";
        let municipality = "";
        if (pairString.startsWith("東京都")) { 
            prefecture = "東京都"; 
            municipality = pairString.substring(3); 
        } else if (pairString.startsWith("北海道")) { 
            prefecture = "北海道"; 
            municipality = pairString.substring(3); 
        } else if (pairString.startsWith("大阪府")) { 
            prefecture = "大阪府"; 
            municipality = pairString.substring(3); 
        } else if (pairString.startsWith("京都府")) { 
            prefecture = "京都府"; 
            municipality = pairString.substring(3); 
        } else {
            // Generic fallback: try to find the last "県"
            const lastKenIndex = pairString.lastIndexOf("県");
            if (lastKenIndex > 0) {
                prefecture = pairString.substring(0, lastKenIndex + 1);
                municipality = pairString.substring(lastKenIndex + 1);
            } else {
                 // If no "県" or other suffixes, return as is, or handle as error
                prefecture = pairString; // Or some default
                municipality = "";       // Or some default
            }
        }
        if (!municipality && prefecture === pairString) { // If municipality is still empty and no split happened
             console.warn("Fallback parsing still resulted in no municipality for:", pairString);
        }
        return { prefecture, municipality };
    }
}

function getRandomPersonalityKeywords() {
    // 3つまでのキーワードをランダムに選択
    const count = Math.floor(Math.random() * 3) + 1; // 1-3個
    const selectedKeywords = [];
    const availableKeywords = [...personaRandomValues.personality]; // コピーを作成
    
    for (let i = 0; i < count; i++) {
        if (availableKeywords.length === 0) break;
        
        const randomIndex = Math.floor(Math.random() * availableKeywords.length);
        selectedKeywords.push(availableKeywords[randomIndex]);
        availableKeywords.splice(randomIndex, 1); // 選んだキーワードは除外
    }
    
    return selectedKeywords.join('、');
}

// --- Utility Functions ---
// Get a random item from an array
function getRandomItem(arr) {
    if (!arr || arr.length === 0) {
        return ""; // Return empty string if array is empty or undefined
    }
    return arr[Math.floor(Math.random() * arr.length)];
}

// Age string (e.g., "30y", "0y6m") to years (number)
function parseAgeToYears(ageString) {
    if (!ageString) return 0;
    if (ageString.includes('m')) { // Months
        const months = parseInt(ageString.split('y')[1].replace('m', ''));
        const years = parseInt(ageString.split('y')[0]);
        return years + (months / 12);
    } else { // Only years
        return parseInt(ageString.replace('y', ''));
    }
}

// Function to set a random value for a field if it's empty
function setRandomValueIfEmpty(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field && field.value === "") {
        field.value = value;
    }
}

// Function to initialize and set random values for detailed persona settings
function randomizeDetailSettingsFields() {
    console.log("[DEBUG] randomizeDetailSettingsFields: Started.");

    // Gender
    const gender = getRandomItem(personaRandomValues.genders);
    setRandomValueIfEmpty("gender", gender);

    // Name (based on gender)
    const name = getRandomName(gender);
    setRandomValueIfEmpty("name", name);

    // Age
    const ageString = getRandomAge(); // Use new weighted random age function
    setRandomValueIfEmpty("age", ageString);
    const ageInYears = parseAgeToYears(ageString); // Get numerical age

    // Prefecture and City
    const prefectureCity = getRandomItem(personaRandomValues.prefectureCityPairs);
    if (prefectureCity) {
        const parts = prefectureCity.match(/(.+?[都道府県])(.+)/);
        if (parts && parts.length === 3) {
            setRandomValueIfEmpty("prefecture", parts[1]);
            setRandomValueIfEmpty("municipality", parts[2]);
        }
    }
    
    // Life Events - Filter based on age (This should be determined *before* family structure if it influences family structure)
    let availableLifeEvents = [...personaRandomValues.life_events];
    if (ageInYears < 18) {
        availableLifeEvents = availableLifeEvents.filter(event => 
            !event.startsWith("婚約中") && 
            event !== "就職・転職"
        );
        if (ageInYears < 15) { 
            availableLifeEvents = availableLifeEvents.filter(event => 
                event !== "出身地から離れた所に住んでいる" && 
                event !== "家族から離れた所に住んでいる"
            );
        }
    }
    // No specific filtering for 65+ for life events for now
    if (availableLifeEvents.length === 0) {
        // Fallback if all specific events are filtered out - allow field to be empty or set a very generic one if any.
    }
    const selectedLifeEvent = getRandomItem(availableLifeEvents);
    setRandomValueIfEmpty("life_events", selectedLifeEvent);

    // Family - Filter based on age AND selectedLifeEvent
    let availableFamilies = [...personaRandomValues.families];
    if (ageInYears < 18) {
        availableFamilies = availableFamilies.filter(family => 
            !["婚約中", "既婚", "新婚（3ヶ月未満）", "新婚（6ヶ月未満）", "新婚（1年未満）", 
             "子どもが生まれたばかり（0〜12ヶ月）", "幼児の子どもがいる（1〜2歳）", "子どもがいる（3〜5歳）", 
             "小学校低学年の子どもがいる（6〜8歳）", "小学校高学年の子どもがいる（9〜12歳）", 
             "中高生の子どもがいる（13〜17歳）", "成人の子どもがいる（18〜26歳）", 
             "配偶者と死別", "離婚", "別居中", "ドメスティックパートナー（事実婚）", 
             "オープンな関係", "シビルユニオン（法的パートナーシップ）"].includes(family)
        );
    }
    if (ageInYears < 1) {
        availableFamilies = availableFamilies.filter(family => family !== "父子家庭");
    }
    
    // For very elderly (90+), limit relationship types and prioritize certain family structures
    if (ageInYears >= 90) {
        // Make "新婚" (newlywed) types and legal partnership types very rare for 90+
        const rareForVeryElderly = [
            "新婚（3ヶ月未満）", "新婚（6ヶ月未満）", "新婚（1年未満）", 
            "シビルユニオン（法的パートナーシップ）", "オープンな関係", "遠距離恋愛", "婚約中"
        ];
        
        // Still possible but with 95% chance of removal - leaves small chance for interesting cases
        const randomRemovalProb = Math.random();
        if (randomRemovalProb < 0.95) {
            availableFamilies = availableFamilies.filter(family => !rareForVeryElderly.includes(family));
        }
        
        // 母子家庭・父子家庭を除外（90歳以上では非現実的）
        availableFamilies = availableFamilies.filter(family => 
            family !== "母子家庭" && family !== "父子家庭"
        );
        
        // Prioritize common elderly family statuses by duplicating them in the array
        const commonVeryElderlyFamilies = ["配偶者と死別", "成人の子どもがいる（18〜26歳）", "独身"];
        
        // Add these 3 times to greatly increase their probability
        for (let i = 0; i < 3; i++) {
            availableFamilies = [...availableFamilies, ...commonVeryElderlyFamilies.filter(f => availableFamilies.includes(f))];
        }
    }
    // For elderly (65-89), make "新婚" types less common
    else if (ageInYears >= 65) {
        const lessCommonForElderly = [
            "新婚（3ヶ月未満）", "新婚（6ヶ月未満）", "新婚（1年未満）"
        ];
        
        // Remove with 70% probability for 65-79 age range
        if (ageInYears < 80 && Math.random() < 0.7) {
            availableFamilies = availableFamilies.filter(family => !lessCommonForElderly.includes(family));
        }
        // Remove with 85% probability for 80-89 age range
        else if (ageInYears >= 80 && Math.random() < 0.85) {
            availableFamilies = availableFamilies.filter(family => !lessCommonForElderly.includes(family));
        }
        
        // 母子家庭・父子家庭を80歳以上では除外（非現実的なため）
        if (ageInYears >= 80) {
            availableFamilies = availableFamilies.filter(family => 
                family !== "母子家庭" && family !== "父子家庭"
            );
        }
        
        // Prioritize common elderly family statuses
        const commonElderlyFamilies = ["配偶者と死別", "成人の子どもがいる（18〜26歳）", "既婚", "独身"];
        
        // Add these 2 times to increase their probability
        for (let i = 0; i < 2; i++) {
            availableFamilies = [...availableFamilies, ...commonElderlyFamilies.filter(f => availableFamilies.includes(f))];
        }
    }

    // If life event is "婚約中", remove "成人の子どもがいる" from family options
    if (selectedLifeEvent && selectedLifeEvent.startsWith("婚約中")) {
        availableFamilies = availableFamilies.filter(family => 
            family !== "成人の子どもがいる（18〜26歳）" && 
            family !== "配偶者と死別" && // 矛盾する状態を防ぐ: 婚約中の人が配偶者と死別というのはおかしい
            family !== "離婚" // 矛盾する状態を防ぐ: 婚約中の人が離婚経験というのも整合性が取れない
        );
    }

    availableFamilies = availableFamilies.filter(family => {
        if (family.includes("子どもが生まれたばかり（0〜12ヶ月）") && (ageInYears < 0 || ageInYears > 55)) return false; // Unlikely for <0 or >55 to have newborn
        if (family.includes("幼児の子どもがいる（1〜2歳）") && (ageInYears < 2 || ageInYears > 57)) return false; // Unlikely for <2 or >57 to have toddler
        if (family.includes("子どもがいる（3〜5歳）") && (ageInYears < 5 || ageInYears > 60)) return false; // Unlikely for <5 or >60 to have 3-5yo
        if (family.includes("小学校低学年の子どもがいる（6〜8歳）") && (ageInYears < 8 || ageInYears > 63)) return false;
        if (family.includes("小学校高学年の子どもがいる（9〜12歳）") && (ageInYears < 12 || ageInYears > 67)) return false;
        if (family.includes("中高生の子どもがいる（13〜17歳）") && (ageInYears < 17 || ageInYears > 72)) return false;
        // For "成人の子どもがいる（18〜26歳）", it's plausible for older parents, so less strict upper bound or remove it.
        // However, ensure persona is at least 18 + 18 = 36 to have an 18yo child.
        if (family.includes("成人の子どもがいる（18〜26歳）") && ageInYears < 36) return false; 
        return true;
    });
    
    // If all families are filtered out (e.g., for a very young age), default to "独身" or "両親がいる"
    if (availableFamilies.length === 0) {
        if (ageInYears < 18) {
            availableFamilies = ["両親がいる", "独身"]; // Prioritize "両親がいる" for minors
        } else {
            availableFamilies = ["独身"];
        }
    }

    setRandomValueIfEmpty("family", getRandomItem(availableFamilies));

    // Occupation - Filter based on age
    let availableOccupations; // Declare here, assign in each block
    const allOccupations = [...personaRandomValues.occupations]; // Use a fresh copy for each main age branch

    const earlyRetirementOccupations = ["自衛官", "警察官", "消防士", "パイロット", "客室乗務員", "アスリート"]; // Occupations with typically earlier retirement or peak physical demand

    if (ageInYears < 3) {
        availableOccupations = ["未就学児"];
    } else if (ageInYears <= 5) {
        availableOccupations = allOccupations.filter(o => ["未就学児", "幼稚園児", "保育園児"].includes(o));
    } else if (ageInYears <= 11) {
        availableOccupations = allOccupations.filter(o => o === "小学生");
    } else if (ageInYears <= 14) {
        availableOccupations = allOccupations.filter(o => o === "中学生");
    } else if (ageInYears <= 17) {
        availableOccupations = allOccupations.filter(o => o === "高校生");
    } else if (ageInYears <= 22) { // Roughly university/early career age
        availableOccupations = allOccupations.filter(o => 
            !["未就学児", "幼稚園児", "保育園児", "小学生", "中学生", "高校生", 
             "教員・教師（小学校）", "教員・教師（中学校）", "教員・教師（高校）", "教員・教師（大学）",
             "会社経営者", "会社役員", 
             "定年退職者", "年金受給者"
            ].includes(o) && !earlyRetirementOccupations.includes(o) // Less likely for very young to be in these specific roles either
        );
    } else if (ageInYears >= 55 && ageInYears < 65) { // Ages 55-64: Filter early retirement roles
        availableOccupations = allOccupations.filter(o => 
            !["未就学児", "幼稚園児", "保育園児", "小学生", "中学生", "高校生", "大学生", "大学院生", "専門学校生", "浪人生", "定年退職者", "年金受給者"].includes(o) &&
            !earlyRetirementOccupations.includes(o)
        );
    } else if (ageInYears >= 65) { // Roughly retirement age
        const likelyRetirementOccupations = ["定年退職者", "年金受給者", "不労所得者", "投資家", "その他"];
        let unsuitableForSeniors = [
            "未就学児", "幼稚園児", "保育園児", "小学生", "中学生", "高校生", "大学生", "大学院生", "専門学校生", "浪人生", 
            "求職中", "就職活動中", "インターンシップ中", 
            // earlyRetirementOccupations are already unsuitable by this age, so ensure they are included if not already
            ...earlyRetirementOccupations,
            // Add other general physically demanding roles
            "建設作業員", 
            "工場勤務", 
            "配達員"
            //客室乗務員, パイロット, 消防士, 警察官, 自衛官, アスリート were moved to earlyRetirementOccupations
        ];

        if (ageInYears >= 85) {
            const veryUnsuitableForSuperSeniors = [
                "教員・教師（小学校）", "教員・教師（中学校）", "教員・教師（高校）", "教員・教師（大学）", "教員・教師（専門学校）",
                "会社経営者", "会社役員", "会社員（総合職）", "会社員（一般職）", "会社員（専門職）", "会社員（技術職）", "会社員（研究職）", "会社員（企画・マーケティング職）", "会社員（営業職）", "会社員（事務職）", "会社員（クリエイティブ職）",
                "医師", "歯科医師", "薬剤師", "看護師", "保健師", "助産師", "理学療法士", "作業療法士", "言語聴覚士",
                "弁護士", "弁理士", "司法書士", "行政書士", "税理士", "公認会計士",
                "コンサルタント（経営）", "コンサルタント（IT）", "コンサルタント（その他専門）",
                "MR（医薬情報担当者）", "臨床開発モニター",
                // Financial sector jobs explicitly excluded for 85+
                "金融関連専門職", "投資家", "不動産関連専門職", 
                // Ensure these are also here from the general 65+ list or early retirement if not already explicitly added for 85+
                ...earlyRetirementOccupations,
                "農業従事者", "林業従事者", "漁業従事者", "酪農家",
                "建設作業員", "工場勤務", "配達員" 
            ];
            unsuitableForSeniors = [...new Set([...unsuitableForSeniors, ...veryUnsuitableForSuperSeniors])];
        }

        // Start filtering from the original full list for this age bracket
        let filteredBaseOccupations = allOccupations.filter(o => 
            !unsuitableForSeniors.includes(o)
        );
        
        const possiblePostRetirement = filteredBaseOccupations.filter(o => 
            !likelyRetirementOccupations.includes(o)
        );
        
        availableOccupations = [...likelyRetirementOccupations, ...likelyRetirementOccupations, ...likelyRetirementOccupations, ...possiblePostRetirement];
    } else { // General working age (23-54, before early retirement specific filter)
        availableOccupations = allOccupations.filter(o => 
            !["未就学児", "幼稚園児", "保育園児", "小学生", "中学生", "高校生", "大学生", "大学院生", "専門学校生", "浪人生", "定年退職者", "年金受給者"].includes(o)
        );
    }

    if (!availableOccupations || availableOccupations.length === 0) { // Fallback if no occupation matches
        availableOccupations = ["その他"];
    }
    setRandomValueIfEmpty("occupation", getRandomItem(availableOccupations));

    // Income - Filter based on age
    let availableIncomeRanges = [...personaRandomValues.incomeRanges];
    const studentOccupations = ["未就学児", "幼稚園児", "保育園児", "小学生", "中学生", "高校生", "大学生", "大学院生", "専門学校生", "浪人生"];
    const currentOccupation = document.getElementById("occupation") ? document.getElementById("occupation").value : getRandomItem(availableOccupations);

    if (studentOccupations.includes(currentOccupation) || ageInYears < 18) {
        availableIncomeRanges = ["<100"]; // Students and under 18 typically have very low or no income
    } else if (ageInYears < 20) { // 18-19 years old
        availableIncomeRanges = availableIncomeRanges.filter(range => {
            const lowerBound = parseInt(range.split('-')[0].replace('<', ''));
            return lowerBound < 200; // e.g., "<100", "100-200"
        });
    } else if (ageInYears < 23) { // 20-22 years old (early career / part-time)
        availableIncomeRanges = availableIncomeRanges.filter(range => {
            const lowerBound = parseInt(range.split('-')[0].replace('<', ''));
            return lowerBound < 400; // Up to "300-400"
        });
    } else if (ageInYears >= 65) {
        // For 65+, allow lower incomes (pension) but also higher if they are still working/investors
        // Prioritize lower incomes more
        const pensionIncomes = ["<100", "100-200", "200-300", "300-400"];
        const otherIncomes = availableIncomeRanges.filter(range => !pensionIncomes.includes(range));
        availableIncomeRanges = [...pensionIncomes, ...pensionIncomes, ...otherIncomes]; // Weight lower incomes
    }
    // For general working ages (23-64), no specific upper cap from this list, but ensure not student income
    // This is implicitly handled by the first condition.

    if (availableIncomeRanges.length === 0) { // Fallback
        availableIncomeRanges = ["<100"]; // Default to lowest if filters are too strict
    }
    
    // 収入設定を年齢と職業に基づく制限ロジックを使用するように変更
    const adjustedIncome = getRandomAnnualIncome(ageInYears, currentOccupation, availableIncomeRanges);
    setRandomValueIfEmpty("income", adjustedIncome);

    // Hobbies - Filter based on age
    let availableHobbies = [...personaRandomValues.hobbies];
    
    if (ageInYears < 1) {
        availableHobbies = ["おもちゃ", "公園"].filter(h => personaRandomValues.hobbies.includes(h));
        if (availableHobbies.length === 0) { // Ultimate fallback for infant
            availableHobbies = ["おもちゃで遊ぶ"];
        }
    } else if (ageInYears < 3) {
        availableHobbies = ["おもちゃ", "テレビ", "公園"].filter(h => personaRandomValues.hobbies.includes(h));
        if (availableHobbies.length === 0) { // Ultimate fallback for toddler
            availableHobbies = ["おもちゃで遊ぶ", "絵本", "お絵かき"];
        }
    } else if (ageInYears >= 65) {
        // 高齢者向けの趣味リストを追加
        const elderlyHobbies = ["読書", "園芸", "散歩", "テレビ鑑賞", "ラジオ", "将棋", "囲碁", "俳句", "短歌", "家庭菜園", 
                               "料理", "絵画", "歴史探訪", "温泉めぐり", "健康体操", "カラオケ", "手芸", "お茶", "花見", "写真"];
        
        // 高齢者に適さない趣味をフィルタリング
        availableHobbies = availableHobbies.filter(hobby => 
            !["スケートボード", "サーフィン", "スノーボード", "バンジージャンプ", "ロッククライミング", "パルクール", 
              "ヘビーメタル", "クラブ通い", "アイドル追っかけ", "コスプレ"].includes(hobby)
        );
        
        // 高齢者向け趣味を追加（重複を避けるためにSet使用）
        availableHobbies = [...new Set([...availableHobbies, ...elderlyHobbies.filter(h => personaRandomValues.hobbies.includes(h))])];
        
        // もし選択肢がない場合は elderlyHobbies から直接選ぶ
        if (availableHobbies.length === 0) {
            availableHobbies = elderlyHobbies;
        }
    } else {
        availableHobbies = ["読書", "音楽", "映画"].filter(h => personaRandomValues.hobbies.includes(h));
        if (availableHobbies.length === 0 && personaRandomValues.hobbies.length > 0) { // Ultimate fallback general
            availableHobbies = [getRandomItem(personaRandomValues.hobbies)];
        }
    }
    
    // 最終的な保険として、趣味が空にならないようにする
    if (!availableHobbies || availableHobbies.length === 0) {
        availableHobbies = ["読書"];
    }
    
    setRandomValueIfEmpty("hobby", getRandomItem(availableHobbies));

    // 追加項目の年齢フィルタリングを行う関数
    function filterRandomValuesForAge(list, ageInYears, categoryType) {
        if (!list || list.length === 0) return [];
        
        let filteredList = [...list];
        
        if (categoryType === 'motto') {
            // 座右の銘の年齢フィルタリング
            if (ageInYears < 7) {
                // 7歳未満の子供には理解できる単純な言葉のみ
                const simpleMottos = ["笑顔が一番", "友達大事", "楽しく遊ぶ", "元気が一番"];
                return filteredList.filter(item => simpleMottos.includes(item)) || simpleMottos;
            } else if (ageInYears < 15) {
                // 15歳未満の子供には難解な四字熟語などをフィルター
                return filteredList.filter(item => 
                    !["初心忘るべからず", "歓びを分かち合えば二倍に、悲しみを分かち合えば半分に"].includes(item)
                );
            }
        } 
        
        else if (categoryType === 'concerns') {
            // 悩み・関心の年齢フィルタリング
            if (ageInYears < 10) {
                // 10歳未満の子供向け
                const childConcerns = ["お友達との関係", "勉強", "好きな遊び", "好きな食べ物", "テレビアニメ"];
                return childConcerns;
            } else if (ageInYears < 18) {
                // 10-18歳向け
                return filteredList.filter(item => 
                    !["老眼", "認知症予防", "生活習慣病予防"].includes(item)
                ).concat(["学校生活", "勉強の成績", "将来の進路", "友人関係"]);
            } else if (ageInYears >= 65) {
                // 65歳以上の高齢者向け
                return filteredList.filter(item => 
                    !["就職活動", "昇進", "子育て"].includes(item)
                ).concat(["老後の生活", "年金", "健康維持"]);
            }
        } 
        
        else if (categoryType === 'favorite_person') {
            // 好きな有名人の年齢フィルタリング
            if (ageInYears < 10) {
                // 10歳未満の子供向け
                const childFavoritePeople = ["アンパンマン", "ドラえもん", "クレヨンしんちゃん", "ポケモンのキャラクター", "プリキュア", "鬼滅の刃のキャラクター", "すみっコぐらし", "ミッキーマウス", "しまじろう", "いないいないばあっ！のワンワン", "おかあさんといっしょの体操のお兄さん", "戦隊ヒーロー", "仮面ライダー", "ウルトラマン", "となりのトトロ", "魔女の宅急便のキキ", "ピカチュウ"];
                return childFavoritePeople;
            } else if (ageInYears < 18) {
                // 10-18歳向け - アニメキャラクターやYouTuber、若手アイドルが好きな傾向
                return filteredList.concat(["ユーチューバー", "若手アイドル", "アニメキャラクター", "TikToker", "Vtuber"]);
            } else if (ageInYears >= 20 && ageInYears < 35) {
                // 20-34歳向け - アニメキャラクターは控え、若手有名人、スポーツ選手などを優先
                const youngAdultFavorites = filteredList.filter(item => 
                    !["アンパンマン", "ドラえもん", "クレヨンしんちゃん", "ポケモンのキャラクター", "プリキュア", "すみっコぐらし", "しまじろう", "いないいないばあっ！のワンワン", "おかあさんといっしょの体操のお兄さん", "ピカチュウ"].includes(item)
                );
                return youngAdultFavorites;
            } else if (ageInYears >= 35 && ageInYears < 60) {
                // 35-59歳向け - 子供向けキャラクターは除外、同世代の有名人や歴史的人物を優先
                const middlewAdultFavorites = filteredList.filter(item => 
                    !["アンパンマン", "ドラえもん", "クレヨンしんちゃん", "ポケモンのキャラクター", "プリキュア", "鬼滅の刃のキャラクター", "すみっコぐらし", "ミッキーマウス", "しまじろう", "いないいないばあっ！のワンワン", "おかあさんといっしょの体操のお兄さん", "戦隊ヒーロー", "仮面ライダー", "ウルトラマン", "となりのトトロ", "魔女の宅急便のキキ", "ピカチュウ", "ユーチューバー", "若手アイドル", "アニメキャラクター", "TikToker", "Vtuber"].includes(item)
                );
                // アニメや漫画のキャラクターが含まれている場合は90%の確率で除外
                if (Math.random() < 0.9) {
                    return middlewAdultFavorites.filter(item => 
                        !item.includes("キャラクター") && !item.includes("アニメ") && !item.includes("漫画")
                    );
                }
                return middlewAdultFavorites;
            } else if (ageInYears >= 60) {
                // 60歳以上の高齢者向け
                const seniorFavoritePeople = ["美空ひばり", "加山雄三", "石原裕次郎", "中村勘三郎", "淡島千景", "松田聖子", "西田敏行", "渥美清", "山田洋次", "黒澤明", "高倉健", "坂本九", "森光子", "吉永小百合", "加藤登紀子", "小林旭", "北野武", "細川たかし", "小柳ルミ子", "司馬遼太郎", "山本五十六", "柳家小さん", "橋田壽賀子"];
                // 子供向けキャラクターや若者向け有名人を除外
                const filteredSeniorList = filteredList.filter(item => 
                    !["アンパンマン", "ドラえもん", "クレヨンしんちゃん", "ポケモンのキャラクター", "プリキュア", "鬼滅の刃のキャラクター", "すみっコぐらし", "ミッキーマウス", "しまじろう", "いないいないばあっ！のワンワン", "おかあさんといっしょの体操のお兄さん", "戦隊ヒーロー", "仮面ライダー", "ウルトラマン", "となりのトトロ", "魔女の宅急便のキキ", "ピカチュウ", "ユーチューバー", "若手アイドル", "TikToker", "Vtuber", "King Gnu", "あいみょん", "Official髭男dism", "藤井聡太", "NiziU", "BTS", "SnowMan", "櫻坂46", "乃木坂46"].includes(item)
                );
                return [...filteredSeniorList, ...seniorFavoritePeople];
            }
        } 
        
        else if (categoryType === 'media_sns') {
            // メディア/SNSの年齢フィルタリング
            if (ageInYears < 10) {
                // 10歳未満の子供には一部SNSは不適切
                return ["テレビ", "YouTube", "子供向けアプリ"];
            } else if (ageInYears < 15) {
                // 10-15歳向け
                return filteredList.filter(item => 
                    !["Twitter", "Facebook", "TikTok", "LINE", "Podcast"].includes(item)
                );
            } else if (ageInYears >= 75) {
                // 75歳以上の高齢者向け
                const seniorMedia = ["テレビ", "新聞", "ラジオ", "NHK", "地上波テレビ"];
                if (Math.random() < 0.3) { // 30%の確率でデジタルメディアも
                    seniorMedia.push("YouTube");
                }
                return seniorMedia;
            }
        } 
        
        else if (categoryType === 'health_actions') {
            // 健康に関する行動の年齢フィルタリング
            if (ageInYears < 15) {
                // 15歳未満の子供向け
                const childHealthActions = ["手洗いうがいを心がけている", "早寝早起きを心がけている", "栄養バランスの良い食事を食べている", "外で遊ぶようにしている"];
                return childHealthActions;
            } else if (ageInYears < 22) {
                // 15-22歳向け
                return filteredList.filter(item => 
                    !["血圧を測るようにした", "定期的に薬を飲み始めた", "禁煙した", "老眼鏡を作った"].includes(item)
                );
            } else if (ageInYears >= 65) {
                // 65歳以上の高齢者向け
                return filteredList.concat(["定期的な病院の通院", "介護予防体操", "血圧測定"]);
            }
        } 
        
        else if (categoryType === 'holiday_activities') {
            // 休日の過ごし方の年齢フィルタリング
            if (ageInYears < 10) {
                // 10歳未満の子供向け
                const childActivities = ["公園で遊ぶ", "テレビを見る", "おもちゃで遊ぶ", "友達と遊ぶ", "家族で出かける"];
                return childActivities;
            } else if (ageInYears < 18) {
                // 10-18歳向け
                return filteredList.filter(item => 
                    !["温泉に行く", "投資の勉強", "ワイン選び", "ドライブに行く"].includes(item)
                );
            } else if (ageInYears >= 80) {
                // 80歳以上の高齢者向け
                return filteredList.filter(item => 
                    !["アクティブスポーツ", "登山", "夜のイベント参加", "長距離旅行"].includes(item)
                ).concat(["近所の散歩", "テレビ視聴", "家族との団欒"]);
            }
        } 
        
        else if (categoryType === 'catchphrase') {
            // キャッチコピーの年齢フィルタリング
            if (ageInYears < 12) {
                // 12歳未満の子供向け
                const childCatchphrases = ["笑顔いっぱい元気いっぱい", "友達と仲良く", "元気が一番", "いつも楽しく"];
                return childCatchphrases;
            }
        }
        
        // カテゴリーに該当するフィルターがないか、フィルターの条件に当てはまらない場合は元のリストを返す
        return filteredList;
    }

    // 座右の銘 (Motto)
    const filteredMottos = filterRandomValuesForAge(personaRandomValues.motto, ageInYears, 'motto');
    setRandomValueIfEmpty("motto", getRandomItem(filteredMottos));

    // 最近の悩み/関心 (Concerns)
    const filteredConcerns = filterRandomValuesForAge(personaRandomValues.concerns, ageInYears, 'concerns');
    setRandomValueIfEmpty("concerns", getRandomItem(filteredConcerns));

    // 好きな有名人/尊敬する人物 (Favorite Person)
    const filteredFavoritePerson = filterRandomValuesForAge(personaRandomValues.favorite_person, ageInYears, 'favorite_person');
    setRandomValueIfEmpty("favorite_person", getRandomItem(filteredFavoritePerson));

    // よく見るメディア/SNS (Media/SNS)
    const filteredMediaSNS = filterRandomValuesForAge(personaRandomValues.media_sns, ageInYears, 'media_sns');
    setRandomValueIfEmpty("media_sns", getRandomItem(filteredMediaSNS));

    // 性格キーワード (Personality)
    setRandomValueIfEmpty("personality_keywords", getRandomPersonalityKeywords());

    // 最近した健康に関する行動 (Health Actions)
    const filteredHealthActions = filterRandomValuesForAge(personaRandomValues.health_actions, ageInYears, 'health_actions');
    setRandomValueIfEmpty("health_actions", getRandomItem(filteredHealthActions));

    // 休日の過ごし方 (Holiday Activities)
    const filteredHolidayActivities = filterRandomValuesForAge(personaRandomValues.holiday_activities, ageInYears, 'holiday_activities');
    setRandomValueIfEmpty("holiday_activities", getRandomItem(filteredHolidayActivities));

    // キャッチコピー (Catchphrase)
    const filteredCatchphrase = filterRandomValuesForAge(personaRandomValues.catchphrase, ageInYears, 'catchphrase');
    setRandomValueIfEmpty("catchphrase", getRandomItem(filteredCatchphrase));

    console.log("[DEBUG] randomizeDetailSettingsFields: Completed.");
}

// --- Helper function to map granular HTML income values to the keys used in incomeBracketsWithWeights ---
function getWeightedBracketForIncome(incomeValueStr) {
    if (!incomeValueStr) return null;
    let lowerBound = 0;
    let upperBound = Infinity;

    // Parse the income string (e.g., "<100", "100-200", ">=10000")
    if (incomeValueStr.startsWith("<")) {
        upperBound = parseInt(incomeValueStr.substring(1));
        lowerBound = 0; // Technically, but the check is mostly upperBound
    } else if (incomeValueStr.startsWith(">=")) {
        lowerBound = parseInt(incomeValueStr.substring(2));
    } else if (incomeValueStr.includes("-")) {
        const parts = incomeValueStr.split('-');
        lowerBound = parseInt(parts[0]);
        upperBound = parseInt(parts[1]);
    } else {
        // If it's a single number (shouldn't happen with current ranges, but for safety)
        try {
            const singleNum = parseInt(incomeValueStr);
            lowerBound = singleNum;
            upperBound = singleNum;
        } catch (e) {
            console.warn("Could not parse incomeValueStr:", incomeValueStr);
            return null;
        }
    }

    // Map to incomeBracketsWithWeights keys based on the lower bound primarily
    if (upperBound <= 100 && lowerBound < 100) return "100万円未満"; // Catches "<100"
    // For ranges like "100-200", "200-300", etc. the lower bound determines the bracket start
    if (lowerBound >= 100 && lowerBound < 200) return "100万円以上200万円未満";
    if (lowerBound >= 200 && lowerBound < 300) return "200万円以上300万円未満";
    if (lowerBound >= 300 && lowerBound < 400) return "300万円以上400万円未満";
    if (lowerBound >= 400 && lowerBound < 500) return "400万円以上500万円未満";
    if (lowerBound >= 500 && lowerBound < 600) return "500万円以上600万円未満";
    if (lowerBound >= 600 && lowerBound < 700) return "600万円以上700万円未満";
    if (lowerBound >= 700 && lowerBound < 800) return "700万円以上800万円未満";
    if (lowerBound >= 800 && lowerBound < 900) return "800万円以上900万円未満";
    if (lowerBound >= 900 && lowerBound < 1000) return "900万円以上1000万円未満";
    if (lowerBound >= 1000 && lowerBound < 1200) return "1000万円以上1200万円未満";
    if (lowerBound >= 1200 && lowerBound < 1500) return "1200万円以上1500万円未満";
    if (lowerBound >= 1500 && lowerBound < 2000) return "1500万円以上200万円未満";
    if (lowerBound >= 2000) return "2000万円以上"; // Catches ">=2000" and any range starting at 2000+

    // Fallback if no bracket matches (e.g. if incomeValueStr was like "abc")
    console.warn("Income value did not map to a bracket:", incomeValueStr, "Lb:", lowerBound, "Ub:", upperBound);
    return null;
}

document.addEventListener('DOMContentLoaded', async () => {
    // 患者タイプのアイコンを初期化
    if (typeof initializePatientTypeIcons === 'function') {
        initializePatientTypeIcons();
    }
    
    let currentPersonaResult = null;
    let hasRandomizedDetailsEver = false; // ランダム初期化実行フラグ
    let loadingStep; // <--- loadingStep をここで宣言

    // (Keep checkDepartmentIcons function here if it exists)
    function checkDepartmentIcons() {
        const departmentIcons = document.querySelectorAll('.department-icon');
        departmentIcons.forEach(icon => {
            const backgroundImage = getComputedStyle(icon).backgroundImage;
            if (backgroundImage === 'none' || backgroundImage === '') return;
            const match = backgroundImage.match(/url\(['"]?([^'"]+)['"]?\)/);
            if (!match) return;
            const imgPath = match[1];
            const img = new Image();
            img.onerror = () => {
                console.warn(`アイコン画像が読み込めませんでした: ${imgPath}`);
                icon.style.display = 'none'; 
                const label = icon.closest('label');
                if (label) label.style.paddingTop = '15px';
            };
            img.src = imgPath;
        });
    }
    checkDepartmentIcons();

    const multiStepForm = document.getElementById('multi-step-form');
    const formSteps = multiStepForm.querySelectorAll('.form-step');
    const nextButtons = multiStepForm.querySelectorAll('.next-step-btn');
    const prevButtons = multiStepForm.querySelectorAll('.prev-step-btn');
    // departmentRadios, purposeRadios, settingTypeRadios are queried before event listeners are added.
    const detailedSettingsDiv = document.getElementById('detailed-settings');
    const autoSettingInfo = document.getElementById('auto-setting-info');
    const addFieldButton = document.getElementById('add-field-btn');
    const additionalFieldsContainer = document.getElementById('additional-fields');
    const confirmAndProceedBtns = document.querySelectorAll('.confirm-and-proceed-btn');
    const editBackButton = multiStepForm.querySelector('.result-step .prev-step-btn');
    const mainContainer = document.querySelector('.main-container');
    const patientTypeSelectionDiv = document.getElementById('patient-type-selection');
    const patientTypeDescriptionDiv = document.getElementById('patient-type-description');
    // patientTypeRadios is queried before its event listener
    const finalGenerateBtns = document.querySelectorAll('.final-generate-btn-common');
    const editStepButtons = multiStepForm.querySelectorAll('.edit-step-btn');

    let currentStep = 1;
    const TOTAL_FORM_STEPS = 5; 
    let hasVisitedConfirmationScreen = false;
    const purposeLabels = multiStepForm.querySelectorAll('.purpose-options label');

    // --- NEW showStep FUNCTION DEFINITION --- 
    function showStep(stepNumberToShow) {
        loadingStep = document.querySelector('.loading-step'); // <--- ここで代入
        const resultStep = document.querySelector('.result-step');

        formSteps.forEach(s => s.classList.remove('active'));
        if (loadingStep) loadingStep.classList.remove('active');
        if (resultStep) resultStep.classList.remove('active');

        if (stepNumberToShow === TOTAL_FORM_STEPS + 1) { // Loading
            if (loadingStep) loadingStep.classList.add('active');
            currentStep = stepNumberToShow;
            return;
        } else if (stepNumberToShow === TOTAL_FORM_STEPS + 2) { // Result
            if (resultStep) resultStep.classList.add('active');
            currentStep = stepNumberToShow;
            return;
        } else if (stepNumberToShow < 1 || stepNumberToShow > TOTAL_FORM_STEPS) {
            console.warn("showStep called with invalid step number:", stepNumberToShow, "Defaulting to step 1.");
            stepNumberToShow = 1; // Default to step 1 if invalid
        }

        const targetStepElement = formSteps[stepNumberToShow - 1];
        if (targetStepElement) {
            targetStepElement.classList.add('active');
            
            // 確認画面（ステップ5）の処理
            if (stepNumberToShow === 5) {
                // 上部のボタンを確実に表示する
                const topButtonContainer = targetStepElement.querySelector('.step-nav-buttons');
                if (topButtonContainer) {
                    topButtonContainer.style.display = 'block';
                    topButtonContainer.style.visibility = 'visible';
                    console.log('[DEBUG] Confirmation screen: Ensuring top button container is visible');
                }
                
                const topGenerateButton = document.getElementById('final-generate-btn-top');
                if (topGenerateButton) {
                    topGenerateButton.style.display = 'inline-block';
                    topGenerateButton.style.visibility = 'visible';
                    console.log('[DEBUG] Confirmation screen: Ensuring top generate button is visible');
                }
            }
        } else {
            console.error(`Form step element not found for step number: ${stepNumberToShow}. Cannot proceed.`);
            return;
        }
        currentStep = stepNumberToShow;

        if (currentStep === 3 && !hasRandomizedDetailsEver) {
            if (typeof randomizeDetailSettingsFields === 'function') {
                console.log("[DEBUG] showStep: Calling randomizeDetailSettingsFields for Step 3. hasRandomizedDetailsEver:", hasRandomizedDetailsEver);
                randomizeDetailSettingsFields();
            }
            hasRandomizedDetailsEver = true;
            console.log("[DEBUG] showStep: hasRandomizedDetailsEver set to true.");
        }

        const numInputSteps = TOTAL_FORM_STEPS - 1;
        if (currentStep >= 1 && currentStep <= numInputSteps) {
            formSteps.forEach((fs) => {
                const stepDataNumber = parseInt(fs.dataset.step);
                if (stepDataNumber !== currentStep) return;
                const progressBarElement = fs.querySelector('.progress');
                const progressTextElement = fs.querySelector('.progress-bar span');
                if (progressBarElement && progressTextElement) {
                    progressBarElement.style.width = `${(currentStep / numInputSteps) * 100}%`;
                    progressTextElement.textContent = `${currentStep}/${numInputSteps}問目`;
                }
            });
        }

        formSteps.forEach((stepElem) => {
            const stepIdx = parseInt(stepElem.dataset.step);
            const confirmBtn = stepElem.querySelector('.confirm-and-proceed-btn');
            const nextBtn = stepElem.querySelector('.next-step-btn');
            const prevBtn = stepElem.querySelector('.prev-step-btn');

            if (stepIdx === currentStep) {
                if (confirmBtn) confirmBtn.style.display = (currentStep >= 1 && currentStep <= numInputSteps) ? 'inline-block' : 'none';
                if (nextBtn) nextBtn.style.display = (currentStep < numInputSteps) ? 'inline-block' : 'none';
                if (prevBtn) prevBtn.style.display = (currentStep > 1 && currentStep <= TOTAL_FORM_STEPS) ? 'inline-block' : 'none';
                } else {
                if (confirmBtn) confirmBtn.style.display = 'none';
                if (nextBtn) nextBtn.style.display = 'none';
                if (prevBtn) prevBtn.style.display = 'none';
            }
        });

        if (currentStep === numInputSteps) {
            const lastInputStepElement = formSteps[numInputSteps - 1];
            if (lastInputStepElement) {
                const nextBtnOnLast = lastInputStepElement.querySelector('.next-step-btn');
                if (nextBtnOnLast) nextBtnOnLast.style.display = 'none';
                const confirmBtnOnLast = lastInputStepElement.querySelector('.confirm-and-proceed-btn');
                if (confirmBtnOnLast) confirmBtnOnLast.style.display = 'inline-block';
            }
        }
    }
    console.log('Debug: typeof showStep before assignment:', typeof showStep); // ADD THIS
    window.showStep = showStep; // Assign to window object
    // --- END NEW showStep FUNCTION DEFINITION ---

    window.currentOutputSettings = { pdf: true, ppt: true, gslide: false };
    try {
        const response = await fetch('/api/settings/output'); 
        if (response.ok) {
            const outputSettings = await response.json();
            window.currentOutputSettings = { ...outputSettings, pdf: true, ppt: true }; 
        } else {
            console.error("Failed to fetch output settings for user:", response.status);
        }
    } catch (error) {
        console.error("Error fetching output settings:", error);
    }

    // --- REMOVE OLD/FAULTY showStep WRAPPER (original lines ~562-574) ---
    // const originalShowStep = showStep; // THIS LINE AND THE BLOCK SHOULD BE GONE
    // window.showStep = function(stepNumber) { ... }; // THIS BLOCK SHOULD BE GONE
    // --- END REMOVAL ---

    function getFormData() {
        const formData = new FormData(multiStepForm);
        const data = {};
        formData.forEach((value, key) => {
            if (key.endsWith('[]')) {
                 const cleanKey = key.slice(0, -2);
                 if (!data[cleanKey]) data[cleanKey] = [];
                 data[cleanKey].push(value);
            } else if (key !== 'setting_type') { 
                 data[key] = value;
            }
        });
        const checkedSettingTypeRadio = document.querySelector('input[name="setting_type"]:checked');
        if (checkedSettingTypeRadio) data['setting_type'] = checkedSettingTypeRadio.value;
        else data['setting_type'] = 'patient_type'; // Default to 'patient_type' if none selected
        const departmentRadio = multiStepForm.querySelector('input[name="department"]:checked');
        if(departmentRadio) data['department'] = departmentRadio.value;
        // console.log("Collected Form Data:", data);
        return data;
    }

    function populateConfirmationScreen(data) {
        // console.log("Populating confirmation screen with data:", data);
        const getRadioDisplayText = (groupName, value) => {
            if (!value) return 'なし';
            const radio = document.querySelector(`input[name="${groupName}"][value="${value}"]`);
            return radio && radio.parentElement && radio.parentElement.textContent ? radio.parentElement.textContent.trim() : value;
        };
        const getSelectDisplayText = (selectId, value) => {
            if (!value) return 'なし';
            const selectElement = document.getElementById(selectId);
            if (selectElement) {
                const optionElement = selectElement.querySelector(`option[value="${value}"]`);
                if (optionElement) return optionElement.textContent.trim();
            }
            return value;
        };
        document.getElementById('summary-department').textContent = getRadioDisplayText('department', data.department);
        document.getElementById('summary-purpose').textContent = getRadioDisplayText('purpose', data.purpose);
        const basicInfoContainer = document.getElementById('summary-basic-info');
        basicInfoContainer.innerHTML = ''; 
        const basicInfoOrder = ['name', 'gender', 'age', 'prefecture', 'municipality', 'family', 'occupation', 'income', 'hobby', 'life_events'];
        const valueMap = {
            name: data.name,
            gender: getSelectDisplayText('gender', data.gender),
            age: data.age ? (data.age.includes('m') ? data.age.replace('y', '歳').replace('m', 'ヶ月') : data.age.replace('y', '歳')) : 'なし',
            prefecture: data.prefecture,
            municipality: data.municipality,
            family: data.family,
            occupation: data.occupation,
            income: data.income ? (data.income.startsWith('<') ? `${data.income.substring(1)}万円未満` : (data.income.startsWith('>=') ? `${data.income.substring(2)}万円以上` : `${data.income}万円`)) : 'なし',
            hobby: data.hobby,
            life_events: data.life_events
        };
        const labelMap = { name: '名前:', gender: '性別:', age: '年齢:', prefecture: '都道府県:', municipality: '市区町村:', family: '家族構成:', occupation: '職業:', income: '年収:', hobby: '趣味:', life_events: 'ライフイベント:' };
        basicInfoOrder.forEach(key => {
            const p = document.createElement('p');
            p.innerHTML = `<strong>${labelMap[key]}</strong> ${valueMap[key] || 'なし'}`;
            basicInfoContainer.appendChild(p);
        });
        if (data.patient_type) {
            const p = document.createElement('p');
            p.innerHTML = `<strong>患者タイプ:</strong> ${getRadioDisplayText('patient_type', data.patient_type) || 'なし'}`;
            basicInfoContainer.appendChild(p);
        }
        const additionalFixedContainer = document.getElementById('summary-additional-fixed-info');
        additionalFixedContainer.innerHTML = '';
        const fixedFieldsOrder = [
            { key: 'motto', label: '座右の銘:' }, { key: 'concerns', label: '最近の悩み/関心:' }, 
            { key: 'favorite_person', label: '好きな有名人/尊敬する人物:' }, { key: 'media_sns', label: 'よく見るメディア/SNS:' }, 
            { key: 'personality_keywords', label: '性格キーワード（3語以内）:' }, { key: 'health_actions', label: '最近した健康に関する行動:' }, 
            { key: 'holiday_activities', label: '休日の過ごし方:' }, { key: 'catchphrase', label: 'キャッチコピー:' }
        ];
        fixedFieldsOrder.forEach(item => {
            const p = document.createElement('p');
            p.innerHTML = `<strong>${item.label}</strong> ${data[item.key] || 'なし'}`;
            additionalFixedContainer.appendChild(p);
        });
        if (data.additional_field_name && data.additional_field_value && data.additional_field_name.length === data.additional_field_value.length) {
            const hasDynamicData = data.additional_field_name.some((name, i) => name || data.additional_field_value[i]);
            if (hasDynamicData) {
                data.additional_field_name.forEach((fieldName, index) => {
                    const fieldValue = data.additional_field_value[index];
                    if (fieldName || fieldValue) { 
                        const p = document.createElement('p');
                        p.innerHTML = `<strong>${fieldName || '項目名なし'}:</strong> ${fieldValue || 'なし'}`;
                        additionalFixedContainer.appendChild(p);
                    }
                });
            }
        }
        hasVisitedConfirmationScreen = true;
    }

    // --- Event Listeners ---
    const currentDepartmentRadios = multiStepForm.querySelectorAll('input[name="department"]');
    currentDepartmentRadios.forEach(originalRadio => {
        const newRadio = originalRadio.cloneNode(true);
        if (originalRadio.parentNode) originalRadio.parentNode.replaceChild(newRadio, originalRadio);
        newRadio.addEventListener('change', () => {
            updateSelectedLabel(multiStepForm.querySelectorAll('input[name="department"]'), 'department');
        });
    });
    const currentPurposeRadios = multiStepForm.querySelectorAll('input[name="purpose"]');
    currentPurposeRadios.forEach(originalRadio => {
        const newRadio = originalRadio.cloneNode(true);
        if (originalRadio.parentNode) originalRadio.parentNode.replaceChild(newRadio, originalRadio);
        newRadio.addEventListener('change', (event) => {
            updateSelectedLabel(multiStepForm.querySelectorAll('input[name="purpose"]'), 'purpose');
        });
    });
    const currentSettingTypeRadios = multiStepForm.querySelectorAll('input[name="setting_type"]');
    currentSettingTypeRadios.forEach(originalRadio => {
        const newRadio = originalRadio.cloneNode(true);
        if (originalRadio.parentNode) originalRadio.parentNode.replaceChild(newRadio, originalRadio);
        newRadio.addEventListener('change', function(event) {
            if (typeof updateSelectedLabel === 'function') {
                updateSelectedLabel(multiStepForm.querySelectorAll('input[name="setting_type"]'), 'setting_type');
            }
            const settingType = event.target.value;
            if (settingType === 'input') {
                if (detailedSettingsDiv) detailedSettingsDiv.style.display = 'block';
                if (autoSettingInfo) autoSettingInfo.style.display = 'none';
                if (patientTypeSelectionDiv) patientTypeSelectionDiv.style.display = 'none';
                if (!hasRandomizedDetailsEver && typeof randomizeDetailSettingsFields === 'function') {
                     const currentStepElement = document.querySelector('.form-step.active');
                     if (currentStepElement && currentStepElement.dataset.step === "3") {
                          randomizeDetailSettingsFields();
                          hasRandomizedDetailsEver = true;
                     }
                }
            } else if (settingType === 'auto') {
                if (detailedSettingsDiv) detailedSettingsDiv.style.display = 'none';
                if (autoSettingInfo) autoSettingInfo.style.display = 'block';
                if (patientTypeSelectionDiv) patientTypeSelectionDiv.style.display = 'none';
            } else { // patient_type or default
                if (detailedSettingsDiv) detailedSettingsDiv.style.display = 'none';
                if (autoSettingInfo) autoSettingInfo.style.display = 'none';
                if (patientTypeSelectionDiv) patientTypeSelectionDiv.style.display = 'flex';
                const convenientTypeRadio = document.getElementById('pt-convenience');
                if (convenientTypeRadio && !document.querySelector('input[name="patient_type"]:checked')) {
                    convenientTypeRadio.checked = true;
                    if (typeof updatePatientTypeDisplay === 'function') updatePatientTypeDisplay(convenientTypeRadio.value);
                } else if (document.querySelector('input[name="patient_type"]:checked')){
                    if (typeof updatePatientTypeDisplay === 'function') updatePatientTypeDisplay(document.querySelector('input[name="patient_type"]:checked').value);
                }
            }
        });
    });
    const patientTypeGrid = document.querySelector('.patient-type-grid');
    if (patientTypeGrid) {
        patientTypeGrid.addEventListener('click', (event) => {
            const targetItem = event.target.closest('.patient-type-item');
            if (!targetItem) return;
            const radio = targetItem.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                multiStepForm.querySelectorAll('.patient-type-item').forEach(item => item.classList.remove('selected'));
                targetItem.classList.add('selected');
                if (typeof updatePatientTypeDisplay === 'function') updatePatientTypeDisplay(radio.value);
            }
        });
    }
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (currentStep === 1) {
                const selectedDept = multiStepForm.querySelector('input[name="department"]:checked');
                if (!selectedDept) {
                    alert('診療科を選択してください。');
                    return;
                }
            }
            if (currentStep < TOTAL_FORM_STEPS - 1) {
                if (typeof window.showStep === 'function') window.showStep(currentStep + 1);
                else console.error('showStep is not a function when trying to go to next step');
             }
        });
    });
    prevButtons.forEach(button => {
        button.addEventListener('click', () => {
            const parentStep = button.closest('.form-step');
            if (parentStep && parentStep.dataset.step === String(TOTAL_FORM_STEPS)) { // Confirmation step (e.g. step 5)
                if (typeof window.showStep === 'function') window.showStep(TOTAL_FORM_STEPS - 1); // Go back to last input step (e.g. step 4)
                else console.error('showStep is not a function when trying to go to prev step from confirmation');
            } else if (currentStep > 1) {
                if (typeof window.showStep === 'function') window.showStep(currentStep - 1);
                else console.error('showStep is not a function when trying to go to prev step');
            }
        });
    });
    if (editBackButton) {
        editBackButton.addEventListener('click', () => {
            if (typeof window.showStep === 'function') window.showStep(TOTAL_FORM_STEPS);
            else console.error('showStep is not a function for editBackButton');
        });
    }
    confirmAndProceedBtns.forEach(button => {
        button.addEventListener('click', async () => {
            const formData = getFormData();
            populateConfirmationScreen(formData);
            if (typeof window.showStep === 'function') {
                window.showStep(TOTAL_FORM_STEPS);
                
                // 確認画面に遷移した後、上部のボタンが表示されるよう強制的に設定
                setTimeout(() => {
                    const confirmationScreen = document.querySelector('.form-step[data-step="5"]');
                    if (confirmationScreen) {
                        const topButtonContainer = confirmationScreen.querySelector('.step-nav-buttons');
                        if (topButtonContainer) {
                            topButtonContainer.style.display = 'block';
                            topButtonContainer.style.visibility = 'visible';
                            console.log('[DEBUG] Confirmation transition: Ensuring top button container is visible');
                        }
                        
                        const topGenerateButton = document.getElementById('final-generate-btn-top');
                        if (topGenerateButton) {
                            topGenerateButton.style.display = 'inline-block';
                            topGenerateButton.style.visibility = 'visible';
                            console.log('[DEBUG] Confirmation transition: Ensuring top generate button is visible');
                        }
                    }
                }, 100); // ページ遷移後に少し遅延して実行
            }
            else console.error('showStep is not a function for confirmAndProceedBtns');
        });
    });
    editStepButtons.forEach(button => {
        button.addEventListener('click', () => {
            hasVisitedConfirmationScreen = true;
            const targetStep = parseInt(button.dataset.step);
            if (targetStep > 0 && targetStep < TOTAL_FORM_STEPS) {
                if (typeof window.showStep === 'function') window.showStep(targetStep);
                else console.error('showStep is not a function for editStepButtons');
                if (targetStep === 3) {
                    const formData = getFormData();
                    const settingType = formData.setting_type || 'patient_type';
                    const radioToSelect = document.querySelector(`input[name="setting_type"][value="${settingType}"]`);
                    if (radioToSelect) {
                        radioToSelect.checked = true;
                        radioToSelect.dispatchEvent(new Event('change'));
                    }
                }
            }
        });
    });
    finalGenerateBtns.forEach(button => {
        button.addEventListener('click', async function() {
            if (typeof window.showStep === 'function') window.showStep(TOTAL_FORM_STEPS + 1); // Show loading
            else console.error('showStep is not a function for finalGenerateBtns (loading)');
            
            const data = getFormData();
            currentPersonaResult = null;
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'ペルソナ生成中に不明なエラーが発生しました。' }));
                    throw new Error(errorData.detail || `サーバーエラー: ${response.status}`);
                }

                const result = await response.json();
                currentPersonaResult = result; // Store the result
                
                // Call showStep before populateResults
                showStep(TOTAL_FORM_STEPS + 2); // Show result screen (Step 7)
                // Delay populateResults to allow DOM to update
                setTimeout(() => {
                    populateResults(result); // Populate results on Step 7
                }, 0); 

            } catch (error) {
                console.error('Error generating persona:', error);
                alert(`ペルソナ生成に失敗しました: ${error.message}`);
                showStep(TOTAL_FORM_STEPS); // Go back to confirmation screen on error
            } finally {
                // Hide loading screen
                if (loadingStep) { // <--- 存在確認を追加
                    loadingStep.classList.remove('active');
                }
            }
        });
    });

     // Add Additional Field Button (Step 4)
     addFieldButton.addEventListener('click', () => {
        const newFieldRow = document.createElement('div');
        newFieldRow.classList.add('additional-field-row');
        newFieldRow.style.display = 'flex';
        newFieldRow.style.alignItems = 'center';
        newFieldRow.style.marginBottom = '10px';
        newFieldRow.style.gap = '10px';
        newFieldRow.innerHTML = `
            <input type="text" name="additional_field_name[]" placeholder="項目" style="height: 32px; border: 1px solid #ccc; border-radius: 4px; padding: 2px 8px; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.9em; flex: 1;">
            <input type="text" name="additional_field_value[]" placeholder="内容" style="height: 32px; border: 1px solid #ccc; border-radius: 4px; padding: 2px 8px; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.9em; flex: 2;">
            <button type="button" class="remove-field-btn" style="background-color: #dc3545; color: white; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; height: fit-content;">削除</button>
        `;
        additionalFieldsContainer.appendChild(newFieldRow);
    });

    // Remove Additional Field Button (Event Delegation)
    additionalFieldsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('remove-field-btn')) {
            event.target.closest('.additional-field-row').remove();
        }
    });

    function populateResults(result) {
        console.log("Populating results screen with data:", result);
        const profile = result.profile || {}; 

        // DEBUG: Check if download buttons exist before population
        console.log('Before population - PDF Button:', document.getElementById('download-pdf-result'));
        console.log('Before population - PPT Button:', document.getElementById('download-ppt-result'));
        
        // HTMLで定義されたダウンロードオプションコンテナのスタイルを調整
        const htmlDownloadOptions = document.querySelector('.persona-details .download-options');
        if (htmlDownloadOptions) {
            // 上部位置を調整して線の上に載らないようにする
            htmlDownloadOptions.style.top = '-20px'; // さらに上に調整（-20pxから-30pxに）
            console.log('Adjusted position of HTML download options container');
            
            // HTMLのボタンも高さを固定
            const pdfBtn = htmlDownloadOptions.querySelector('#download-pdf-result');
            const pptBtn = htmlDownloadOptions.querySelector('#download-ppt-result');
            
            if (pdfBtn) {
                pdfBtn.style.height = '30px';
                pdfBtn.style.lineHeight = '18px';
            }
            
            if (pptBtn) {
                pptBtn.style.height = '30px';
                pptBtn.style.lineHeight = '18px';
            }
        }
        
        // 完全に独立したフローティングダウンロードボタンを作成
        // まず既存のボタンを削除
        const existingPdfButton = document.getElementById('floating-pdf-button');
        const existingPptButton = document.getElementById('floating-ppt-button');
        if (existingPdfButton) existingPdfButton.remove();
        if (existingPptButton) existingPptButton.remove();
        
        // フローティングコンテナ作成
        const floatingContainer = document.createElement('div');
        floatingContainer.id = 'floating-download-buttons';
        floatingContainer.style.position = 'absolute'; 
        floatingContainer.style.top = '-20px'; // -30px から -20px に変更して少し下げる
        floatingContainer.style.right = '20px'; 
        floatingContainer.style.zIndex = '1000'; 
        floatingContainer.style.display = 'flex'; 
        floatingContainer.style.flexDirection = 'row'; 
        floatingContainer.style.gap = '10px';

        // PDFボタン
        const pdfButton = document.createElement('button');
        pdfButton.id = 'floating-pdf-button';
        pdfButton.textContent = 'PDF'; 
        pdfButton.style.backgroundColor = '#ff0000';
        pdfButton.style.color = 'white';
        pdfButton.style.border = 'none';
        pdfButton.style.borderRadius = '4px';
        pdfButton.style.padding = '6px 12px'; 
        pdfButton.style.cursor = 'pointer';
        pdfButton.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)'; 
        pdfButton.style.fontSize = '13px'; 
        pdfButton.style.width = '80px'; 
        pdfButton.style.height = '30px'; // 高さを固定
        pdfButton.style.lineHeight = '18px'; // 行の高さを調整
        pdfButton.style.textAlign = 'center'; 
        
        // PPTボタン
        const pptButton = document.createElement('button');
        pptButton.id = 'floating-ppt-button';
        pptButton.textContent = 'PPT'; 
        pptButton.style.backgroundColor = '#ff8431';
        pptButton.style.color = 'white';
        pptButton.style.border = 'none';
        pptButton.style.borderRadius = '4px';
        pptButton.style.padding = '6px 12px'; 
        pptButton.style.cursor = 'pointer';
        pptButton.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)'; 
        pptButton.style.fontSize = '13px'; 
        pptButton.style.width = '80px'; 
        pptButton.style.height = '30px'; // 高さを固定
        pptButton.style.lineHeight = '18px'; // 行の高さを調整
        pptButton.style.textAlign = 'center';
        
        // PDFボタンのクリックイベント
        pdfButton.addEventListener('click', async () => {
            if (!currentPersonaResult) {
                alert('ペルソナがまだ生成されていません。');
             return;
        }

            // ボタンスタイル変更
            pdfButton.textContent = '生成中...';
            pdfButton.disabled = true;
            pdfButton.style.opacity = '0.7';
            
            try {
                const response = await fetch('/api/download/pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentPersonaResult)
                });
                
                if (!response.ok) {
                    throw new Error(`サーバーエラー ${response.status}`);
                }
                
                const blob = await response.blob();
                let filename = `${currentPersonaResult.profile.name || 'persona'}_persona.pdf`;
                
                // Content-Dispositionが存在すればファイル名を取得
                const contentDisposition = response.headers.get('content-disposition');
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                    if (filenameMatch && filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }
                
                // ダウンロード処理
                triggerDownload(blob, filename);
                
            } catch (error) {
                console.error('PDF Download Error:', error);
                alert(`エラーが発生しました: ${error.message}`);
            } finally {
                // ボタン状態を戻す
                pdfButton.textContent = 'PDF';
                pdfButton.disabled = false;
                pdfButton.style.opacity = '1';
            }
        });
        
        // PPTボタンのクリックイベント
        pptButton.addEventListener('click', async () => {
            if (!currentPersonaResult) {
                alert('ペルソナがまだ生成されていません。');
             return;
        }

            // ボタンスタイル変更
            pptButton.textContent = '生成中...';
            pptButton.disabled = true;
            pptButton.style.opacity = '0.7';
            
            try {
                const response = await fetch('/api/download/ppt', {
                method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentPersonaResult)
            });

            if (!response.ok) {
                    throw new Error(`サーバーエラー ${response.status}`);
            }

                const blob = await response.blob();
                let filename = `${currentPersonaResult.profile.name || 'persona'}_persona.pptx`;

                // Content-Dispositionが存在すればファイル名を取得
                const contentDisposition = response.headers.get('content-disposition');
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                    if (filenameMatch && filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }
                
                // ダウンロード処理
                triggerDownload(blob, filename);

        } catch (error) {
                console.error('PPT Download Error:', error);
                alert(`エラーが発生しました: ${error.message}`);
            } finally {
                // ボタン状態を戻す
                pptButton.textContent = 'PPT';
                pptButton.disabled = false;
                pptButton.style.opacity = '1';
            }
        });
        
        // ボタンをコンテナに追加
        floatingContainer.appendChild(pdfButton);
        floatingContainer.appendChild(pptButton);
        
        // 親コンテナを見つけて追加
        const resultContainer = document.querySelector('.result-step');
        if (resultContainer) {
            // 既存のものがあれば削除
            const existingContainer = document.getElementById('floating-download-buttons');
            if (existingContainer) {
                existingContainer.remove();
            }
            
            // 相対配置用に親コンテナにposition: relative設定
            resultContainer.style.position = 'relative';
            resultContainer.appendChild(floatingContainer);
            console.log('Download buttons added to result-step container');
        } else {
            // フォールバック: body直下に追加
            document.body.appendChild(floatingContainer);
            console.log('Download buttons added to body (fallback)');
        }

        // Populate New Header Info Section
        let headerDepartmentDisplay = profile.department || '-';
        if (profile.department) {
            const deptRadio = document.querySelector(`input[name="department"][value="${profile.department}"]`);
            if (deptRadio && deptRadio.parentElement && deptRadio.parentElement.textContent) {
                headerDepartmentDisplay = deptRadio.parentElement.textContent.trim();
            }
        }
        document.getElementById('header-department').textContent = headerDepartmentDisplay;

        let headerPurposeDisplay = profile.purpose || '-';
        if (profile.purpose) {
            const purposeRadio = document.querySelector(`input[name="purpose"][value="${profile.purpose}"]`);
            if (purposeRadio && purposeRadio.parentElement && purposeRadio.parentElement.textContent) {
                headerPurposeDisplay = purposeRadio.parentElement.textContent.trim();
            }
        }
        document.getElementById('header-purpose').textContent = headerPurposeDisplay;
        
        // Update image
        document.getElementById('preview-persona-image').src = result.image_url || 'https://via.placeholder.com/150';
        document.getElementById('preview-name').textContent = profile.name || '-';

        // Populate basic info in the preview pane (2-column grid)
        // Department and Purpose are now removed from this specific section in the preview
        // document.getElementById('preview-department').textContent = departmentDisplay; // REMOVED
        // document.getElementById('preview-purpose').textContent = purposeDisplay; // REMOVED

        document.getElementById('preview-gender').textContent = getSelectDisplayTextForResult('gender', profile.gender);
        document.getElementById('preview-age').textContent = formatAgeDisplayForResult(profile.age);
        const prefectureSelectResult = document.getElementById('preview-prefecture');
        if (prefectureSelectResult) {
            // 選択リストの値を設定し、デバッグ情報を出力
            console.log('Setting prefecture value:', profile.prefecture);
            prefectureSelectResult.value = profile.prefecture || "";
            
            // 値が正しく設定されたか確認
            console.log('Prefecture select after setting value:', prefectureSelectResult.value);
            
            // 選択肢のoption要素が存在するか確認
            const options = Array.from(prefectureSelectResult.options);
            const matchingOption = options.find(opt => opt.value === profile.prefecture);
            console.log('Matching option found:', matchingOption ? 'Yes' : 'No');
            
            // 明示的にchangeイベントを発火させる
            prefectureSelectResult.dispatchEvent(new Event('change'));
        }
        document.getElementById('preview-municipality').textContent = profile.municipality || '-';
        document.getElementById('preview-family').textContent = profile.family || '-';
        document.getElementById('preview-occupation').textContent = profile.occupation || '-';
        document.getElementById('preview-income').textContent = formatIncomeDisplayForResult(profile.income);
        document.getElementById('preview-hobby').textContent = profile.hobby || '-';
        document.getElementById('preview-life_events').textContent = profile.life_events && Array.isArray(profile.life_events) ? profile.life_events.join(', ') : (profile.life_events || '-');
        
        let patientTypeDisplay = profile.patient_type || '-';
        if (profile.patient_type && typeof patientTypeDetails !== 'undefined' && patientTypeDetails[profile.patient_type]) {
            patientTypeDisplay = profile.patient_type; 
        } else if (profile.patient_type) {
            const patientTypeRadio = document.querySelector(`input[name="patient_type"][value="${profile.patient_type}"]`);
            if (patientTypeRadio && patientTypeRadio.parentElement && patientTypeRadio.parentElement.querySelector('.patient-type-name')) {
                patientTypeDisplay = patientTypeRadio.parentElement.querySelector('.patient-type-name').textContent.trim();
            }
        }
        document.getElementById('preview-patient_type').textContent = patientTypeDisplay;

        // Populate Step 4 Fixed Additional Fields (1-column in .additional-info-column)
        document.getElementById('preview-motto').textContent = profile.motto || '-';
        document.getElementById('preview-concerns').textContent = profile.concerns || '-';
        document.getElementById('preview-favorite_person').textContent = profile.favorite_person || '-';
        document.getElementById('preview-media_sns').textContent = profile.media_sns || '-';
        document.getElementById('preview-personality_keywords').textContent = profile.personality_keywords || '-';
        document.getElementById('preview-health_actions').textContent = profile.health_actions || '-';
        document.getElementById('preview-holiday_activities').textContent = profile.holiday_activities || '-';
        document.getElementById('preview-catchphrase_input').textContent = profile.catchphrase || '-'; 

        // Populate Step 4 Dynamically Added Fields (1-column in .additional-info-column)
        const dynamicFieldsContainer = document.getElementById('preview-additional-dynamic-fields');
        dynamicFieldsContainer.innerHTML = ''; 
        if (profile.additional_field_name && profile.additional_field_value &&
            Array.isArray(profile.additional_field_name) && Array.isArray(profile.additional_field_value) &&
            profile.additional_field_name.length === profile.additional_field_value.length) {
            profile.additional_field_name.forEach((fieldName, index) => {
                const fieldValue = profile.additional_field_value[index];
                if (fieldName || fieldValue) { 
                    const p = document.createElement('p');
                    p.innerHTML = `<strong>${fieldName || '項目名なし'}:</strong> ${fieldValue || 'なし'}`;
                    dynamicFieldsContainer.appendChild(p);
                }
            });
        }

        // Populate detailed persona text on the right side
        const detailsContainer = document.querySelector('.persona-details');
        detailsContainer.innerHTML = ''; // Clear previous details

        if (result.details) {
            // Map the backend keys to their display titles
            const detailOrder = [
                { key: 'personality', title: '性格（価値観・人生観）' },
                { key: 'reason', title: '通院理由' },
                { key: 'behavior', title: '症状通院頻度・行動パターン' },
                { key: 'reviews', title: '口コミの重視ポイント' },
                { key: 'values', title: '医療機関への価値観・行動傾向' },
                { key: 'demands', title: '医療機関に求めるもの' }
            ];
            
            let contentAdded = false;
            detailOrder.forEach(item => {
                if (result.details[item.key]) {
                    const sectionTitle = document.createElement('h4');
                    sectionTitle.textContent = item.title;
                    detailsContainer.appendChild(sectionTitle);

                    const sectionContent = document.createElement('p');
                    if (Array.isArray(result.details[item.key])) {
                         sectionContent.innerHTML = result.details[item.key].map(pText => String(pText || '').replace(/\n/g, '<br>')).join('<br>');
                    } else {
                        sectionContent.innerHTML = String(result.details[item.key] || '').replace(/\n/g, '<br>');
                    }
                    detailsContainer.appendChild(sectionContent);
                    contentAdded = true;
                }
            });

            if (!contentAdded) {
                 const noResultText = document.createElement('p');
                 noResultText.textContent = 'ペルソナの詳細情報が生成されませんでした。';
                 detailsContainer.appendChild(noResultText);
            }

        } else {
            const noResultText = document.createElement('p');
            noResultText.textContent = 'ペルソナの詳細情報が生成されませんでした。';
            detailsContainer.appendChild(noResultText);
        }

        // 編集可能フィールドのセットアップ
        setupEditableFields();
        
        // DEBUG: Final check of download buttons after population
        console.log('After population - PDF Button:', document.getElementById('download-pdf-result'));
        console.log('After population - PPT Button:', document.getElementById('download-ppt-result'));
        
        // Force buttons to be visible again
        const pdfBtn = document.getElementById('download-pdf-result');
        const pptBtn = document.getElementById('download-ppt-result');
        if (pdfBtn) pdfBtn.style.display = 'inline-block';
        if (pptBtn) pptBtn.style.display = 'inline-block';
    }

    // --- Download Functionality ---

    // Helper function to trigger browser download
    function triggerDownload(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    }

    // 編集可能フィールドの変更イベントを設定する関数
    function setupEditableFields() {
        // 名前フィールドの編集リスナー設定
        const nameField = document.getElementById('preview-name');
        if (nameField) {
            nameField.addEventListener('input', function() {
                // currentPersonaResultを更新
                if (currentPersonaResult && currentPersonaResult.profile) {
                    currentPersonaResult.profile.name = this.textContent;
                }
            });
            
            // フォーカスアウト時のトリミング処理
            nameField.addEventListener('blur', function() {
                this.textContent = this.textContent.trim();
                if (this.textContent === '') {
                    this.textContent = '-';
                }
            });
        }
        
        // 都道府県フィールドの編集リスナー設定 (select要素なのでchangeイベントを使用)
        const prefectureField = document.getElementById('preview-prefecture');
        if (prefectureField) {
            prefectureField.addEventListener('change', function() {
                // currentPersonaResultを更新
                if (currentPersonaResult && currentPersonaResult.profile) {
                    currentPersonaResult.profile.prefecture = this.value;
                    console.log('Prefecture changed to:', this.value);
                }
            });
            
            // populateResults時に正しく選択状態を復元するため
            if (currentPersonaResult && currentPersonaResult.profile && currentPersonaResult.profile.prefecture) {
                prefectureField.value = currentPersonaResult.profile.prefecture;
            }
        }
        
        // 市区町村フィールドの編集リスナー設定
        const municipalityField = document.getElementById('preview-municipality');
        if (municipalityField) {
            municipalityField.addEventListener('input', function() {
                // currentPersonaResultを更新
                if (currentPersonaResult && currentPersonaResult.profile) {
                    currentPersonaResult.profile.municipality = this.textContent;
                }
            });
            
            // フォーカスアウト時のトリミング処理
            municipalityField.addEventListener('blur', function() {
                this.textContent = this.textContent.trim();
                if (this.textContent === '') {
                    this.textContent = '-';
                }
            });
        }
    }

    // Event listener for PDF download button
    const pdfDownloadBtn = document.getElementById('download-pdf-result');
    if (pdfDownloadBtn) {
        // あらかじめ幅を固定
        pdfDownloadBtn.style.width = '80px';
        pdfDownloadBtn.style.height = '30px';
        pdfDownloadBtn.style.lineHeight = '18px';
        pdfDownloadBtn.style.textAlign = 'center';
        
        pdfDownloadBtn.addEventListener('click', async () => {
            if (!currentPersonaResult) {
                alert('ペルソナがまだ生成されていません。');
                return;
            }
            if (!currentPersonaResult.profile || !currentPersonaResult.details) {
                 alert('ペルソナデータが不完全です。');
                 console.error("Incomplete persona data for download:", currentPersonaResult);
                 return;
            }

            // Add a simple loading indicator (optional)
            const originalText = pdfDownloadBtn.textContent;
            pdfDownloadBtn.textContent = '生成中...';
            pdfDownloadBtn.disabled = true;

            try {
                const response = await fetch('/api/download/pdf', { // Changed to relative path
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentPersonaResult), // Send the stored result
                });

                if (!response.ok) {
                    // Try to parse error message from backend
                    let errorMsg = 'PDFの生成に失敗しました。';
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    } catch (e) {
                        // Ignore if response is not JSON
                    }
                    throw new Error(errorMsg + ` (Status: ${response.status})`);
                }

                const blob = await response.blob();
                // Extract filename from Content-Disposition header if available, otherwise generate one
                const contentDisposition = response.headers.get('content-disposition');
                let filename = `${currentPersonaResult.profile.name || 'persona'}_persona.pdf`; // Default filename
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                    if (filenameMatch && filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }
                triggerDownload(blob, filename);

            } catch (error) {
                console.error('PDF Download Error:', error);
                alert(`エラーが発生しました: ${error.message}`);
            } finally {
                 // Restore button text and state
                pdfDownloadBtn.textContent = originalText;
                pdfDownloadBtn.disabled = false;
            }
        });
    }

    // Event listener for "最初から" (restart) button
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
        restartBtn.addEventListener('click', () => {
            // リセット確認
            if (confirm('最初からやり直しますか？入力した内容はすべてリセットされます。')) {
                // フォームをリセット
                document.getElementById('multi-step-form').reset();
                // ステップ1に戻る
                showStep(1);
                // 現在のペルソナ結果をクリア
                currentPersonaResult = null;
                hasRandomizedDetailsEver = false; // ランダム初期化フラグをリセット

                // Reset setting_type to patient_type and update UI
                const patientTypeRadio = document.querySelector('input[name="setting_type"][value="patient_type"]');
                if (patientTypeRadio) {
                    patientTypeRadio.checked = true;
                    patientTypeRadio.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        });
    }

    // Placeholder for PPT download button
    const pptDownloadBtn = document.getElementById('download-ppt-result');
    if (pptDownloadBtn) {
        // あらかじめ幅を固定
        pptDownloadBtn.style.width = '80px';
        pptDownloadBtn.style.height = '30px';
        pptDownloadBtn.style.lineHeight = '18px';
        pptDownloadBtn.style.textAlign = 'center';
        
        pptDownloadBtn.addEventListener('click', async () => {
            if (!currentPersonaResult) {
                alert('ペルソナがまだ生成されていません。');
                return;
            }
            if (!currentPersonaResult.profile || !currentPersonaResult.details) {
                 alert('ペルソナデータが不完全です。');
                 console.error("Incomplete persona data for download:", currentPersonaResult);
                 return;
            }

            // Add loading indicator
            const originalText = pptDownloadBtn.textContent;
            pptDownloadBtn.textContent = '生成中...';
            pptDownloadBtn.disabled = true;

            try {
                const response = await fetch('/api/download/ppt', { // Changed to relative path
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentPersonaResult),
                });

                if (!response.ok) {
                    let errorMsg = 'PPTの生成に失敗しました。';
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    } catch (e) { /* Ignore */ }
                    throw new Error(errorMsg + ` (Status: ${response.status})`);
                }

                const blob = await response.blob();
                const contentDisposition = response.headers.get('content-disposition');
                let filename = `${currentPersonaResult.profile.name || 'persona'}_persona.pptx`; // Default .pptx
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                    if (filenameMatch && filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }
                triggerDownload(blob, filename);

            } catch (error) {
                console.error('PPT Download Error:', error);
                alert(`エラーが発生しました: ${error.message}`);
            } finally {
                // Restore button
                pptDownloadBtn.textContent = originalText;
                pptDownloadBtn.disabled = false;
            }
        });
    }

    // --- Function to control button visibility ---
    function updateDownloadButtonVisibility(settings) {
        console.log("Updating download button visibility with settings:", settings);
        const pdfBtn = document.getElementById('download-pdf-result');
        const pptBtn = document.getElementById('download-ppt-result');
        // const gslideBtn = document.getElementById('download-gslide-result'); // Removed Googleスライド button

        // Always force PDF and PPT buttons to be visible regardless of settings
        if (pdfBtn) pdfBtn.style.display = 'inline-block';
        if (pptBtn) pptBtn.style.display = 'inline-block';

        // Googleスライドは設定に基づいて表示/非表示 - このセクションを削除
        /*
        if (gslideBtn) {
            if (settings && settings.output_gslide_enabled) {
                gslideBtn.style.display = 'inline-block';
            } else {
                gslideBtn.style.display = 'none';
            }
        }
        */
    }

    // Function to update the .selected class on labels
    function updateSelectedLabel(radios, type) {
        // Remove selected class from all labels
        let optionsContainer;
        if (type === 'setting_type') {
            // Use direct class selector specifically for setting_type
            optionsContainer = multiStepForm.querySelector('.setting-type-options');
        } else {
            // Use attribute selector for others (like purpose, department)
            optionsContainer = multiStepForm.querySelector(`div[class*="${type}-options"]`);
        }

        if (optionsContainer) {
            const labels = optionsContainer.querySelectorAll('label');
            labels.forEach(label => {
                label.classList.remove('selected');
            });
        } 
        
        // Add selected class to the label of the checked radio
        const checkedRadio = multiStepForm.querySelector(`input[name="${type}"]:checked`);
        if (checkedRadio) {
            const parentLabel = checkedRadio.closest('label');
            if (parentLabel) {
                parentLabel.classList.add('selected');
            }
        }
    }

    // --- Initial Setup --- 
    showStep(1); // TEMPORARY: Show result screen for UI dev

    // Set initial selected class based on checked radios (replaces initial updateSelectedLabel calls)
    ['department', 'purpose', 'setting_type'].forEach(type => {
        const checkedRadio = multiStepForm.querySelector(`input[name="${type}"]:checked`);
        if (checkedRadio) {
            const parentLabel = checkedRadio.closest('label');
            if (parentLabel) {
                // Find all labels for this type and remove selected first
                const container = parentLabel.closest(`div[class*="${type.replace('_', '-')}-options"]`);
                if(container){
                    container.querySelectorAll('label').forEach(lbl => lbl.classList.remove('selected'));
                }
                // Then add selected class to the correct one
                parentLabel.classList.add('selected');
            }
        }
    });

    // Initialize state for step 3 display (after setting initial class)
    const initialSettingTypeRadio = document.querySelector('input[name="setting_type"]:checked');
    if (initialSettingTypeRadio) {
        const initialSettingType = initialSettingTypeRadio.value;
        // 初期表示の制御。HTMLで patient_type が checked になっている想定。
        if (initialSettingType === 'input') {
            detailedSettingsDiv.style.display = 'block';
            autoSettingInfo.style.display = 'none';
            patientTypeSelectionDiv.style.display = 'none';
        } else if (initialSettingType === 'auto') {
            detailedSettingsDiv.style.display = 'none';
            autoSettingInfo.style.display = 'block';
            patientTypeSelectionDiv.style.display = 'none';
        } else if (initialSettingType === 'patient_type') {
             detailedSettingsDiv.style.display = 'none';
             autoSettingInfo.style.display = 'none';
             patientTypeSelectionDiv.style.display = 'flex';
             
             const convenientTypeRadio = document.getElementById('pt-convenience');
             if (convenientTypeRadio && !document.querySelector('input[name="patient_type"]:checked')) {
                 convenientTypeRadio.checked = true;
                 updatePatientTypeDisplay(convenientTypeRadio.value);
             } else if (document.querySelector('input[name="patient_type"]:checked')){
                 updatePatientTypeDisplay(document.querySelector('input[name="patient_type"]:checked').value);
             } else if (convenientTypeRadio) { // Fallback if no patient type is checked but convenient exists
                 convenientTypeRadio.checked = true;
                 updatePatientTypeDisplay(convenientTypeRadio.value);
             }
        }
    } else { 
         // Default case if nothing is checked initially for setting_type (should be patient_type based on HTML)
         const patientTypeRadioDefault = document.querySelector('input[name="setting_type"][value="patient_type"]');
         if(patientTypeRadioDefault) patientTypeRadioDefault.checked = true;

         if (detailedSettingsDiv) detailedSettingsDiv.style.display = 'none'; 
         if (autoSettingInfo) autoSettingInfo.style.display = 'none';
         if (patientTypeSelectionDiv) patientTypeSelectionDiv.style.display = 'flex';// Default to patient_type view
         
         const convenientTypeRadio = document.getElementById('pt-convenience');
         if (convenientTypeRadio && !document.querySelector('input[name="patient_type"]:checked')) {
             convenientTypeRadio.checked = true;
             updatePatientTypeDisplay(convenientTypeRadio.value);
         } else if (document.querySelector('input[name="patient_type"]:checked')){
             updatePatientTypeDisplay(document.querySelector('input[name="patient_type"]:checked').value);
         }
    }

    setupEditableFields();
    
    // 都道府県選択リストのグローバルイベントリスナを追加
    const prefectureSelect = document.getElementById('preview-prefecture');
    if (prefectureSelect) {
        // カスタムのchangeイベントリスナを追加
        prefectureSelect.addEventListener('change', function() {
            console.log('Global prefecture change event:', this.value);
            // currentPersonaResultがなければ早期リターン
            if (!currentPersonaResult || !currentPersonaResult.profile) return;
            
            // 値を更新
            currentPersonaResult.profile.prefecture = this.value;
            console.log('Updated prefecture in currentPersonaResult:', currentPersonaResult.profile.prefecture);
        });
        
        // MutationObserverでselect要素の値変更を監視
        const prefectureObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                    console.log('Prefecture select value attribute changed:', prefectureSelect.value);
                }
            });
        });
        
        prefectureObserver.observe(prefectureSelect, { attributes: true });
    }

    // Helper function to update patient type description and selection style
    function updatePatientTypeDisplay(selectedValue) {
        const patientTypeDescriptionDiv = document.getElementById('patient-type-description');
        const multiStepForm = document.getElementById('multi-step-form');

        // 全ての患者タイプアイテムのアイコンを初期化
        multiStepForm.querySelectorAll('.patient-type-item').forEach(item => {
            item.classList.remove('selected');
            
            // タイプ名を取得
            const radioInput = item.querySelector('input[type="radio"]');
            if (radioInput) {
                const typeName = radioInput.value;
                const iconDiv = item.querySelector('.patient-type-icon');
                
                if (iconDiv) {
                    // 各タイプのアイコンを設定
                    iconDiv.style.backgroundImage = `url('/static/images/${typeName}.png')`;
                    iconDiv.style.backgroundSize = 'contain';
                    iconDiv.style.backgroundPosition = 'center';
                    iconDiv.style.backgroundRepeat = 'no-repeat';
                    iconDiv.style.backgroundColor = 'transparent';
                    iconDiv.style.backgroundBlendMode = 'normal'; // 追加: 通常のブレンドモードに設定
                }
            }
        });
        
        // 選択されたアイテムにselectedクラスを追加
        const selectedRadio = document.querySelector(`input[name="patient_type"][value="${selectedValue}"]`);
        if (selectedRadio) {
            const parentItem = selectedRadio.closest('.patient-type-item');
            if (parentItem) {
                parentItem.classList.add('selected');
                
                // 選択されたアイコンのブレンドモード設定を削除
                // 以下のコードを削除
                /* const iconDiv = parentItem.querySelector('.patient-type-icon');
                if (iconDiv) {
                    iconDiv.style.backgroundBlendMode = 'multiply'; // 選択時は乗算ブレンドを設定
                } */
            }
        }

        const details = patientTypeDetails[selectedValue];
        if (details) {
            patientTypeDescriptionDiv.innerHTML = `
                <h5>${selectedValue}</h5>
                <p><strong>特徴:</strong> ${details.description}</p>
                <p><strong>例:</strong> ${details.example}</p>
            `;
            patientTypeDescriptionDiv.style.display = 'block';
        } else {
            patientTypeDescriptionDiv.innerHTML = '';
            patientTypeDescriptionDiv.style.display = 'none';
        }
    }

    // 同様に initializePatientTypeIcons 関数も更新
    function initializePatientTypeIcons() {
        const patientTypeItems = document.querySelectorAll('.patient-type-item');
        patientTypeItems.forEach(item => {
            const radioInput = item.querySelector('input[type="radio"]');
            if (radioInput) {
                const typeName = radioInput.value;
                const iconDiv = item.querySelector('.patient-type-icon');
                
                if (iconDiv) {
                    // 既存の背景画像設定を削除
                    iconDiv.style.backgroundImage = '';
                    
                    // すでに画像がある場合は追加しない
                    if (!iconDiv.querySelector('img')) {
                        // 新しいimg要素を作成
                        const img = document.createElement('img');
                        // 環境に応じた画像パスを構築（Render用の静的ディレクトリに対応）
                        img.src = `/static/images/${typeName}.png`;
                        img.alt = typeName;
                        img.loading = 'eager'; // 即時読み込み
                        // 画像がない場合にエラーハンドリング
                        img.onerror = function() {
                            // 代替パスを試す
                            this.src = `/images/${typeName}.png`;
                            // それでもだめなら絶対パスを試す
                            this.onerror = function() {
                                this.src = `./images/${typeName}.png`;
                                // 最終的に失敗したらエラー表示を消す
                                this.onerror = null;
                            };
                        };
                        iconDiv.appendChild(img);
                    }
                }
            }
        });
    }

    // DOMContentLoadedイベントリスナーを追加して確実に実行
    document.addEventListener('DOMContentLoaded', function() {
        // 既存のイベントリスナーに加えて
        initializePatientTypeIcons();
    });

});

// Helper function (can be moved to a more global scope if needed elsewhere)
function getSelectDisplayTextForResult(selectId, value) {
    if (!value) return '-';
    const selectElement = document.getElementById(selectId);
    if (selectElement) {
        const optionElement = selectElement.querySelector(`option[value="${value}"]`);
        if (optionElement) {
            return optionElement.textContent.trim();
        }
    }
    return value; // Fallback
}

function formatAgeDisplayForResult(ageValue) {
    if (!ageValue) return '-';
    let display = ageValue.replace('y', '歳');
    if (ageValue.includes('m')) {
        display = display.replace('m', 'ヶ月');
    }
    return display;
}

function formatIncomeDisplayForResult(incomeValue) {
    if (!incomeValue) return '-';
    if (incomeValue.startsWith('<')) {
        return `${incomeValue.substring(1)}万円未満`;
    } else if (incomeValue.startsWith('>=')) {
        return `${incomeValue.substring(2)}万円以上`;
    } else if (incomeValue.includes('-')) {
        return `${incomeValue}万円`;
    }
    return `${incomeValue}万円`;
}

// --- Helper Function to get random annual income with weighted distribution ---

const incomeBracketsWithWeights = {
    "100万円未満": 25,             // Increased
    "100万円以上200万円未満": 30,    // Increased
    "200万円以上300万円未満": 25,    // Maintained
    "300万円以上400万円未満": 15,    // Decreased
    "400万円以上500万円未満": 10,    // Decreased
    "500万円以上600万円未満": 7,     // Decreased
    "600万円以上700万円未満": 4,     // Decreased
    "700万円以上800万円未満": 2,     // Significantly Decreased
    "800万円以上900万円未満": 1,     // Significantly Decreased
    "900万円以上1000万円未満": 0.5,   // Significantly Decreased
    "1000万円以上1200万円未満": 0.3, // Significantly Decreased
    "1200万円以上1500万円未満": 0.1, // Significantly Decreased
    "1500万円以上2000万円未満": 0.05, // Significantly Decreased
    "2000万円以上": 0.02             // Significantly Decreased
};

function getRandomAnnualIncome(ageInYears, currentOccupation, allPossibleHtmlIncomeValues) {
    console.log("getRandomAnnualIncome called with age:", ageInYears, "occupation:", currentOccupation, "availableHtmlIncomes:", allPossibleHtmlIncomeValues);

    const studentOccupations = personaRandomValues.occupations.filter(o =>
        o.includes("学生") || o.includes("生徒") || o.includes("浪人生") || o.includes("未就学児") || o.includes("幼稚園児") || o.includes("保育園児")
    ).concat(["小学生", "中学生", "高校生"]);

    const lowIncomeElderlyProfessions = [
        "年金受給者", "無職（高齢）", "清掃員", "警備員", "軽作業スタッフ", 
        "農業（小規模）", "漁業（小規模）", "秘書", "事務職（一般）", 
        "事務職（専門）", "受付", "販売員", "接客業" 
    ];

    if (studentOccupations.includes(currentOccupation) || ageInYears < 18) {
        console.log("Selecting '<100' (100万円未満) due to student status or age < 18");
        return "<100";
    }

    // Define professions with generally capped income (not likely to reach very high brackets)
    const incomeCappedProfessions = {
        // 公務員・公的機関系
        "自衛官": 1500, // Max ~15 million JPY
        "警察官": 1500,
        "消防士": 1500,
        "公務員（国家）": 1800, // Max ~18 million JPY for high-ranking national public servants
        "公務員（地方）": 1500, // Max ~15 million JPY for local public servants
        
        // 教育系
        "教員・教師（小学校）": 1200,
        "教員・教師（中学校）": 1200,
        "教員・教師（高校）": 1300,
        "教員・教師（専門学校）": 1200,
        "教員・教師（大学）": 1800,
        "学者・研究者": 1800,
        
        // 医療・福祉系
        "保育士": 800,
        "介護福祉士": 800,
        "社会福祉士": 900,
        "精神保健福祉士": 900,
        "看護師": 1200,
        "助産師": 1200,
        "保健師": 1000,
        "介護職": 800,
        "理学療法士": 1000,
        "作業療法士": 1000,
        "言語聴覚士": 1000,
        "臨床検査技師": 1000,
        "診療放射線技師": 1000,
        "薬剤師": 1500,
        "臨床心理士": 1000,
        "栄養士・管理栄養士": 900,
        
        // 事務・管理系
        "秘書": 900,
        "事務職（一般）": 800,
        "事務職（専門）": 1000,
        "受付": 700,
        "総務担当": 1000,
        "人事担当": 1200,
        "経理担当": 1200,
        "営業事務": 900,
        "貿易事務": 1000,
        "図書館司書": 800,
        "学芸員": 800,
        
        // 特定の状況
        "年金受給者": 500, // 年金のみの場合、通常500万円以下
        "定年退職者": 700, // 退職者でも副業や年金で一定収入あり
        "パート・アルバイト": 500,
        "主婦・主夫": 300,
        "求職中": 300,
        "就職活動中": 300,
        
        // フリーランス・自営業系
        "フリーランス": 1500, // 特定分野を除く一般的なフリーランス
        "個人事業主": 2000,
        "個人商店経営": 1500,
        "飲食店経営": 1500,
        
        // 一次産業系
        "農業従事者": 1200,
        "漁業従事者": 1200,
        "林業従事者": 1200,
        "酪農家": 1500,
        
        // サービス業系
        "ドライバー・運転手": 900,
        "タクシー運転手": 800,
        "バス運転手": 900,
        "トラック運転手": 1000,
        "配達員": 800,
        "清掃員": 700,
        "警備員": 800,
        "調理師・料理人": 1000,
        "パティシエ": 900,
        "美容師": 1000,
        "理容師": 1000,
        "エステティシャン": 900,
        "ネイリスト": 800,
        "マッサージ師": 800,
        "アロマセラピスト": 800,
        "ヨガインストラクター": 800,
        "トレーナー・インストラクター": 900,
        "ツアーガイド": 800,
        "通訳・翻訳者": 1200,
        "カウンセラー": 1000,
        "セラピスト": 1000,
        
        // 技術・製造系
        "工場勤務": 1000,
        "建設作業員": 1000,
        "大工": 1200,
        "電気工事士": 1200,
        "配管工": 1100,
        "溶接工": 1100,
        "機械オペレーター": 900,
        "製造ライン作業員": 800,
        "縫製工": 700,
        "印刷工": 800,
        "車両整備士": 1000,
        
        // クリエイティブ系
        "グラフィックデザイナー": 1200,
        "Webデザイナー": 1200,
        "イラストレーター": 1000,
        "漫画家": 1200,
        "アニメーター": 1000,
        "フォトグラファー": 1000,
        "ジャーナリスト": 1200,
        "編集者": 1200,
        "ライター": 1000,
        "記者": 1200,
        "映像制作": 1200,
        "音響エンジニア": 1100,
        "メイクアップアーティスト": 1000,
        "スタイリスト": 1000,
        "インテリアデザイナー": 1200,
        
        // IT・エンジニア系（上限が比較的高い）
        "プログラマー": 1500,
        "システムエンジニア": 1800,
        "ネットワークエンジニア": 1800,
        "データアナリスト": 1800,
        "ゲームプランナー": 1500,
        "ゲームプログラマー": 1500,
        "AIエンジニア": 2000,
        "ブロックチェーンエンジニア": 2000,
        "サーバーエンジニア": 1800,
        "クラウドエンジニア": 1800,
        "セキュリティエンジニア": 1800,
        
        // 営業・販売系
        "営業職": 1200,
        "販売員": 800,
        "小売店員": 700,
        "接客業": 700,
        "コンビニ店員": 600,
        "スーパー店員": 600,
        "百貨店員": 700,
        "アパレル販売員": 700,
        "家電販売員": 800,
        "携帯電話販売員": 900,
        "不動産営業": 1500,
        "保険営業": 1300,
        "金融商品営業": 1500,
        
        // エンターテインメント系
        "俳優・女優": 1500,
        "声優": 1200,
        "歌手": 1500,
        "ミュージシャン": 1200,
        "ダンサー": 1000,
        "モデル": 1200,
        "タレント": 1500,
        "芸人": 1200,
        "スポーツ選手": 1800,
        "スポーツトレーナー": 1200,
    };

    // Apply severe income caps for very elderly persons regardless of occupation
    // The older the person, the more restrictive the cap
    let ageCap = Infinity;
    // 60代から段階的に年収上限を下げる
    if (ageInYears >= 60 && ageInYears < 65) {
        ageCap = 3000; // 60-64歳：最大3000万円（特殊職業除く）
    } else if (ageInYears >= 65 && ageInYears < 70) {
        ageCap = 2000; // 65-69歳：最大2000万円
    } else if (ageInYears >= 70 && ageInYears < 75) {
        ageCap = 1500; // 70-74歳：最大1500万円
    } else if (ageInYears >= 75 && ageInYears < 80) {
        ageCap = 1200; // 75-79歳：最大1200万円
    } else if (ageInYears >= 80 && ageInYears < 85) {
        ageCap = 1000; // 80-84歳：最大1000万円  
    } else if (ageInYears >= 85 && ageInYears < 90) {
        ageCap = 800; // 85-89歳：最大800万円
    } else if (ageInYears >= 90 && ageInYears < 95) {
        ageCap = 600; // 90-94歳：最大600万円
    } else if (ageInYears >= 95) {
        ageCap = 400; // 95歳以上：最大400万円
    }

    // 特定のハイリスク組み合わせチェック - 78歳の秘書で5000万円以上のような状況を避ける
    const isHighRiskOccupationIncomeCombination = 
        (ageInYears >= 65 && incomeCappedProfessions[currentOccupation] && 
         incomeCappedProfessions[currentOccupation] < 1500); // 65歳以上で収入上限が1500万円未満の職業

    if (isHighRiskOccupationIncomeCombination) {
        // 年齢による追加制限
        if (ageInYears >= 75) {
            // 75歳以上の場合、職業の通常上限よりさらに厳しく制限
            ageCap = Math.min(ageCap, incomeCappedProfessions[currentOccupation] * 0.7); // 職業上限の70%に
            console.log(`75歳以上の${currentOccupation}の収入上限をさらに厳しく制限: ${ageCap}万円`);
        } else {
            // 65-74歳の場合
            ageCap = Math.min(ageCap, incomeCappedProfessions[currentOccupation] * 0.85); // 職業上限の85%に
            console.log(`65-74歳の${currentOccupation}の収入上限を制限: ${ageCap}万円`);
        }
    }

    // 職業別の特殊ケース
    if (ageInYears >= 70) {
        // 70歳以上で年金受給者・定年退職者の場合は、より厳しく制限
        if (currentOccupation === "年金受給者") {
            ageCap = Math.min(ageCap, 500); // 年金受給者は最大500万円
        } else if (currentOccupation === "定年退職者") {
            ageCap = Math.min(ageCap, 700); // 定年退職者は最大700万円
        }

        // 秘書・事務職・受付など特定職種は70歳以上では特に収入上限を低く設定
        // const lowIncomeElderlyProfessions = ["秘書", "事務職（一般）", "事務職（専門）", "受付", "販売員", "接客業"]; // Moved to function scope
        if (lowIncomeElderlyProfessions.includes(currentOccupation)) {
            ageCap = Math.min(ageCap, 700); // 70歳以上の秘書などは最大700万円
            console.log(`70歳以上の${currentOccupation}の収入上限を700万円に制限`);
        }
    }

    // 「秘書」に対する特別制限
    if (currentOccupation === "秘書") {
        // 年齢に応じて秘書の収入に制限をかける
        if (ageInYears >= 65 && ageInYears < 70) {
            ageCap = Math.min(ageCap, 800); // 65-69歳の秘書は最大800万円
        } else if (ageInYears >= 70 && ageInYears < 75) {
            ageCap = Math.min(ageCap, 700); // 70-74歳の秘書は最大700万円
        } else if (ageInYears >= 75 && ageInYears < 80) {
            ageCap = Math.min(ageCap, 600); // 75-79歳の秘書は最大600万円
        } else if (ageInYears >= 80) {
            ageCap = Math.min(ageCap, 500); // 80歳以上の秘書は最大500万円
        }
        console.log(`${ageInYears}歳の秘書の収入上限を${ageCap}万円に制限`);
    }

    let filteredHtmlIncomeValues = [...allPossibleHtmlIncomeValues];

    // Function to apply income caps and handle empty results
    function applyIncomeCap(incomeValues, cap) {
        const filtered = incomeValues.filter(incomeRange => {
            let lowerBoundOfRange = 0;
            if (incomeRange.startsWith("<")) {
                lowerBoundOfRange = 0; // effectively, so it will likely be kept unless cap is 0
            } else if (incomeRange.startsWith(">=")) {
                lowerBoundOfRange = parseInt(incomeRange.substring(2));
            } else if (incomeRange.includes("-")) {
                lowerBoundOfRange = parseInt(incomeRange.split('-')[0]);
            } else {
                try { lowerBoundOfRange = parseInt(incomeRange); } catch (e) { lowerBoundOfRange = Infinity; }
            }
            return lowerBoundOfRange < cap;
        });

        if (filtered.length === 0) { // Fallback if capping removed all options
            console.warn(`Capping removed all income options. Adding fallback options.`);
            // Try to find the highest value under the cap
            const highestPossibleUnderCap = incomeValues
                .filter(range => {
                    const lowerBound = parseInt(range.split('-')[0]?.replace('<', '') || '0');
                    return lowerBound < cap;
                })
                .sort((a,b) => {
                    const lbA = parseInt(a.split('-')[0]?.replace('<', '') || '0');
                    const lbB = parseInt(b.split('-')[0]?.replace('<', '') || '0');
                    return lbB - lbA;
                });
            
            if(highestPossibleUnderCap.length > 0) {
                return [highestPossibleUnderCap[0]];
            }
            // Ultimate fallback
            return incomeValues.includes("<100") ? ["<100"] : [incomeValues[0] || "<100"];
        }
        return filtered;
    }

    // First apply profession-specific cap
    if (incomeCappedProfessions.hasOwnProperty(currentOccupation)) {
        const profCap = incomeCappedProfessions[currentOccupation];
        console.log(`Occupation ${currentOccupation} has an income cap at lower bound ${profCap}万円.`);
        filteredHtmlIncomeValues = applyIncomeCap(filteredHtmlIncomeValues, profCap);
    }

    // Then apply age-based cap if it's more restrictive
    if (ageCap < Infinity) {
        console.log(`Age ${ageInYears} has an income cap at lower bound ${ageCap}万円.`);
        filteredHtmlIncomeValues = applyIncomeCap(filteredHtmlIncomeValues, ageCap);
    }

    // 強制的な上書き: 78歳の秘書などの極端なケースは強制的に調整
    if (ageInYears >= 75 && currentOccupation === "秘書") {
        // 75歳以上の秘書は700万円未満の範囲に強制
        const forcedMaxIncome = 700;
        // これをロガーに出力 
        console.log(`強制的な上書き: ${ageInYears}歳の${currentOccupation}の年収を${forcedMaxIncome}万円以下に制限`);
        filteredHtmlIncomeValues = applyIncomeCap(filteredHtmlIncomeValues, forcedMaxIncome);
        
        // さらに、最も低い方の年収値を優先的に選ぶ（3つの候補から2つの低い方を選択）
        if (filteredHtmlIncomeValues.length > 2) {
            filteredHtmlIncomeValues.sort((a, b) => {
                const lbA = parseInt(a.split('-')[0]?.replace('<', '') || '0');
                const lbB = parseInt(b.split('-')[0]?.replace('<', '') || '0');
                return lbA - lbB; // 昇順ソート
            });
            filteredHtmlIncomeValues = filteredHtmlIncomeValues.slice(0, 2); // 最も低い2つを選択
        }
    }

    // 高齢者（75歳以上）の学者・研究者は年収を制限
    if (ageInYears >= 75 && currentOccupation === "学者・研究者") {
        // 75歳以上の学者・研究者は800万円未満の範囲に制限
        let forcedMaxIncome = 800;
        
        // 85歳以上はさらに制限
        if (ageInYears >= 85) {
            forcedMaxIncome = 600;
        }
        
        // 95歳以上はさらに厳しく制限
        if (ageInYears >= 95) {
            forcedMaxIncome = 400;
        }
        
        console.log(`強制的な上書き: ${ageInYears}歳の${currentOccupation}の年収を${forcedMaxIncome}万円以下に制限`);
        filteredHtmlIncomeValues = applyIncomeCap(filteredHtmlIncomeValues, forcedMaxIncome);
        
        // 高齢になるほど低い収入を優先的に選ぶ
        if (filteredHtmlIncomeValues.length > 2) {
            filteredHtmlIncomeValues.sort((a, b) => {
                const lbA = parseInt(a.split('-')[0]?.replace('<', '') || '0');
                const lbB = parseInt(b.split('-')[0]?.replace('<', '') || '0');
                return lbA - lbB; // 昇順ソート
            });
            // 90歳以上なら最も低い収入を優先
            if (ageInYears >= 90) {
                filteredHtmlIncomeValues = filteredHtmlIncomeValues.slice(0, 1);
            } else {
                filteredHtmlIncomeValues = filteredHtmlIncomeValues.slice(0, 2); // それ以外は低い方から2つ
            }
        }
    }

    // 新規追加：高収入領域に対する確率重み付け
    // 2000万円以上の年収は発生確率を下げる
    function applyIncomeWeighting(incomeValues) {
        // 収入値を低・中・高の3つのグループに分類
        const lowIncomeValues = incomeValues.filter(v => {
            const lb = parseInt(v.split('-')[0]?.replace('<', '') || '0');
            return lb < 800; // 800万円未満
        });
        
        const midIncomeValues = incomeValues.filter(v => {
            const lb = parseInt(v.split('-')[0]?.replace('<', '') || '0');
            return lb >= 800 && lb < 2000; // 800万円以上2000万円未満
        });
        
        const highIncomeValues = incomeValues.filter(v => {
            const lb = parseInt(v.split('-')[0]?.replace('<', '') || '0');
            return lb >= 2000; // 2000万円以上
        });
        
        // 高収入がある場合は確率を調整
        if (highIncomeValues.length > 0) {
            // 職業に基づいて高収入の選択確率を調整
            let highIncomeChance = 0.01; // デフォルト1%に変更
            
            // 高収入が一般的な職業の場合は確率を上げる
            const highIncomeOccupations = [
                "医師", "歯科医師", "弁護士", "公認会計士", "税理士", 
                "会社経営者", "会社役員", "投資家", "不労所得者"
            ];
            
            if (highIncomeOccupations.includes(currentOccupation)) {
                highIncomeChance = 0.05; // 高収入職業でも5%に変更
            }
            
            // 運命の選択：高収入を選ぶかどうか
            const selectHighIncome = Math.random() < highIncomeChance;
            
            if (selectHighIncome && highIncomeValues.length > 0) {
                return getRandomItem(highIncomeValues);
            } else {
                // 中所得か低所得から選択
                const combinedLowMidValues = [...lowIncomeValues, ...midIncomeValues];
                if (combinedLowMidValues.length > 0) {
                    // さらに、中所得と低所得の選択にも重み付け
                    const midIncomeChance = 0.6; // 中所得を選ぶ確率60%
                    const selectMidIncome = Math.random() < midIncomeChance;
                    
                    if (selectMidIncome && midIncomeValues.length > 0) {
                        return getRandomItem(midIncomeValues);
                    } else if (lowIncomeValues.length > 0) {
                        return getRandomItem(lowIncomeValues);
                    } else {
                        return getRandomItem(midIncomeValues || combinedLowMidValues);
                    }
                } else {
                    // 万が一、中・低所得の選択肢がない場合
                    return getRandomItem(highIncomeValues);
                }
            }
        }
        
        // 高収入の選択肢がない場合は、従来通りの処理
        return null;
    }
    
    // 収入の重み付け処理を適用
    const weightedSelection = applyIncomeWeighting(filteredHtmlIncomeValues);
    if (weightedSelection) {
        console.log(`重み付けにより選択された収入: ${weightedSelection}`);
        return weightedSelection;
    }

    if (ageInYears >= 18 && ageInYears <= 19) {
        const targetIncome = "100-200";
        console.log(`Selecting '${targetIncome}' due to age 18-19 (or '<100' if not available from filtered list)`);
        return filteredHtmlIncomeValues.includes(targetIncome) ? targetIncome : (filteredHtmlIncomeValues.includes("<100") ? "<100" : filteredHtmlIncomeValues[0] || "<100");
    }
    if (ageInYears >= 20 && ageInYears <= 22) {
        const targets = ["200-300", "300-400"];
        const fallback1 = "100-200";
        const fallback2 = "<100";
        for (const target of targets) {
            if (filteredHtmlIncomeValues.includes(target)) return target;
        }
        if (filteredHtmlIncomeValues.includes(fallback1)) return fallback1;
        console.log(`Selecting '${fallback2}' as fallback for age 20-22 from filtered list`);
        return filteredHtmlIncomeValues.includes(fallback2) ? fallback2 : filteredHtmlIncomeValues[0] || "<100";
    }

    // 最終的に、フィルタされたリストからランダムに選択
    if (filteredHtmlIncomeValues.length === 0) {
        console.warn("フィルタリング後の収入オプションがありません。デフォルト値を返します。");
        return "<100"; // デフォルト値
    }

    // 特定のパターンの場合は低い収入を優先
    if ((ageInYears >= 70 && lowIncomeElderlyProfessions && lowIncomeElderlyProfessions.includes(currentOccupation)) ||
        (ageInYears >= 75)) {
        // 700万円未満のオプションを優先
        const lowerOptions = filteredHtmlIncomeValues.filter(opt => {
            const lowerBound = parseInt(opt.split('-')[0]?.replace('<', '') || '0');
            return lowerBound < 700;
        });
        
        if (lowerOptions.length > 0) {
            return getRandomItem(lowerOptions);
        }
    }

    // 通常の選択
    return getRandomItem(filteredHtmlIncomeValues);
}

/*
// This was inside DOMContentLoaded, needs to be global or passed for populateResults to use it.
// Consider moving this to a global scope or a shared utility object/module.
const patientTypeDetails = {
    '利便性重視型': { description: '...', example: '...' },
    // ... other types
};
*/ 