// 結果表示モジュール

const ResultDisplay = {
    // 結果を表示
    populateResults: function(result) {
        console.log('Received result:', result);
        
        // 基本情報
        this.displayBasicInfo(result);
        
        // AIが生成したテキスト
        this.displayGeneratedText(result);
        
        // 画像表示
        this.displayPersonaImage(result);
        
        // ダウンロードボタンの設定
        this.setupDownloadButtons(result);
    },
    
    // 基本情報を表示
    displayBasicInfo: function(result) {
        // 部門と目的
        const departmentElement = document.getElementById('result-department');
        if (departmentElement) departmentElement.textContent = result.department || '';
        
        const purposeElement = document.getElementById('result-purpose');
        if (purposeElement) purposeElement.textContent = result.purpose || '';
        
        // 基本情報の表示
        const basicInfoFields = [
            'name', 'gender', 'age', 'prefecture', 'municipality',
            'family', 'occupation', 'income', 'hobby', 'life_events',
            'patient_type', 'motto', 'concerns', 'favorite_person',
            'media_sns', 'personality_keywords', 'health_actions',
            'holiday_activities', 'catchphrase'
        ];
        
        basicInfoFields.forEach(field => {
            const element = document.getElementById(`result-${field}`);
            if (element && result[field]) {
                let displayValue = result[field];
                
                // 特殊なフォーマット処理
                if (field === 'age') {
                    displayValue = this.formatAgeDisplay(displayValue);
                } else if (field === 'income') {
                    displayValue = this.formatIncomeDisplay(displayValue);
                }
                
                element.textContent = displayValue;
            }
        });
    },
    
    // 生成されたテキストを表示
    displayGeneratedText: function(result) {
        const textFields = {
            'personality': 'result-personality',
            'reason': 'result-reason',
            'behavior': 'result-behavior',
            'reviews': 'result-reviews',
            'values': 'result-values',
            'demands': 'result-demands'
        };
        
        Object.entries(textFields).forEach(([key, elementId]) => {
            const element = document.getElementById(elementId);
            if (element && result[key]) {
                element.textContent = result[key];
            }
        });
    },
    
    // ペルソナ画像を表示
    displayPersonaImage: function(result) {
        const imageElement = document.getElementById('result-persona-image');
        const placeholderElement = document.getElementById('image-placeholder');
        const imageContainer = document.querySelector('.image-container');
        
        if (result.image_url && imageElement) {
            imageElement.src = result.image_url;
            imageElement.style.display = 'block';
            
            if (placeholderElement) {
                placeholderElement.style.display = 'none';
            }
            
            // 画像読み込みエラー処理
            imageElement.onerror = () => {
                console.error('Failed to load persona image');
                imageElement.style.display = 'none';
                if (placeholderElement) {
                    placeholderElement.style.display = 'block';
                }
            };
        } else {
            if (imageElement) imageElement.style.display = 'none';
            if (placeholderElement) placeholderElement.style.display = 'block';
        }
    },
    
    // ダウンロードボタンの設定
    setupDownloadButtons: function(result) {
        // PDFダウンロード
        const pdfButton = document.getElementById('download-pdf-btn');
        if (pdfButton) {
            pdfButton.onclick = () => this.downloadPDF(result);
        }
        
        // CSVダウンロード
        const csvButton = document.getElementById('download-csv-btn');
        if (csvButton) {
            csvButton.onclick = () => this.downloadCSV(result);
        }
    },
    
    // PDFダウンロード
    downloadPDF: async function(personaData) {
        try {
            if (window.PersonaGeneration && window.PersonaGeneration.generatePDF) {
                const blob = await window.PersonaGeneration.generatePDF(personaData);
                this.triggerDownload(blob, 'persona.pdf');
            }
        } catch (error) {
            console.error('PDF download failed:', error);
            alert('PDFのダウンロードに失敗しました。');
        }
    },
    
    // CSVダウンロード
    downloadCSV: function(personaData) {
        const csvContent = this.generateCSV(personaData);
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        this.triggerDownload(blob, 'persona.csv');
    },
    
    // CSV生成
    generateCSV: function(data) {
        const rows = [
            ['項目', '内容'],
            ['診療科', data.department || ''],
            ['目的', data.purpose || ''],
            ['名前', data.name || ''],
            ['性別', data.gender || ''],
            ['年齢', this.formatAgeDisplay(data.age || '')],
            ['都道府県', data.prefecture || ''],
            ['市区町村', data.municipality || ''],
            ['家族構成', data.family || ''],
            ['職業', data.occupation || ''],
            ['年収', this.formatIncomeDisplay(data.income || '')],
            ['趣味', data.hobby || ''],
            ['ライフイベント', data.life_events || ''],
            ['患者タイプ', data.patient_type || ''],
            ['座右の銘', data.motto || ''],
            ['最近の悩み/関心', data.concerns || ''],
            ['好きな有名人/尊敬する人物', data.favorite_person || ''],
            ['よく見るメディア/SNS', data.media_sns || ''],
            ['性格キーワード', data.personality_keywords || ''],
            ['最近した健康に関する行動', data.health_actions || ''],
            ['休日の過ごし方', data.holiday_activities || ''],
            ['キャッチコピー', data.catchphrase || ''],
            ['性格（価値観・人生観）', data.personality || ''],
            ['通院理由', data.reason || ''],
            ['症状通院頻度・行動パターン', data.behavior || ''],
            ['口コミの重視ポイント', data.reviews || ''],
            ['医療機関への価値観・行動傾向', data.values || ''],
            ['医療機関に求めるもの', data.demands || '']
        ];
        
        return rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    },
    
    // ファイルダウンロード実行
    triggerDownload: function(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },
    
    // 年齢表示フォーマット
    formatAgeDisplay: function(ageValue) {
        if (!ageValue) return '';
        
        if (ageValue.includes('y') && ageValue.includes('m')) {
            return ageValue.replace('y', '歳').replace('m', 'ヶ月');
        } else if (ageValue.includes('y')) {
            return ageValue.replace('y', '歳');
        }
        return ageValue;
    },
    
    // 収入表示フォーマット
    formatIncomeDisplay: function(incomeValue) {
        if (!incomeValue) return '';
        
        if (incomeValue.startsWith('<')) {
            return `${incomeValue.substring(1)}万円未満`;
        } else if (incomeValue.startsWith('>=')) {
            return `${incomeValue.substring(2)}万円以上`;
        } else if (incomeValue.includes('-')) {
            return `${incomeValue}万円`;
        }
        return `${incomeValue}万円`;
    }
};

// エクスポート
window.ResultDisplay = ResultDisplay;