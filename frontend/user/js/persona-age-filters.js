// 年齢に基づくフィルタリング関数のモジュール

// 年齢に基づいてランダム値をフィルタリング
function filterRandomValuesForAge(valueList, ageInYears, categoryType) {
    if (!valueList || valueList.length === 0) return valueList;
    
    // 全年齢対象の項目はそのまま返す
    const filteredList = [...valueList];
    
    if (categoryType === 'media_sns') {
        // メディア/SNSの年齢フィルタリング
        if (ageInYears < 13) {
            // 13歳未満はSNS利用制限
            return ["テレビ", "YouTube（子供向けチャンネル）", "絵本", "図鑑"];
        } else if (ageInYears < 18) {
            // 18歳未満は一部制限
            return filteredList.filter(item => 
                !["出会い系アプリ", "マッチングアプリ", "婚活サイト"].includes(item)
            );
        } else if (ageInYears >= 65) {
            // 高齢者向けに調整
            return filteredList.filter(item => 
                !["TikTok", "Snapchat", "BeReal"].includes(item)
            ).concat(["新聞", "ラジオ", "NHK"]);
        }
    } 
    
    else if (categoryType === 'health_actions') {
        // 健康行動の年齢フィルタリング
        if (ageInYears < 15) {
            // 子供向け健康行動
            const childHealthActions = ["早寝早起きを心がけた", "野菜を食べるようにした", "手洗いうがいを徹底した"];
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
    
    else if (categoryType === 'concerns') {
        // 悩み・関心事の年齢フィルタリング
        if (ageInYears < 18) {
            // 未成年向け
            return filteredList.filter(item => 
                !["老後の不安", "介護", "更年期", "資産運用", "相続", "年金"].includes(item)
            );
        } else if (ageInYears >= 65) {
            // 高齢者向け
            return filteredList.filter(item => 
                !["就活", "婚活", "キャリアアップ", "転職", "育児"].includes(item)
            );
        }
    }
    
    else if (categoryType === 'motto') {
        // 座右の銘の年齢フィルタリング
        if (ageInYears < 15) {
            // 子供向け
            const childMottos = ["元気いっぱい", "友達を大切に", "毎日楽しく", "一生懸命頑張る"];
            return childMottos;
        }
    }
    
    else if (categoryType === 'favorite_person') {
        // 好きな有名人の年齢フィルタリング
        // 世代に応じて適切な有名人を選択する処理を追加可能
    }
    
    // カテゴリーに該当するフィルターがないか、フィルターの条件に当てはまらない場合は元のリストを返す
    return filteredList;
}

// エクスポート
window.PersonaAgeFilters = {
    filterRandomValuesForAge: filterRandomValuesForAge
};