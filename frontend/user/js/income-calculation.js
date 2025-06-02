// 収入計算モジュール

const IncomeCalculation = {
    // 収入ブラケットと重み付け
    incomeBracketsWithWeights: {
        "100万円未満": 0.15,
        "100万円以上200万円未満": 0.15,
        "200万円以上300万円未満": 0.20,
        "300万円以上400万円未満": 0.15,
        "400万円以上500万円未満": 0.10,
        "500万円以上600万円未満": 0.08,
        "600万円以上700万円未満": 0.05,
        "700万円以上800万円未満": 0.04,
        "800万円以上900万円未満": 0.03,
        "900万円以上1000万円未満": 0.02,
        "1000万円以上2000万円未満": 0.02,
        "2000万円以上": 0.01
    },
    
    // HTML収入値を重み付けブラケットにマッピング
    getWeightedBracketForIncome: function(incomeValueStr) {
        if (!incomeValueStr) return null;
        let lowerBound = 0;
        let upperBound = Infinity;
        
        // 収入文字列をパース
        if (incomeValueStr.startsWith("<")) {
            upperBound = parseInt(incomeValueStr.substring(1));
            lowerBound = 0;
        } else if (incomeValueStr.startsWith(">=")) {
            lowerBound = parseInt(incomeValueStr.substring(2));
        } else if (incomeValueStr.includes("-")) {
            const parts = incomeValueStr.split('-');
            lowerBound = parseInt(parts[0]);
            upperBound = parseInt(parts[1]);
        } else {
            try {
                const singleNum = parseInt(incomeValueStr);
                lowerBound = singleNum;
                upperBound = singleNum;
            } catch (e) {
                console.warn("Could not parse incomeValueStr:", incomeValueStr);
                return null;
            }
        }
        
        // 下限値に基づいてブラケットにマッピング
        if (upperBound <= 100 && lowerBound < 100) return "100万円未満";
        if (lowerBound >= 100 && lowerBound < 200) return "100万円以上200万円未満";
        if (lowerBound >= 200 && lowerBound < 300) return "200万円以上300万円未満";
        if (lowerBound >= 300 && lowerBound < 400) return "300万円以上400万円未満";
        if (lowerBound >= 400 && lowerBound < 500) return "400万円以上500万円未満";
        if (lowerBound >= 500 && lowerBound < 600) return "500万円以上600万円未満";
        if (lowerBound >= 600 && lowerBound < 700) return "600万円以上700万円未満";
        if (lowerBound >= 700 && lowerBound < 800) return "700万円以上800万円未満";
        if (lowerBound >= 800 && lowerBound < 900) return "800万円以上900万円未満";
        if (lowerBound >= 900 && lowerBound < 1000) return "900万円以上1000万円未満";
        if (lowerBound >= 1000 && lowerBound < 2000) return "1000万円以上2000万円未満";
        if (lowerBound >= 2000) return "2000万円以上";
        
        return null;
    },
    
    // 重み付き分布でランダム年収を取得
    getRandomAnnualIncomeWithWeights: function() {
        const brackets = Object.keys(this.incomeBracketsWithWeights);
        const weights = brackets.map(bracket => this.incomeBracketsWithWeights[bracket]);
        
        // 累積重みを計算
        const cumulativeWeights = [];
        let cumulativeSum = 0;
        for (const weight of weights) {
            cumulativeSum += weight;
            cumulativeWeights.push(cumulativeSum);
        }
        
        // ランダム値を生成
        const randomValue = Math.random() * cumulativeSum;
        
        // どのブラケットに該当するか決定
        let selectedBracket = brackets[0];
        for (let i = 0; i < cumulativeWeights.length; i++) {
            if (randomValue <= cumulativeWeights[i]) {
                selectedBracket = brackets[i];
                break;
            }
        }
        
        // 選択されたブラケットから具体的な収入値を生成
        return this.getIncomeValueFromBracket(selectedBracket);
    },
    
    // ブラケットから収入値を生成
    getIncomeValueFromBracket: function(bracket) {
        if (bracket === "100万円未満") {
            return "<100";
        } else if (bracket === "2000万円以上") {
            const highIncomes = ["2000-2100", "2100-2200", "2200-2300", "2300-2400", 
                               "2400-2500", "2500-2600", "2600-2700", "2700-2800", 
                               "2800-2900", "2900-3000", ">=3000"];
            return highIncomes[Math.floor(Math.random() * highIncomes.length)];
        } else {
            // ブラケットから範囲を抽出
            const match = bracket.match(/(\d+)万円以上(\d+)万円未満/);
            if (match) {
                const min = parseInt(match[1]);
                const max = parseInt(match[2]);
                
                // 100万円刻みで値を生成
                const step = 100;
                const numSteps = Math.floor((max - min) / step);
                const randomStep = Math.floor(Math.random() * numSteps);
                const lower = min + (randomStep * step);
                const upper = Math.min(lower + step, max);
                
                if (lower === upper || upper > max) {
                    return `${lower}`;
                } else {
                    return `${lower}-${upper}`;
                }
            }
        }
        
        return "300-400"; // デフォルト
    }
};

// エクスポート
window.IncomeCalculation = IncomeCalculation;