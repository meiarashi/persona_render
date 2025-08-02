// 競合分析機能のJavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('competitive-analysis-form');
    const analyzingScreen = document.getElementById('analyzing-screen');
    const resultScreen = document.getElementById('result-screen');
    
    // その他の診療科リスト
    const medicalDepartments = [
        '精神科', '美容外科', 'リハビリテーション科', '皮膚科（美容）',
        'ペインクリニック', '漢方内科', '在宅診療', '健診・人間ドック'
    ];
    
    // 初期化
    init();
    
    function init() {
        // 診療科チェックボックスを生成
        renderDepartmentCheckboxes();
        
        // イベントリスナーの設定
        setupEventListeners();
        
        // 郵便番号検索機能
        setupPostalCodeSearch();
    }
    
    function renderDepartmentCheckboxes() {
        const container = document.querySelector('.department-checkbox-grid');
        container.innerHTML = '';
        
        medicalDepartments.forEach(dept => {
            const div = document.createElement('div');
            div.className = 'department-checkbox';
            div.innerHTML = `
                <input type="checkbox" id="dept-${dept}" name="departments" value="${dept}">
                <label for="dept-${dept}">${dept}</label>
            `;
            container.appendChild(div);
        });
    }
    
    function setupEventListeners() {
        // 次へボタン
        document.querySelectorAll('.next-step-btn').forEach(btn => {
            btn.addEventListener('click', handleNextStep);
        });
        
        // 前へボタン
        document.querySelectorAll('.prev-step-btn').forEach(btn => {
            btn.addEventListener('click', handlePrevStep);
        });
        
        // 分析開始ボタン
        document.querySelector('.analyze-btn').addEventListener('click', handleAnalyze);
    }
    
    function handleNextStep(e) {
        const currentStep = parseInt(e.target.closest('.form-step').dataset.step);
        
        // バリデーション
        if (!validateStep(currentStep)) {
            return;
        }
        
        // 次のステップへ
        showStep(currentStep + 1);
    }
    
    function handlePrevStep(e) {
        const currentStep = parseInt(e.target.closest('.form-step').dataset.step);
        showStep(currentStep - 1);
    }
    
    function showStep(stepNumber) {
        document.querySelectorAll('.form-step').forEach(step => {
            step.classList.remove('active');
        });
        
        const targetStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (targetStep) {
            targetStep.classList.add('active');
        }
    }
    
    function validateStep(stepNumber) {
        switch(stepNumber) {
            case 1:
                // クリニック情報の検証
                const clinicName = document.getElementById('clinic-name').value.trim();
                const address = document.getElementById('address').value.trim();
                const checkedDepts = document.querySelectorAll('input[name="departments"]:checked');
                
                if (!clinicName) {
                    alert('クリニック名を入力してください。');
                    return false;
                }
                
                if (!address) {
                    alert('住所を入力してください。');
                    return false;
                }
                
                if (checkedDepts.length === 0) {
                    alert('診療科を少なくとも1つ選択してください。');
                    return false;
                }
                
                return true;
                
            case 2:
                // 分析範囲は必ず選択されているので追加検証不要
                return true;
                
            case 3:
                // 任意項目なので検証不要
                return true;
                
            default:
                return true;
        }
    }
    
    function setupPostalCodeSearch() {
        const postalSearchBtn = document.querySelector('.postal-search-btn');
        const postalCodeInput = document.getElementById('postal-code');
        const addressInput = document.getElementById('address');
        
        postalSearchBtn.addEventListener('click', async function() {
            const postalCode = postalCodeInput.value.replace(/[^0-9]/g, '');
            
            if (postalCode.length !== 7) {
                alert('郵便番号は7桁で入力してください。');
                return;
            }
            
            try {
                // 郵便番号API（実装時は実際のAPIに置き換え）
                const response = await fetch(`https://zipcloud.ibsnet.co.jp/api/search?zipcode=${postalCode}`);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    const result = data.results[0];
                    addressInput.value = `${result.address1}${result.address2}${result.address3}`;
                } else {
                    alert('該当する住所が見つかりませんでした。');
                }
            } catch (error) {
                console.error('郵便番号検索エラー:', error);
                alert('郵便番号検索中にエラーが発生しました。');
            }
        });
    }
    
    async function handleAnalyze() {
        // フォームデータを収集
        const formData = collectFormData();
        
        // バリデーション
        if (!validateStep(1)) {
            showStep(1);
            return;
        }
        
        // 分析画面を表示
        form.style.display = 'none';
        analyzingScreen.style.display = 'block';
        
        // 分析アニメーション開始
        startAnalyzingAnimation();
        
        try {
            // APIリクエスト
            const response = await fetch('/api/competitive/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('分析に失敗しました');
            }
            
            const result = await response.json();
            
            // 結果を表示
            displayResult(result);
            
        } catch (error) {
            console.error('分析エラー:', error);
            alert('分析中にエラーが発生しました。もう一度お試しください。');
            analyzingScreen.style.display = 'none';
            form.style.display = 'block';
        }
    }
    
    function collectFormData() {
        const departments = Array.from(document.querySelectorAll('input[name="departments"]:checked'))
            .map(cb => cb.value);
        
        return {
            clinicName: document.getElementById('clinic-name').value.trim(),
            postalCode: document.getElementById('postal-code').value.trim(),
            address: document.getElementById('address').value.trim(),
            departments: departments,
            analysisRange: document.querySelector('input[name="analysisRange"]:checked').value,
            clinicFeatures: document.getElementById('clinic-features').value.trim(),
            targetPatients: document.getElementById('target-patients').value.trim()
        };
    }
    
    function startAnalyzingAnimation() {
        const steps = document.querySelectorAll('.step-item');
        const progressFill = document.querySelector('.progress-fill');
        let currentStep = 0;
        
        // アニメーションループ
        const animateStep = () => {
            if (currentStep < steps.length) {
                // 現在のステップをアクティブに
                steps[currentStep].classList.add('active');
                
                // プログレスバーを更新
                const progress = ((currentStep + 1) / steps.length) * 100;
                progressFill.style.width = `${progress}%`;
                
                currentStep++;
                
                // 次のステップへ（2秒後）
                setTimeout(animateStep, 2000);
            }
        };
        
        // アニメーション開始
        setTimeout(animateStep, 500);
    }
    
    function displayResult(result) {
        // 結果画面のHTMLを生成（実装時に詳細を追加）
        resultScreen.innerHTML = `
            <h2>競合分析結果</h2>
            <div class="result-content">
                <!-- 結果の詳細表示 -->
                <p>分析結果の表示機能は現在開発中です。</p>
            </div>
        `;
        
        analyzingScreen.style.display = 'none';
        resultScreen.style.display = 'block';
    }
});